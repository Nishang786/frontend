# Agricultural insights dashboard
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Agricultural Insights", page_icon="", layout="wide")
st.title("Agricultural Decision Support Dashboard")

conn = get_db_connection()
df = load_fact_table(conn)

# Calculate Agricultural Stress Index
# Formula: High stress when ET > Rain + low soil moisture + high VPD
df['water_deficit'] = df['et0_fao_evapotranspiration'] - df['rain']
df['stress_index'] = (
    (df['water_deficit'] / df['et0_fao_evapotranspiration'].max() * 0.4) +
    (df['vapor_pressure_deficit'] / df['vapor_pressure_deficit'].max() * 0.3) +
    ((30 - df['temperature_2m']).clip(lower=0) / 30 * 0.3)  # Temperature stress
)

# Daily aggregation
daily_stress = df.groupby(df['time'].dt.date).agg({
    'stress_index': 'mean',
    'rain': 'sum',
    'et0_fao_evapotranspiration': 'sum'
}).reset_index()

# Create dual-axis chart
fig = go.Figure()

# Stress index as area
fig.add_trace(go.Scatter(
    x=daily_stress['time'],
    y=daily_stress['stress_index'],
    fill='tozeroy',
    name='Agricultural Stress Index',
    fillcolor='rgba(255, 100, 100, 0.3)',
    line=dict(color='red', width=2),
    yaxis='y1'
))

# Water balance as bars
fig.add_trace(go.Bar(
    x=daily_stress['time'],
    y=daily_stress['rain'] - daily_stress['et0_fao_evapotranspiration'],
    name='Water Balance (Rain - ET)',
    marker_color=['green' if x > 0 else 'orange' for x in 
                  (daily_stress['rain'] - daily_stress['et0_fao_evapotranspiration'])],
    yaxis='y2',
    opacity=0.6
))

fig.update_layout(
    title="Agricultural Stress Index & Water Balance Analysis",
    xaxis=dict(title="Date"),
    yaxis=dict(title="Stress Index (0-1)", side='left', range=[0, 1]),
    yaxis2=dict(title="Water Balance (mm)", side='right', overlaying='y'),
    template='plotly_white',
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.success("""
- Red zones (high stress): Irrigation needed
- Green bars (positive balance): You have excess water - adjust irrigation
- Orange bars (negative balance): Water deficit - need to act
""")


st.subheader("Agricultural Water Balance Analysis")

# Weekly aggregation
df['week'] = df['time'].dt.isocalendar().week
weekly = df.groupby('week').agg({
    'rain': 'sum',
    'et0_fao_evapotranspiration': 'sum'
}).reset_index()

weekly['water_balance'] = weekly['rain'] - weekly['et0_fao_evapotranspiration']

fig1 = go.Figure()

# Water balance as bars (color-coded by surplus/deficit)
colors = ['green' if x > 0 else 'red' for x in weekly['water_balance']]
fig1.add_trace(go.Bar(
    x=weekly['week'],
    y=weekly['water_balance'],
    name='Water Balance',
    marker_color=colors,
    text=weekly['water_balance'].round(1),
    textposition='outside'
))

# Add zero line
fig1.add_hline(y=0, line_dash="dash", line_color="black", 
               annotation_text="Zero Balance")

fig1.update_layout(
    title="Weekly Water Balance: Precipitation - Evapotranspiration",
    xaxis_title="Week of Year",
    yaxis_title="Water Balance (mm)",
    template='plotly_white',
    height=500
)

st.plotly_chart(fig1, use_container_width=True)

st.success("""
- **Green bars (positive):** Water surplus - excess rainfall, no irrigation needed
- **Red bars (negative):** Water deficit - crops under stress, irrigation required
- **Critical periods:** Identify weeks needing supplemental irrigation
- **Annual pattern:** Shows seasonal water availability for crop planning
""")

# Summary statistics
surplus_weeks = (weekly['water_balance'] > 0).sum()
deficit_weeks = (weekly['water_balance'] < 0).sum()
total_deficit = weekly[weekly['water_balance'] < 0]['water_balance'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Surplus Weeks", f"{surplus_weeks}")
col2.metric("Deficit Weeks", f"{deficit_weeks}")
col3.metric("Cumulative Deficit", f"{total_deficit:.1f} mm")


# Multi-metric KPIs
st.markdown("---")
st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    avg_temp = df['temperature_2m'].mean()
    min_temp = df['temperature_2m'].min()
    max_temp = df['temperature_2m'].max()
    
    fig_kpi1 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_temp,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Average Temperature (°C)", 'font': {'size': 16}},
        delta={'reference': 15, 'suffix': "°C"},
        gauge={
            'axis': {'range': [min_temp-5, max_temp+5]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_temp-5, 10], 'color': "lightblue"},
                {'range': [10, 20], 'color': "lightyellow"},
                {'range': [20, max_temp+5], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_temp
            }
        }
    ))
    fig_kpi1.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_kpi1, use_container_width=True)

with col2:
    total_rain = df['rain'].sum()
    
    fig_kpi2 = go.Figure(go.Indicator(
        mode="number+delta",
        value=total_rain,
        title={'text': "Total Rainfall (mm)", 'font': {'size': 16}},
        delta={'reference': 800, 'suffix': " mm", 'relative': True},
        number={'suffix': " mm", 'font': {'size': 40}}
    ))
    fig_kpi2.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_kpi2, use_container_width=True)

with col3:
    avg_wind = df['wind_speed_10m'].mean()
    max_wind = df['wind_speed_10m'].max()
    
    fig_kpi3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_wind,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Avg Wind Speed (m/s)", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, max_wind+2]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 5], 'color': "lightgreen"},
                {'range': [5, 10], 'color': "yellow"},
                {'range': [10, max_wind+2], 'color': "red"}
            ]
        }
    ))
    fig_kpi3.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_kpi3, use_container_width=True)


st.markdown("---")
st.caption("Key metrics showing overall weather conditions and trends.")