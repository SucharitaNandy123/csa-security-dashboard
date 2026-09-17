# test_pdf_reader.py

import io
import pypdf
import re
from google.cloud import bigquery, storage
from config.settings import BIGQUERY_TABLE_ID

def download_pdf_from_gcs(url: str) -> bytes:
    """Downloads PDF bytes securely using google-cloud-storage SDK."""
    if not url:
        raise ValueError("URL is empty or invalid.")
    
    print(f"[*] Parsing GCS URL: {url}")
    
    # Strip any prefix (https://storage.cloud.google.com/, https://storage.googleapis.com/, gs://)
    clean_url = re.sub(r"^https?://(storage\.cloud\.google\.com|storage\.googleapis\.com)/", "", url)
    clean_url = re.sub(r"^gs://", "", clean_url)
    
    parts = clean_url.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Could not parse bucket and blob from URL: {url}")
        
    bucket_name, blob_name = parts[0], parts[1]
    print(f"[*] Bucket: '{bucket_name}' | Blob: '{blob_name}'")
    
    # Download using GCP client authentication
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    print(f"[*] Downloading blob from GCS...")
    content = blob.download_as_bytes()
    
    if not content.startswith(b"%PDF"):
        html_preview = content[:200].decode("utf-8", errors="ignore")
        raise ValueError(f"Downloaded object is not a valid PDF binary:\n{html_preview}")
        
    return content

def read_pdf_text(pdf_bytes: bytes, max_chars: int = 15000) -> str:
    """Extracts text page by page using pypdf."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    print(f"[*] Total PDF Pages: {len(reader.pages)}")
    
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(f"--- PAGE {i+1} ---\n{text.strip()}")
            
    full_text = "\n\n".join(pages_text)
    return full_text[:max_chars]

def run_test():
    client = bigquery.Client()
    
    print("[*] Querying BigQuery for an available report...")
    query = f"""
        SELECT Tenant_Name, Report_Period, Report_URL 
        FROM `{BIGQUERY_TABLE_ID}` 
        WHERE Report_URL IS NOT NULL 
        LIMIT 1
    """
    df = client.query(query).to_dataframe()
    
    if df.empty:
        print("[!] No reports found in BigQuery table.")
        return
        
    tenant = df.iloc[0]["Tenant_Name"]
    period = df.iloc[0]["Report_Period"]
    url = df.iloc[0]["Report_URL"]
    
    print(f"[+] Found Report | Tenant: {tenant} | Period: {period}")
    
    # Download authenticated PDF bytes
    pdf_bytes = download_pdf_from_gcs(url)
    print(f"[+] Successfully downloaded PDF ({len(pdf_bytes)} bytes)")
    
    # Extract text
    print("[*] Extracting raw text via pypdf...\n")
    raw_text = read_pdf_text(pdf_bytes)
    
    print("=" * 60)
    print("RAW EXTRACTED PDF OUTPUT:")
    print("=" * 60)
    print(raw_text)
    print("=" * 60)

if __name__ == "__main__":
    run_test()