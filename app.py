# app.py

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from backend.bigquery_service import fetch_tenant_names, fetch_report_periods
from backend.backend_builder import run_csa_pipeline

# Page Setup
st.set_page_config(
    page_title="Skyhigh Security - Cloud Security Intelligence", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Dark Theme with White Text & Traffic-Light Trigger Colors
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Global Typography - Enforce White Text */
    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #F8FAFC !important;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94A3B8 !important;
        margin-bottom: 20px;
    }
    
    /* Traffic Light / Trigger Point Indicators */
    .status-red {
        background-color: #7F1D1D;
        color: #FECACA !important;
        border-left: 5px solid #EF4444;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .status-yellow {
        background-color: #78350F;
        color: #FEF08A !important;
        border-left: 5px solid #F59E0B;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .status-green {
        background-color: #064E3B;
        color: #A7F3D0 !important;
        border-left: 5px solid #10B981;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    /* Metric Card Customization */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 700;
    }
    
    /* Activity Log Styling */
    .log-box {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8rem;
        background-color: #020617;
        color: #38BDF8 !important;
        padding: 12px;
        border-radius: 6px;
        max-height: 220px;
        overflow-y: auto;
        border: 1px solid #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Logo & Controls
# ---------------------------------------------------------
# Correct relative path targeting frontend/assets/skyhigh_logo.png
LOGO_PATH = os.path.join("frontend", "assets", "skyhigh_logo.png")

if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    # Backup check for root directory
    ROOT_LOGO = "skyhigh_logo.png"
    if os.path.exists(ROOT_LOGO):
        st.sidebar.image(ROOT_LOGO, use_container_width=True)
    else:
        st.sidebar.title("🛡️ Skyhigh Security")

st.sidebar.header("📋 Controls & Filtering")

# Initialize Execution Log History
if "execution_logs" not in st.session_state:
    st.session_state.execution_logs = []

def add_log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.execution_logs.append(f"[{timestamp}] {msg}")

# Fetch Tenant Names
try:
    tenant_names = fetch_tenant_names()
except Exception as e:
    st.sidebar.error(f"Error connecting to BigQuery: {str(e)}")
    tenant_names = []

selected_tenant = st.sidebar.selectbox("Select Enterprise Tenant", options=tenant_names)

report_periods = []
if selected_tenant:
    try:
        report_periods = fetch_report_periods(selected_tenant)
    except Exception as e:
        st.sidebar.error(f"Error fetching report periods: {str(e)}")

selected_period = st.sidebar.selectbox("Select Current Report Period", options=report_periods)

# Trigger Button
run_pipeline_btn = st.sidebar.button("🚀 Generate Intelligence Report", use_container_width=True)

# Sidebar Activity Log Console
st.sidebar.divider()
st.sidebar.subheader("📟 Activity & Execution Log")
log_container = st.sidebar.empty()

def render_logs():
    if st.session_state.execution_logs:
        log_text = "\n".join(st.session_state.execution_logs)
        log_container.markdown(f"<div class='log-box'>{log_text}</div>", unsafe_allow_html=True)
    else:
        log_container.info("Ready to execute pipeline.")

render_logs()

# Header Section
st.markdown("<div class='main-title'>Cloud Security Intelligence Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Visual Analytics, Threshold Monitoring & Period-over-Period Trend Analysis</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Execution Pipeline Trigger
# ---------------------------------------------------------
if run_pipeline_btn:
    if not selected_tenant or not selected_period:
        st.warning("Please select both a Tenant Name and a Report Period.")
    else:
        st.session_state.execution_logs = []
        add_log("Initializing Skyhigh Pipeline...")
        render_logs()
        
        with st.spinner("Fetching GCS PDF & executing Gemini Analytics..."):
            try:
                data = run_csa_pipeline(
                    selected_tenant, 
                    selected_period, 
                    logger_callback=lambda msg: (add_log(msg), render_logs())
                )
                st.session_state.pipeline_data = data
                add_log("Pipeline completed successfully!")
                render_logs()
                st.success("Executive Analytics & Visualizations Ready!")
            except Exception as e:
                add_log(f"ERROR: {str(e)}")
                render_logs()
                st.error(f"Error processing security intelligence pipeline: {str(e)}")

# ---------------------------------------------------------
# Main Dashboard Content & Visualizations
# ---------------------------------------------------------
if "pipeline_data" in st.session_state:
    data = st.session_state.pipeline_data
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Maturity Score & Posture", 
        "2. Usage & Threat Summary", 
        "3. Executive Insights",
        "4. 🔄 Period-over-Period Comparison"
    ])
    
    # ==========================================
    # TAB 1: MATURITY SCORE & POSTURE
    # ==========================================
    with tab1:
        st.header("1. Maturity Score & Governance")
        maturity = data.get("maturity_score", {})
        
        c1, c2, c3 = st.columns(3)
        score = maturity.get("score", 0)
        
        # Color trigger for maturity score
        if score >= 75:
            score_class = "status-green"
        elif score >= 50:
            score_class = "status-yellow"
        else:
            score_class = "status-red"
            
        c1.markdown(f"<div class='{score_class}'><h4>1.1 Your Score</h4><h2>{score} / 100</h2></div>", unsafe_allow_html=True)
        c1.progress(min(max(score / 100, 0.0), 1.0))
        
        vis = maturity.get("visibility_metrics", {})
        vis_pct = vis.get('coverage_pct', 0)
        c2.metric("1.2 Visibility Coverage", f"{vis_pct}%")
        c2.progress(min(max(vis_pct / 100, 0.0), 1.0))
        c2.caption(vis.get("insights", ""))
        
        ctrl = maturity.get("control_metrics", {})
        ctrl_pct = ctrl.get('enforcement_pct', 0)
        c3.metric("1.3 Control Enforcement", f"{ctrl_pct}%")
        c3.progress(min(max(ctrl_pct / 100, 0.0), 1.0))
        c3.caption(ctrl.get("insights", ""))
        
        st.divider()
        st.subheader("📊 Governance & Posture Gauge Breakdown")
        df_posture = pd.DataFrame({
            "Governance Area": ["Maturity Score", "Visibility Coverage", "Control Enforcement"],
            "Percentage Score": [score, vis_pct, ctrl_pct]
        })
        st.bar_chart(df_posture.set_index("Governance Area"))

    # ==========================================
    # TAB 2: USAGE & THREAT SUMMARY
    # ==========================================
    with tab2:
        st.header("2. Usage & Risk Visual Analytics")
        usage = data.get("usage_summary", {})
        
        # Row 1: Footprint & Resources
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("2.1 Cloud Footprint")
            fp = usage.get("cloud_footprint", {})
            st.metric("Active Cloud Apps", fp.get('active_cloud_apps', 0))
            st.markdown(f"<div class='status-yellow'>⚠️ <b>High Risk Apps:</b> {fp.get('high_risk_apps', 0)}</div>", unsafe_allow_html=True)
            st.info(fp.get("insights", ""))
            
        with col2:
            st.subheader("2.2 Resources")
            res = usage.get("resources", {})
            st.metric("Total Resources", res.get('total_resources', 0))
            st.markdown(f"<div class='status-red'>🔴 <b>Publicly Exposed:</b> {res.get('publicly_exposed_resources', 0)}</div>", unsafe_allow_html=True)
            st.info(res.get("insights", ""))
        
        st.divider()
        
        # Row 2: Incidents, Threats & Malware Charts
        st.subheader("2.3 - 2.5 Security Events Breakdown")
        inc = usage.get("incidents", {})
        thr = usage.get("threats", {})
        mal = usage.get("malware", {})
        
        c_inc, c_thr, c_mal = st.columns(3)
        c_inc.markdown(f"<div class='status-red'>🚨 <b>Critical Incidents:</b> {inc.get('critical_incidents', 0)} / {inc.get('total_incidents', 0)}</div>", unsafe_allow_html=True)
        c_thr.markdown(f"<div class='status-yellow'>⚠️ <b>Total Threats:</b> {thr.get('total_threats', 0)} ({thr.get('top_threat_type', 'N/A')})</div>", unsafe_allow_html=True)
        c_mal.markdown(f"<div class='status-red'>🦠 <b>Malware Instances:</b> {mal.get('malware_count', 0)}</div>", unsafe_allow_html=True)
        
        df_events = pd.DataFrame({
            "Event Type": ["Total Incidents", "Critical Incidents", "Total Threats", "Malware Count"],
            "Count": [
                inc.get('total_incidents', 0), 
                inc.get('critical_incidents', 0), 
                thr.get('total_threats', 0), 
                mal.get('malware_count', 0)
            ]
        })
        st.bar_chart(df_events.set_index("Event Type"))
            
        st.divider()
        
        # Row 3: Sensitive Data Distribution
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.subheader("2.6 Data At Risk")
            dar = usage.get("data_at_risk", {})
            st.markdown(f"<div class='status-red'>🔓 <b>Exposed Sensitive Files:</b> {dar.get('exposed_sensitive_files_pct', 0)}%</div>", unsafe_allow_html=True)
            st.info(dar.get("insights", ""))
            
        with col_d2:
            st.subheader("2.7 Sensitive Data Distribution")
            sdd = usage.get("sensitive_data_distribution", [])
            if sdd:
                df_sdd = pd.DataFrame(sdd)
                st.bar_chart(df_sdd.set_index("category"))
            else:
                st.write("No distribution data available.")
        
        st.divider()
        
        # Row 4: Users, Mobile, Apps & MITRE
        r4_1, r4_2, r4_3, r4_4 = st.columns(4)
        with r4_1:
            st.subheader("2.8 Users")
            usr = usage.get("users", {})
            st.metric("Total Users", usr.get("total_users", 0))
            st.markdown(f"<div class='status-red'>High Risk: {usr.get('high_risk_users', 0)}</div>", unsafe_allow_html=True)
            
        with r4_2:
            st.subheader("2.9 Mobile")
            mob = usage.get("mobile_devices", {})
            st.metric("Total Devices", mob.get("total_devices", 0))
            st.markdown(f"<div class='status-yellow'>Unmanaged: {mob.get('unmanaged_devices', 0)}</div>", unsafe_allow_html=True)
            
        with r4_3:
            st.subheader("2.10 Apps")
            apps = usage.get("connected_apps", {})
            st.metric("Connected Apps", apps.get("third_party_apps", 0))
            st.markdown(f"<div class='status-yellow'>OAuth Risks: {apps.get('high_risk_oauth_apps', 0)}</div>", unsafe_allow_html=True)
            
        with r4_4:
            st.subheader("2.11 MITRE ATT&CK")
            mit = usage.get("mitre_attck", {})
            st.markdown(f"<div class='status-green'>Tactics: {mit.get('primary_tactics', 'N/A')}</div>", unsafe_allow_html=True)

    # ==========================================
    # TAB 3: EXECUTIVE TAKEAWAYS
    # ==========================================
    with tab3:
        st.header("Executive Summary & Recommendations")
        takeaways = data.get("executive_takeaways", [])
        
        # Custom CSS for dark-themed recommendation cards matching the home background
        st.markdown("""
        <style>
            .insight-card {
                background-color: #020617;
                border: 1px solid #1E293B;
                border-left: 4px solid #38BDF8;
                border-radius: 8px;
                padding: 16px 20px;
                margin-bottom: 12px;
                color: #F8FAFC !important;
                font-size: 0.98rem;
                line-height: 1.5;
            }
            .insight-card b {
                color: #38BDF8 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        for idx, item in enumerate(takeaways, 1):
            st.markdown(
                f"<div class='insight-card'><b>{idx}.</b> {item}</div>", 
                unsafe_allow_html=True
            )
    # ==========================================
    # TAB 4: PERIOD-OVER-PERIOD COMPARISON
    # ==========================================
    with tab4:
        st.header("🔄 Period-over-Period Visual Comparison")
        comp = data.get("comparison_data")
        
        if not comp:
            st.warning("No prior baseline period report was found in BigQuery to compare against.")
        else:
            prev_label = data.get("previous_period_label", "Previous Period")
            st.subheader(f"Baseline ({prev_label}) vs Current ({selected_period})")
            
            st.info(comp.get("comparative_executive_summary", "No comparison summary generated."))
            
            st.divider()
            
            # Metrics Comparison Visual Graph
            metrics_list = comp.get("metrics_comparison", [])
            if metrics_list:
                df_comp = pd.DataFrame(metrics_list)
                st.subheader("📊 Metric Shifts Comparison Chart")
                
                # Chart comparing Previous vs Current values side-by-side
                chart_data = df_comp.set_index("metric")[["previous", "current"]]
                st.bar_chart(chart_data)
                
                # Structured Table
                st.dataframe(df_comp, use_container_width=True)
            
            st.divider()
            
            # Trigger Point Cards for Shifts
            col_inc, col_dec = st.columns(2)
            with col_inc:
                st.subheader("🔴 Areas Increasing / Degraded")
                inclines = comp.get("key_inclines", [])
                for inc_item in inclines:
                    st.markdown(f"<div class='status-red'><b>{inc_item.get('area', 'Metric')}:</b> {inc_item.get('detail', '')}</div>", unsafe_allow_html=True)
                    
            with col_dec:
                st.subheader("🟢 Areas Decreasing / Improved")
                declines = comp.get("key_declines", [])
                for dec_item in declines:
                    st.markdown(f"<div class='status-green'><b>{dec_item.get('area', 'Metric')}:</b> {dec_item.get('detail', '')}</div>", unsafe_allow_html=True)