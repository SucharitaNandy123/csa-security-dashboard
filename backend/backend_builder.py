# backend/backend_builder.py

import io
import pypdf
import re
from google.cloud import bigquery, storage
from config.settings import BIGQUERY_TABLE_ID, GEMINI_MODEL_ID
from config.prompts import SECURITY_REPORT_ANALYTICS_PROMPT, COMPARATIVE_ANALYSIS_PROMPT
from backend.data_processor import parse_and_validate_gemini_response

_bq_client = None
_storage_client = None

def get_bq_client():
    global _bq_client
    if _bq_client is None:
        _bq_client = bigquery.Client()
    return _bq_client

def get_storage_client():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client

def download_pdf_from_gcs(url: str) -> bytes:
    """Downloads PDF bytes securely using GCS SDK."""
    if not url:
        return None
    
    clean_url = re.sub(r"^https?://(storage\.cloud\.google\.com|storage\.googleapis\.com)/", "", url)
    clean_url = re.sub(r"^gs://", "", clean_url)
    
    parts = clean_url.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Could not parse bucket and blob from URL: {url}")
        
    bucket_name, blob_name = parts[0], parts[1]
    
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    content = blob.download_as_bytes()
    if not content.startswith(b"%PDF"):
        raise ValueError("Downloaded object is not a valid PDF binary.")
        
    return content

def read_pdf_text(pdf_bytes: bytes, max_chars: int = 25000) -> str:
    """Extracts raw text page by page using pypdf."""
    if not pdf_bytes:
        return "N/A - No document available."
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(f"--- PAGE {i+1} ---\n{text.strip()}")
            
    full_text = "\n\n".join(pages_text)
    return full_text[:max_chars] if full_text else "No extractable text found in PDF."

def analyze_text_via_bigquery_ml(prompt_text: str) -> str:
    """Sends extracted text prompt to Gemini 2.5 Flash via BigQuery ML."""
    bq_client = get_bq_client()
    
    query = f"""
        SELECT JSON_VALUE(ml_generate_text_result, '$.candidates[0].content.parts[0].text') AS response_text
        FROM ML.GENERATE_TEXT(
            MODEL `{GEMINI_MODEL_ID}`,
            (SELECT @prompt AS prompt),
            STRUCT(0.0 AS temperature)
        )
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("prompt", "STRING", prompt_text)]
    )
    
    df = bq_client.query(query, job_config=job_config, timeout=180).to_dataframe()
    if not df.empty and df.iloc[0]["response_text"] is not None:
        return df.iloc[0]["response_text"]
    raise ValueError("Empty response returned from Gemini via BigQuery ML.")

def run_csa_pipeline(tenant_name: str, selected_period: str, logger_callback=None) -> dict:
    """Pipeline: Fetch Current & Previous URLs -> GCS Downloads -> pypdf Text Extract -> Gemini Analysis."""
    
    def log(msg):
        if logger_callback:
            logger_callback(msg)

    bq_client = get_bq_client()
    
    log(f"Querying BigQuery metadata for tenant: {tenant_name} ({selected_period})...")
    
    # Query current and preceding period reports
    query = f"""
        WITH SelectedReport AS (
            SELECT Report_Date 
            FROM `{BIGQUERY_TABLE_ID}`
            WHERE Tenant_Name = @tenant_name AND Report_Period = @selected_period
            LIMIT 1
        )
        SELECT Tenant_Name, Report_Period, Report_Date, Report_URL
        FROM `{BIGQUERY_TABLE_ID}`
        WHERE Tenant_Name = @tenant_name
          AND Report_Date <= (SELECT Report_Date FROM SelectedReport)
        ORDER BY Report_Date DESC
        LIMIT 2
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("tenant_name", "STRING", tenant_name),
            bigquery.ScalarQueryParameter("selected_period", "STRING", selected_period)
        ]
    )
    df = bq_client.query(query, job_config=job_config, timeout=60).to_dataframe()
    
    if df.empty or not df.iloc[0]["Report_URL"]:
        raise ValueError(f"No valid Report_URL found for '{tenant_name}' during '{selected_period}'.")
    
    current_meta = df.iloc[0].to_dict()
    previous_meta = df.iloc[1].to_dict() if len(df) >= 2 else None
    
    log(f"Current Report Period: {current_meta['Report_Period']}")
    if previous_meta:
        log(f"Preceding Report Period found: {previous_meta['Report_Period']}")
    else:
        log("No prior baseline period found. Running current period single analysis.")

    # 1. Download Current PDF
    log("Downloading Current PDF binary from private GCS bucket...")
    current_pdf_bytes = download_pdf_from_gcs(current_meta["Report_URL"])
    
    # 2. Download Previous PDF if present
    previous_pdf_bytes = None
    if previous_meta and previous_meta.get("Report_URL"):
        log("Downloading Preceding Period PDF binary from GCS...")
        previous_pdf_bytes = download_pdf_from_gcs(previous_meta["Report_URL"])

    # 3. Extract text
    log("Parsing Current PDF text via pypdf...")
    current_text = read_pdf_text(current_pdf_bytes)
    
    previous_text = "N/A"
    if previous_pdf_bytes:
        log("Parsing Preceding Period PDF text via pypdf...")
        previous_text = read_pdf_text(previous_pdf_bytes)

    # 4. Generate Current Period Analytics
    log("Sending Current Period prompt to Gemini via BigQuery ML...")
    current_prompt = f"{SECURITY_REPORT_ANALYTICS_PROMPT}\n\n--- SECURITY REPORT TEXT ---\n{current_text}"
    raw_current_json = analyze_text_via_bigquery_ml(current_prompt)
    data = parse_and_validate_gemini_response(raw_current_json)

    # 5. Generate Comparison Data if previous period exists
    data["comparison_data"] = None
    if previous_pdf_bytes:
        log("Generating Period-over-Period comparative analysis prompt...")
        comp_prompt = f"{COMPARATIVE_ANALYSIS_PROMPT}\n\n--- DOCUMENT 1 (PREVIOUS) ---\n{previous_text}\n\n--- DOCUMENT 2 (CURRENT) ---\n{current_text}"
        raw_comp_json = analyze_text_via_bigquery_ml(comp_prompt)
        data["comparison_data"] = parse_and_validate_gemini_response(raw_comp_json)
        data["previous_period_label"] = previous_meta["Report_Period"]
    
    log("Processing and rendering dashboard visualizations...")
    return data