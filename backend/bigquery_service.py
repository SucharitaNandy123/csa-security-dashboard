# backend/bigquery_service.py

import re
from google.cloud import bigquery, storage
from config.settings import BIGQUERY_TABLE_ID

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

def fetch_tenant_names():
    client = get_bq_client()
    query = f"""
        SELECT DISTINCT Tenant_Name 
        FROM `{BIGQUERY_TABLE_ID}` 
        WHERE Tenant_Name IS NOT NULL
        ORDER BY Tenant_Name ASC
    """
    df = client.query(query, timeout=60).to_dataframe()
    return df["Tenant_Name"].tolist()

def fetch_report_periods(tenant_name: str):
    client = get_bq_client()
    query = f"""
        SELECT Report_Period
        FROM `{BIGQUERY_TABLE_ID}`
        WHERE Tenant_Name = @tenant_name
        ORDER BY Report_Date DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("tenant_name", "STRING", tenant_name)]
    )
    df = client.query(query, job_config=job_config, timeout=60).to_dataframe()
    return df["Report_Period"].tolist()

def download_pdf_from_gcs(url: str) -> bytes:
    """Working GCS download logic from test_pdf_reader.py"""
    if not url:
        raise ValueError("URL is empty or invalid.")
    
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
        html_preview = content[:200].decode("utf-8", errors="ignore")
        raise ValueError(f"Downloaded object is not a valid PDF binary:\n{html_preview}")
        
    return content