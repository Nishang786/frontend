import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import ssl

# MongoDB connection with caching
# Try to get from Streamlit secrets (cloud), fallback to .env (local)
try:
    MONGO_URL = st.secrets["MONGO_URL"]
except (FileNotFoundError, KeyError):
    MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://etl_user:7oy3cvMr5Ue0PkKf@cluster0.bgj5m0x.mongodb.net/?appName=Cluster0")

@st.cache_resource
def get_db_connection():
    """Create cached MongoDB connection with proper error handling"""
    try:
        client = MongoClient(
            MONGO_URL,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000
        )
        # Test connection
        client.admin.command('ping')
        st.success("✅ Connected to MongoDB")
        return client
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {str(e)}")
        st.info("**Troubleshooting:**\n- Check MongoDB Atlas IP whitelist includes 0.0.0.0/0\n- Verify MONGO_URL in secrets is correct")
        st.stop()

# Data loading with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_table(_conn, table_name):
    """Load collection from MongoDB with caching"""
    db = _conn['weather_analytics']  # Database name from your ETL code
    collection = db[table_name]

    
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's internal _id field
    df = pd.DataFrame(data)
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
    return df

@st.cache_data(ttl=600)
def load_fact_table(_conn):
    """Load unified fact collection from MongoDB"""
    df = load_table(_conn, 'fact_weather')
    
    # Check if time column exists, if not show available columns
    if 'time' not in df.columns:
        st.error(f"'time' column not found in database. Available columns: {list(df.columns)}")
        st.stop()
    
    # Ensure time column is datetime (MongoDB may store as ISO string)
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    
    # Add derived columns from time if they don't exist
    if 'month_name' not in df.columns:
        df['month_name'] = df['time'].dt.strftime('%B')
    if 'hour' not in df.columns:
        df['hour'] = df['time'].dt.hour
    if 'day_of_week' not in df.columns:
        df['day_of_week'] = df['time'].dt.day_name()
    if 'is_weekend' not in df.columns:
        df['is_weekend'] = df['time'].dt.dayofweek.isin([5, 6]).astype(int)
    
    return df

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
