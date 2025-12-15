import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import *
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main {background-color: #f5f7fa;}
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {color: #1f77b4;}
    .sidebar .sidebar-content {background-color: #f0f2f6;}
</style>
""", unsafe_allow_html=True)

# Header
st.title("Weather Analytics Dashboard")
st.markdown("### Meteorological Data Analysis")
st.markdown("---")

# Initialize connection
try:
    conn = get_db_connection()
    df = load_fact_table(conn)
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
st.sidebar.markdown("---")


# Month filter
months = st.sidebar.multiselect(
    "Select Months",
    options=df['month_name'].unique().tolist(),
    default=df['month_name'].unique().tolist()
)

# Hour range filter
hour_range = st.sidebar.slider(
    "Select Hour Range",
    min_value=0,
    max_value=23,
    value=(0, 23),
    step=1
)

# Weekend filter
weekend_filter = st.sidebar.radio(
    "Day Type",
    options=["All Days", "Weekdays Only", "Weekends Only"],
    index=0
)

# Apply filters
filtered_df = df.copy()



# Month filter
filtered_df = filtered_df[filtered_df['month_name'].isin(months)]

# Hour filter
filtered_df = filtered_df[
    (filtered_df['hour'] >= hour_range[0]) &
    (filtered_df['hour'] <= hour_range[1])
]

# Weekend filter
if weekend_filter == "Weekdays Only":
    filtered_df = filtered_df[filtered_df['is_weekend'] == 0]
elif weekend_filter == "Weekends Only":
    filtered_df = filtered_df[filtered_df['is_weekend'] == 1]

st.sidebar.markdown(f"**Filtered Records: {len(filtered_df):,}**")

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'temperature_2m' in filtered_df.columns:
        avg_temp = filtered_df['temperature_2m'].mean()
        st.metric(
            label="Avg Temperature",
            value=f"{avg_temp:.1f}°C",
            delta=f"{avg_temp - df['temperature_2m'].mean():.1f}°C"
        )

with col2:
    if 'rain' in filtered_df.columns:
        avg_rain = filtered_df['rain'].mean()
        st.metric(
            label="Avg Rainfall",
            value=f"{avg_rain:.1f} mm",
            delta=f"{avg_rain - df['rain'].mean():.1f} mm"
        )

with col3:
    if 'wind_speed_10m' in filtered_df.columns:
        avg_wind = filtered_df['wind_speed_10m'].mean()
        st.metric(
            label="Avg Wind Speed",
            value=f"{avg_wind:.1f} m/s",
            delta=f"{avg_wind - df['wind_speed_10m'].mean():.1f} m/s"
        )

with col4:
    if 'shortwave_radiation' in filtered_df.columns:
        avg_radiation = filtered_df['shortwave_radiation'].mean()
        st.metric(
            label="Avg Solar Radiation",
            value=f"{avg_radiation:.0f} W/m²",
            delta=f"{avg_radiation - df['shortwave_radiation'].mean():.0f} W/m²"
        )

st.markdown("---")

# Quick Overview Chart - Temperature Trend
st.subheader("Temperature Trend Overview")

fig_temp = go.Figure()

if 'temperature_2m' in filtered_df.columns:
    fig_temp.add_trace(go.Scatter(
        x=filtered_df['time'],
        y=filtered_df['temperature_2m'],
        mode='lines',
        name='Land Temperature',
        line=dict(color=COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))

# Add marine temperature if available
if 'temperature_2m_marine' in filtered_df.columns:
    fig_temp.add_trace(go.Scatter(
        x=filtered_df['time'],
        y=filtered_df['temperature_2m_marine'],
        mode='lines',
        name='Marine Temperature',
        line=dict(color=COLORS['secondary'], width=2, dash='dash')
    ))

fig_temp = apply_custom_theme(fig_temp, "Temperature Over Time (Land vs Marine)")
fig_temp.update_layout(
    height=600,
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
fig_temp.update_xaxes(title="Date/Time")
fig_temp.update_yaxes(title="Temperature (°C)")

st.plotly_chart(fig_temp, use_container_width=True, config={'responsive': True})

# Data summary table
st.subheader("Data Summary Statistics")

# Select only columns that exist in the dataframe
summary_cols = [
    'temperature_2m', 'rain', 'wind_speed_10m', 
    'shortwave_radiation', 'pressure_msl', 'et0_fao_evapotranspiration'
]
summary_cols = [col for col in summary_cols if col in filtered_df.columns]

if summary_cols:
    summary_stats = filtered_df[summary_cols].describe()
    st.dataframe(
        summary_stats.style.highlight_max(axis=0, color='lightgreen')
                          .highlight_min(axis=0, color='lightcoral')
                          .format("{:.2f}"),
        use_container_width=True
    )
else:
    st.warning("No summary statistics available for the selected columns.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Data Source: Open-Meteo API | Storage: MongoDB Atlas | ETL: Dagster | Visualization: Plotly</p>
</div>
""", unsafe_allow_html=True)
