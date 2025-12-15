# pages/6_🗺️_Interactive_Map.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Dublin Weather Map", page_icon="", layout="wide")

st.title(" Dublin Weather Map - Hourly Evolution")
st.markdown("---")

# Load data
conn = get_db_connection()
df = load_fact_table(conn)

DUBLIN_LAT = 53.34
DUBLIN_LON = -6.26

# ========================
# DATE SELECTOR
# ========================
selected_date = st.date_input(
    "Select Date",
    value=df['time'].min().date(),
    min_value=df['time'].min().date(),
    max_value=df['time'].max().date()
)

# Filter data for selected date
date_data = df[df['time'].dt.date == selected_date].copy()
date_data = date_data.sort_values('time').reset_index(drop=True)

if len(date_data) == 0:
    st.error("No data available for selected date")
    st.stop()

# ========================
# HOUR SLIDER
# ========================
st.markdown("###  Select Hour")
selected_hour = st.slider(
    "Hour of the day",
    min_value=0,
    max_value=23,
    value=12,
    format="%02d:00"
)

current_data = date_data[date_data['hour'] == selected_hour].iloc[0]

st.markdown("---")

# ========================
# WEATHER MAP
# ========================
st.subheader(f"Weather at {selected_hour:02d}:00")

# Get weather data
temp = current_data['temperature_2m']
rain = current_data['rain']
solar = current_data['shortwave_radiation']
clouds = current_data['cloud_cover']
wind = current_data['wind_speed_10m']
wind_dir = current_data['wind_direction_100m']

# Create map with weather layers
fig_map = go.Figure()

# Layer 1: Base circle (temperature background)
temp_color = 'red' if temp > 20 else 'orange' if temp > 15 else 'yellow' if temp > 10 else 'lightblue'
fig_map.add_trace(go.Scattermapbox(
    lat=[DUBLIN_LAT],
    lon=[DUBLIN_LON],
    mode='markers',
    marker=dict(
        size=120,
        color=temp_color,
        opacity=0.3
    ),
    name='Temperature',
    hoverinfo='skip',
    showlegend=False
))

# Layer 2: Sun intensity (if sunny)
if solar > 100:
    sun_size = 60 + (solar / 10)
    fig_map.add_trace(go.Scattermapbox(
        lat=[DUBLIN_LAT],
        lon=[DUBLIN_LON],
        mode='markers+text',
        marker=dict(
            size=sun_size,
            color='gold',
            opacity=0.6
        ),
        text=['☀️'],
        textfont=dict(size=40, color='orange'),
        textposition="middle center",
        name=f'Solar: {solar:.0f} W/m²',
        hovertemplate=f'<b>Solar Radiation</b><br>{solar:.0f} W/m²<extra></extra>'
    ))

# Layer 3: Clouds (if cloudy)
if clouds > 30:
    cloud_size = 50 + (clouds / 2)
    fig_map.add_trace(go.Scattermapbox(
        lat=[DUBLIN_LAT],
        lon=[DUBLIN_LON],
        mode='markers+text',
        marker=dict(
            size=cloud_size,
            color='lightgray',
            opacity=0.5
        ),
        text=['☁️'],
        textfont=dict(size=35, color='gray'),
        textposition="middle center",
        name=f'Clouds: {clouds:.0f}%',
        hovertemplate=f'<b>Cloud Cover</b><br>{clouds:.0f}%<extra></extra>'
    ))

# Layer 4: Rain (if raining)
if rain > 0.1:
    rain_size = 40 + (rain * 20)
    rain_opacity = min(0.7, 0.3 + rain * 0.1)
    fig_map.add_trace(go.Scattermapbox(
        lat=[DUBLIN_LAT],
        lon=[DUBLIN_LON],
        mode='markers+text',
        marker=dict(
            size=rain_size,
            color='blue',
            opacity=rain_opacity
        ),
        text=['🌧️'],
        textfont=dict(size=30, color='darkblue'),
        textposition="middle center",
        name=f'Rain: {rain:.2f} mm/h',
        hovertemplate=f'<b>Precipitation</b><br>{rain:.2f} mm/h<extra></extra>'
    ))

# Layer 5: Wind direction indicator
if wind > 1:
    # Calculate wind arrow endpoint
    wind_length = 0.02 * (wind / 5)  # Scale based on wind speed
    wind_rad = np.radians(wind_dir)
    
    end_lat = DUBLIN_LAT + wind_length * np.cos(wind_rad)
    end_lon = DUBLIN_LON + wind_length * np.sin(wind_rad)
    
    # Add wind arrow
    fig_map.add_trace(go.Scattermapbox(
        lat=[DUBLIN_LAT, end_lat],
        lon=[DUBLIN_LON, end_lon],
        mode='lines+markers',
        line=dict(width=4, color='purple'),
        marker=dict(size=[10, 15], color='purple', symbol=['circle', 'triangle']),
        name=f'Wind: {wind:.1f} m/s',
        hovertemplate=f'<b>Wind</b><br>Speed: {wind:.1f} m/s<br>Direction: {wind_dir}°<extra></extra>'
    ))

# Center point with main weather icon
if rain > 5:
    main_icon = '🌧️'
    main_color = 'blue'
elif rain > 1:
    main_icon = '🌦️'
    main_color = 'lightblue'
elif clouds > 75:
    main_icon = '☁️'
    main_color = 'gray'
