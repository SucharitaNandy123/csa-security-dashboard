# config/prompts.py

SECURITY_REPORT_ANALYTICS_PROMPT = """
You are an Enterprise Cloud Security Architect. Analyze the provided report text and extract data, insights, and key takeaways for the standard report structure below.

CRITICAL FORMAT INSTRUCTIONS:
1. Return ONLY raw, valid JSON. Do NOT use markdown code blocks (```json).
2. Extract numerical metrics accurately. If a metric/section is not explicitly present in the text, use 0 for numbers and "No data available in report" for text.

Return JSON strictly matching this schema:
{
  "maturity_score": {
    "score": 0,
    "max_score": 100,
    "visibility_metrics": {
      "coverage_pct": 0,
      "insights": "Key findings regarding visibility."
    },
    "control_metrics": {
      "enforcement_pct": 0,
      "insights": "Key findings regarding control enforcement."
    }
  },
  "usage_summary": {
    "cloud_footprint": {
      "active_cloud_apps": 0,
      "high_risk_apps": 0,
      "insights": "Summary of app footprint and risk."
    },
    "resources": {
      "total_resources": 0,
      "publicly_exposed_resources": 0,
      "insights": "Summary of cloud resource exposure."
    },
    "incidents": {
      "total_incidents": 0,
      "critical_incidents": 0,
      "insights": "Incident trends and highlights."
    },
    "threats": {
      "total_threats": 0,
      "top_threat_type": "string",
      "insights": "Threat landscape overview."
    },
    "malware": {
      "malware_count": 0,
      "affected_files": 0,
      "insights": "Malware activity summary."
    },
    "data_at_risk": {
      "exposed_sensitive_files_pct": 0,
      "insights": "Data exposure and DLP highlights."
    },
    "sensitive_data_distribution": [
      {"category": "PII", "percentage": 0},
      {"category": "PCI/Financial", "percentage": 0},
      {"category": "Credentials/Secrets", "percentage": 0},
      {"category": "IP/Proprietary", "percentage": 0}
    ],
    "users": {
      "total_users": 0,
      "high_risk_users": 0,
      "insights": "User risk and behavior summary."
    },
    "mobile_devices": {
      "total_devices": 0,
      "unmanaged_devices": 0,
      "insights": "Mobile endpoint posture."
    },
    "connected_apps": {
      "third_party_apps": 0,
      "high_risk_oauth_apps": 0,
      "insights": "Third-party ecosystem exposure."
    },
    "mitre_attck": {
      "primary_tactics": "string",
      "insights": "MITRE ATT&CK mapping and technique highlights."
    }
  },
  "executive_takeaways": [
    "string"
  ]
}
"""

COMPARATIVE_ANALYSIS_PROMPT = """
You are an Enterprise Cloud Security Analyst.

Document 1 is the PREVIOUS period security report text.
Document 2 is the CURRENT period security report text.

Compare Document 2 against Document 1 to extract current metrics AND calculate period-over-period shifts.

CRITICAL INSTRUCTION: Return ONLY raw, valid JSON. Do NOT wrap in markdown code blocks.

Return JSON strictly matching this schema:
{
  "comparison_period_label": "string (e.g., Previous Period vs Current Period)",
  "metrics_comparison": [
    {"metric": "Maturity Score", "previous": 0, "current": 0, "change_pct": 0, "status": "Improved/Degraded/Unchanged"},
    {"metric": "Total Incidents", "previous": 0, "current": 0, "change_pct": 0, "status": "Improved/Degraded/Unchanged"},
    {"metric": "Critical Incidents", "previous": 0, "current": 0, "change_pct": 0, "status": "Improved/Degraded/Unchanged"},
    {"metric": "High Risk Apps", "previous": 0, "current": 0, "change_pct": 0, "status": "Improved/Degraded/Unchanged"},
    {"metric": "Exposed Sensitive Files Pct", "previous": 0, "current": 0, "change_pct": 0, "status": "Improved/Degraded/Unchanged"}
  ],
  "key_inclines": [
    {"area": "string", "detail": "Detailed explanation of security metrics that increased or worsened."}
  ],
  "key_declines": [
    {"area": "string", "detail": "Detailed explanation of threats/incidents that decreased or improved."}
  ],
  "comparative_executive_summary": "High-level summary comparing posture trends across both periods."
}
"""