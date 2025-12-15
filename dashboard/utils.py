import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Database connection with caching
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "etl_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "StrongPass123!")
PG_DB   = os.getenv("PG_DB", "weather_demo")
@st.cache_resource
def get_db_connection():
    """Create cached db connection"""
    url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    return create_engine(url)

# Data loading with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_table(_conn, table_name):
    """Load table from database with caching"""
    query = f'SELECT * FROM {table_name}'
    df = pd.read_sql(query, _conn)
    df['time'] = pd.to_datetime(df['time'])
    return df

@st.cache_data(ttl=600)
def load_fact_table(_conn):
    """Load unified fact table"""
    return load_table(_conn, 'fact_weather')

# Custom Plotly theme
def apply_custom_theme(fig, title=""):
    """Apply professional styling to Plotly figures"""
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#1f77b4', family='Arial Black')),
        template='plotly_white',
        hovermode='x unified',
        font=dict(family='Arial', size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )
    return fig

# Color schemes
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd',
    'gradient': ['#0d47a1', '#1976d2', '#42a5f5', '#90caf9']
}