elif solar > 400:
    main_icon = '☀️'
    main_color = 'gold'
elif solar > 200:
    main_icon = '🌤️'
    main_color = 'yellow'
else:
    main_icon = '🌥️'
    main_color = 'lightgray'

fig_map.add_trace(go.Scattermapbox(
    lat=[DUBLIN_LAT],
    lon=[DUBLIN_LON],
    mode='markers+text',
    marker=dict(
        size=50,
        color=main_color,
        opacity=0.8
    ),
    text=[main_icon],
    textfont=dict(size=30),
    textposition="middle center",
    name='Dublin',
    hovertemplate=(
        f'<b>Dublin</b><br>' +
        f'Time: {selected_hour:02d}:00<br>' +
        f'Temperature: {temp:.1f}°C<br>' +
        f'Rain: {rain:.2f} mm/h<br>' +
        f'Solar: {solar:.0f} W/m²<br>' +
        f'Clouds: {clouds:.0f}%<br>' +
        f'Wind: {wind:.1f} m/s<br>' +
        '<extra></extra>'
    )
))

# Configure map
fig_map.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=DUBLIN_LAT, lon=DUBLIN_LON),
        zoom=11
    ),
    height=600,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=True,
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="gray",
        borderwidth=1
    )
)

st.plotly_chart(fig_map, use_container_width=True)

# ========================
# INSTANTANEOUS METRICS CHART
# ========================
st.markdown("---")
st.subheader(f" All Weather Metrics at {selected_hour:02d}:00")

# Create single combined chart
fig_metrics = go.Figure()

# Prepare data
metrics = {
    'Temperature': {'value': temp, 'unit': '°C', 'color': 'red'},
    'Solar Radiation': {'value': solar / 10, 'unit': 'W/m² (×10)', 'color': 'orange'},
    'Cloud Cover': {'value': clouds, 'unit': '%', 'color': 'gray'},
    'Precipitation': {'value': rain * 10, 'unit': 'mm/h (×10)', 'color': 'blue'},
    'Wind Speed': {'value': wind, 'unit': 'm/s', 'color': 'purple'},
    'Pressure': {'value': (current_data['pressure_msl'] - 1000), 'unit': 'hPa - 1000', 'color': 'green'}
}

categories = list(metrics.keys())
values = [metrics[k]['value'] for k in categories]
colors = [metrics[k]['color'] for k in categories]

# Create bar chart
fig_metrics.add_trace(go.Bar(
    x=categories,
    y=values,
    marker_color=colors,
    text=[f"{v:.1f}" for v in values],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
))

fig_metrics.update_layout(
    title=f"Instantaneous Weather Conditions - {selected_date} at {selected_hour:02d}:00",
    xaxis_title="Weather Parameter",
    yaxis_title="Normalized Value",
    template='plotly_white',
    height=400,
    showlegend=False
)

st.plotly_chart(fig_metrics, use_container_width=True)

# Add metric cards below
st.markdown("###Detailed Readings")
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Temperature", f"{temp:.1f}°C")
col2.metric("Solar", f"{solar:.0f} W/m²")
col3.metric("Clouds", f"{clouds:.0f}%")
col4.metric("Rain", f"{rain:.2f} mm/h")
col5.metric("Wind", f"{wind:.1f} m/s")
col6.metric("Pressure", f"{current_data['pressure_msl']:.1f} hPa")

# Add explanation
st.markdown("---")
st.info("""
**Map Legend:**
- **Yellow/Gold Glow:** Solar radiation intensity
- **Gray Cloud:** Cloud cover percentage
- **Blue Raindrops:** Precipitation intensity
- **Purple Arrow:** Wind direction and speed
- **Background Color:** Temperature (red=hot, blue=cold)
- **Center Icon:** Overall weather condition
""")

# Add daily comparison
st.markdown("---")
st.subheader("Comparison with Daily Average")

daily_avg = {
    'Temperature': date_data['temperature_2m'].mean(),
    'Solar': date_data['shortwave_radiation'].mean(),
    'Clouds': date_data['cloud_cover'].mean(),
    'Rain': date_data['rain'].mean(),
    'Wind': date_data['wind_speed_10m'].mean(),
    'Pressure': date_data['pressure_msl'].mean()
}

comparison_data = {
    'Parameter': list(daily_avg.keys()),
    'Current Hour': [
        temp,
        solar,
        clouds,
        rain,
        wind,
        current_data['pressure_msl']
    ],
    'Daily Average': list(daily_avg.values())
}

comparison_df = pd.DataFrame(comparison_data)

fig_compare = go.Figure()

fig_compare.add_trace(go.Bar(
    name='Current Hour',
    x=comparison_df['Parameter'],
    y=comparison_df['Current Hour'],
    marker_color='steelblue',
    text=comparison_df['Current Hour'].round(1),
    textposition='outside'
))

fig_compare.add_trace(go.Bar(
    name='Daily Average',
    x=comparison_df['Parameter'],
    y=comparison_df['Daily Average'],
    marker_color='lightcoral',
    text=comparison_df['Daily Average'].round(1),
    textposition='outside'
))

fig_compare.update_layout(
    barmode='group',
    title="Current Hour vs Daily Average",
    xaxis_title="Weather Parameter",
    yaxis_title="Value",
    template='plotly_white',
    height=400
)

st.plotly_chart(fig_compare, use_container_width=True)
