# csa-security-dashboard
# 🛡️ CSA Cloud Security Intelligence Dashboard

An enterprise-grade security intelligence pipeline that automatically retrieves security report PDFs from Google Cloud Storage (GCS) based on BigQuery metadata, extracts text in-memory using `pypdf`, and generates structured business insights, KPI metrics, threshold alerts, and period-over-period trend analysis using Gemini via BigQuery ML.

---

## 🏗️ Architecture & Pipeline Flow

+-------------------+      +-----------------------+      +-----------------------+
|  BigQuery Table   | ---> |  GCS Private Bucket   | ---> |   In-Memory Parsing   |
| (Metadata & URLs) |      | (Authenticated SDK)   |      |       (pypdf)         |
+-------------------+      +-----------------------+      +-----------------------+
|
v
+-------------------+      +-----------------------+      +-----------------------+
| Streamlit UI      | <--- | JSON Schema Validator | <--- | Gemini 2.5 Flash      |
| (Analytics & Logs)|      | (data_processor.py)   |      | (BigQuery ML Remote)  |
+-------------------+      +-----------------------+      +-----------------------+


### End-to-End Pipeline Execution Steps:
1. **Metadata Lookup:** Streamlit queries BigQuery to fetch available enterprise tenants and report periods.
2. **Authenticated Fetch:** The system parses GCS blob URLs (`gs://` or `https://storage.cloud.google.com/`) and securely downloads raw PDF bytes using the `google-cloud-storage` SDK, bypassing standard HTTP 403 access restrictions.
3. **In-Memory Extraction:** `pypdf` parses raw text from PDF binary buffers page-by-page without saving local file copies.
4. **AI Inference:** Extracted report text is injected into engineered prompt schemas and processed by Gemini 2.5 Flash using BigQuery ML remote model execution (`ML.GENERATE_TEXT`).
5. **Comparative Analytics:** If an immediately preceding report period exists in BigQuery, the pipeline automatically executes a secondary comparative analysis query to calculate metric shifts and posture deltas.
6. **Structured Rendering:** Raw JSON output is validated, parsed, and rendered into interactive Streamlit visual components, progress bars, threshold cards, and side-by-side comparison charts.

---

## 📁 Project Structure

CSA/
│
├── backend/
│   ├── init.py
│   ├── backend_builder.py    # Main pipeline runner (GCS fetch + Gemini execution)
│   ├── bigquery_service.py   # BigQuery connection & GCS download client
│   ├── data_processor.py     # JSON response cleaning & schema validation
│   └── gemini_service.py     # PDF text extraction utilities
│
├── config/
│   ├── init.py
│   ├── prompts.py            # Structured Gemini analytics & comparative prompts
│   └── settings.py           # BigQuery table IDs & GCP model parameters
│
├── frontend/
│   └── assets/
│       └── skyhigh_logo.png  # Enterprise branding logo
│
├── .env                      # GCP Environment configurations (Git ignored)
├── .gitignore                # Excluded build/cache/secret files
├── app.py                    # Streamlit UI dashboard layer
├── requirements.txt          # Python dependency list
├── test_pdf_reader.py        # Independent pipeline verification script
└── README.md                 # Project documentation


---

## ⚙️ End-to-End Installation & Setup Guide

### 1. Prerequisites
* **Python 3.10 or higher** installed ([Download Python](https://www.python.org/downloads/))
* **Google Cloud SDK (`gcloud`)** installed and authenticated ([Install gcloud CLI](https://cloud.google.com/sdk/docs/install))
* Access to GCP project containing BigQuery metadata and GCS private storage buckets

---

### 2. Google Cloud Authentication Setup

Before running the application, authenticate your local terminal with Google Cloud Application Default Credentials (ADC):

```bash
gcloud auth login
gcloud auth application-default login
Set your active GCP project ID:

Bash
gcloud config set project YOUR_GCP_PROJECT_ID
3. Virtual Environment (venv) Creation & Activation
Setting up a virtual environment isolates project dependencies and prevents conflicts with system-level Python packages.

On Windows (PowerShell):
PowerShell
# 1. Navigate to project root directory
cd C:\Users\SucharitaNandy\Desktop\CSA

# 2. Create the virtual environment named 'venv'
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1
Note: If you encounter a PowerShell Execution_Policies script restriction error, run:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process and retry activating.

On macOS / Linux:
Bash
# 1. Navigate to project root directory
cd /path/to/CSA

# 2. Create the virtual environment named 'venv'
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate
(You will know activation succeeded when (venv) appears at the start of your terminal prompt).

4. Install Dependencies
With the virtual environment activated ((venv) active), upgrade pip and install all required packages:

Bash
python -m pip install --upgrade pip
pip install -r requirements.txt
Core Packages Included in requirements.txt:
streamlit — Interactive frontend dashboard interface

google-cloud-bigquery — GCP BigQuery client & BQML text generation

google-cloud-storage — Authenticated binary GCS PDF extraction

pypdf — Fast in-memory PDF text extraction

pandas — Tabular data processing & Streamlit chart rendering

db-dtypes — Data type support for BigQuery to pandas DataFrames

5. Configuration Settings
Verify config/settings.py points to your correct BigQuery table ID and Gemini ML remote model:

Python
# config/settings.py

BIGQUERY_TABLE_ID = "your-gcp-project.your_dataset.your_metadata_table"
GEMINI_MODEL_ID = "your-gcp-project.your_dataset.gemini_2_5_flash_model"
🚀 Running the Dashboard
1. Launch Streamlit UI
Ensure your virtual environment is active, then run:

Bash
streamlit run app.py
The application will open automatically in your browser at http://localhost:8501.

2. Verify Pipeline Standalone (Optional)
To test BigQuery queries, GCS binary downloading, and pypdf extraction without starting the frontend dashboard, run:

Bash
python test_pdf_reader.py
📊 Key Features & Visualizations
Slide-Wise Sections: Standardized analysis covering Maturity Scores, Visibility Coverage, Control Metrics, Cloud Footprint, Incidents, Threats, Data at Risk, Users, Apps, and MITRE ATT&CK mappings.

Traffic-Light Threshold Alerts: Color-coded visual cards highlighting critical incidents (🔴 Red), high-risk OAuth apps (🟡 Yellow), and healthy governance metrics (🟢 Green).

Period-over-Period Trend Analysis: Automated comparative view illustrating metric shifts against historical report periods.

Live Activity Console: Real-time log console integrated into the sidebar for transparent operational debugging.
