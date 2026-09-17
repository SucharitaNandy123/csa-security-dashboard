# backend/chart_service.py

import pandas as pd
import plotly.express as px

def create_threat_distribution_chart(threat_data: list):
    """Generates Plotly donut chart for threat category distribution."""
    df = pd.DataFrame(threat_data)
    if df.empty:
        return None
    fig = px.pie(
        df, 
        names="category", 
        values="count", 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    return fig

def create_risky_entities_chart(entity_data: list):
    """Generates Plotly bar chart for top risky users/applications."""
    df = pd.DataFrame(entity_data)
    if df.empty:
        return None
    fig = px.bar(
        df,
        x="entity_name",
        y="incident_count",
        color="risk_level",
        labels={"entity_name": "Entity / Application", "incident_count": "Incidents"},
        color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    return fig