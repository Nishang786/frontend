import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Wind & Marine", page_icon="", layout="wide")

st.title("Wind & Marine Conditions")
st.markdown("### Atmospheric Data Analysis")
st.markdown("---")

# Load data
conn = get_db_connection()
df = load_fact_table(conn)

# Visual 6: Wind Speed Profile
st.subheader("Vertical Wind Profile (10m vs 100m)")

# Sample data for performance (every 12 hours)
sampled_df = df.iloc[::12].copy()

fig6 = go.Figure()

fig6.add_trace(go.Scatter(
    x=sampled_df['time'],
    y=sampled_df['wind_speed_10m'],
    mode='lines',
    name='Wind Speed @ 10m',
    line=dict(color='#1f77b4', width=2)
))

fig6.add_trace(go.Scatter(
    x=sampled_df['time'],
    y=sampled_df['wind_speed_100m'],
    mode='lines',
    name='Wind Speed @ 100m',
    line=dict(color='#ff7f0e', width=2)
))

fig6 = apply_custom_theme(fig6, "Wind Speed Comparison: Surface vs Upper Atmosphere")
fig6.update_xaxes(title="Date/Time")
fig6.update_yaxes(title="Wind Speed (m/s)")

st.plotly_chart(fig6, use_container_width=True)

st.success("Wind speed increases with altitude - important for wind energy and marine operations.")

# Visual 7: Wind Direction Distribution
st.markdown("---")
st.subheader("Dominant Wind Direction Patterns")

# Bin wind directions into 8 cardinal directions
def bin_direction(angle):
    if pd.isna(angle):
        return 'Unknown'
    bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    idx = int((angle + 22.5) // 45) % 8
    return bins[idx]

df['wind_dir_cardinal'] = df['wind_direction_100m'].apply(bin_direction)
direction_counts = df['wind_dir_cardinal'].value_counts()

fig7 = go.Figure(data=[go.Pie(
    labels=direction_counts.index,
    values=direction_counts.values,
    hole=0.4,
    marker=dict(colors=px.colors.qualitative.Set3),
    textinfo='label+percent',
    textfont_size=14
)])

fig7.update_layout(
    title="Wind Direction Distribution (100m Altitude)",
    annotations=[dict(text='Wind<br>Direction', x=0.5, y=0.5, font_size=16, showarrow=False)],
    template='plotly_white',
    height=500
)

st.plotly_chart(fig7, use_container_width=True)

st.info("Prevailing wind patterns show direction distribution - useful for site selection and planning.")

#  Wind Rose Diagram
st.markdown("---")
st.subheader("Wind Rose Diagram")

# Create bins for wind speed
df['wind_speed_bin'] = pd.cut(df['wind_speed_100m'], 
                                bins=[0, 5, 10, 15, 20, 100],
                                labels=['0-5 m/s', '5-10 m/s', '10-15 m/s', '15-20 m/s', '>20 m/s'])

wind_rose_data = df.groupby(['wind_dir_cardinal', 'wind_speed_bin']).size().reset_index(name='count')

fig_rose = go.Figure()

# Define color mapping for wind speed bins
speed_colors = {
    '0-5 m/s': "#faf4f4",
    '5-10 m/s': '#2ca02c',
    '10-15 m/s': '#ff7f0e',
    '15-20 m/s': '#d62728',
    '>20 m/s': "#6798bd"
}

for speed_bin in ['0-5 m/s', '5-10 m/s', '10-15 m/s', '15-20 m/s', '>20 m/s']:
    data = wind_rose_data[wind_rose_data['wind_speed_bin'] == speed_bin]
    fig_rose.add_trace(go.Barpolar(
        r=data['count'],
        theta=data['wind_dir_cardinal'].map({
            'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
            'S': 180, 'SW': 225, 'W': 270, 'NW': 315
        }),
        name=speed_bin,
        marker_color=speed_colors[speed_bin]
    ))

fig_rose.update_layout(
    title="Wind Rose: Direction × Speed Distribution",
    polar=dict(
        radialaxis=dict(showticklabels=True, ticks=''),
        angularaxis=dict(
            direction='clockwise',
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
            ticktext=['N (0°)', 'NE (45°)', 'E (90°)', 'SE (135°)', 'S (180°)', 'SW (225°)', 'W (270°)', 'NW (315°)']
        )
    ),
    template='plotly_white',
    height=600
)

st.plotly_chart(fig_rose, use_container_width=True)

st.caption("Wind rose shows direction and speed distribution - useful for renewable energy assessment.")

st.subheader("Atmospheric Pressure: MSL vs Surface")

df['pressure_diff'] = df['pressure_msl'] - df['surface_pressure']

# Daily aggregation
daily_pressure = df.groupby(df['time'].dt.date).agg({
    'pressure_msl': 'mean',
    'surface_pressure': 'mean',
    'pressure_diff': 'mean',
    'temperature_2m': 'mean'
}).reset_index()

fig5 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    subplot_titles=('Pressure Levels', 'Pressure Difference (Station Correction)'),
    vertical_spacing=0.1,
    row_heights=[0.6, 0.4]
)

# Top panel: Both pressures
fig5.add_trace(
    go.Scatter(x=daily_pressure['time'], y=daily_pressure['pressure_msl'],
               name='MSL Pressure', line=dict(color='blue', width=2)),
    row=1, col=1
)

fig5.add_trace(
    go.Scatter(x=daily_pressure['time'], y=daily_pressure['surface_pressure'],
               name='Surface Pressure', line=dict(color='red', width=2)),
    row=1, col=1
)

# Bottom panel: Difference
fig5.add_trace(
    go.Scatter(x=daily_pressure['time'], y=daily_pressure['pressure_diff'],
               name='Pressure Difference', line=dict(color='purple', width=2),
               fill='tozeroy', fillcolor='rgba(128,0,128,0.2)'),
    row=2, col=1
)

fig5.update_xaxes(title_text="Date", row=2, col=1)
fig5.update_yaxes(title_text="Pressure (hPa)", row=1, col=1)
fig5.update_yaxes(title_text="Diff (hPa)", row=2, col=1)

fig5.update_layout(
    height=700,
    title_text="Mean Sea Level vs Surface Pressure Analysis",
    template='plotly_white',
    showlegend=True
)

st.plotly_chart(fig5, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Mean MSL Pressure", f"{df['pressure_msl'].mean():.1f} hPa")
col2.metric("Mean Surface Pressure", f"{df['surface_pressure'].mean():.1f} hPa")
col3.metric("Mean Difference", f"{df['pressure_diff'].mean():.2f} hPa")


