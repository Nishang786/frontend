import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Solar Analytics", page_icon="", layout="wide")

st.title("Solar & Radiation Analytics")
st.markdown("### Solar Energy Potential Analysis")
st.markdown("---")

# Load data
conn = get_db_connection()
df = load_fact_table(conn)

# Solar Radiation Components
st.subheader("Solar Radiation Components Over Time")

# Daily aggregation
daily_solar = df.groupby(df['time'].dt.date).agg({
    'shortwave_radiation': 'mean',
    'direct_radiation': 'mean',
    'diffuse_radiation': 'mean'
}).reset_index()
daily_solar.columns = ['date', 'shortwave', 'direct', 'diffuse']

fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=daily_solar['date'],
    y=daily_solar['shortwave'],
    mode='lines',
    name='Shortwave Radiation',
    line=dict(color='#ff7f0e', width=3),
    stackgroup='one'
))

fig4.add_trace(go.Scatter(
    x=daily_solar['date'],
    y=daily_solar['direct'],
    mode='lines',
    name='Direct Radiation',
    line=dict(color='#d62728', width=2)
))

fig4.add_trace(go.Scatter(
    x=daily_solar['date'],
    y=daily_solar['diffuse'],
    mode='lines',
    name='Diffuse Radiation',
    line=dict(color='#9467bd', width=2)
))

fig4 = apply_custom_theme(fig4, "Solar Radiation Components - Daily Average")
fig4.update_xaxes(title="Date")
fig4.update_yaxes(title="Radiation (W/m²)")

st.plotly_chart(fig4, use_container_width=True)

st.success("High solar energy potential shows up in summer months when direct radiation peaks.")

# Cloud Cover vs Radiation
st.markdown("---")
st.subheader("Cloud Cover Impact on Solar Radiation")

monthly_cloud = df.groupby('month_name').agg({
    'cloud_cover': 'mean',
    'shortwave_radiation': 'mean'
}).reset_index()

# Order months correctly
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_cloud['month_name'] = pd.Categorical(monthly_cloud['month_name'], 
                                               categories=month_order, 
                                               ordered=True)
monthly_cloud = monthly_cloud.sort_values('month_name')

# Normalize for comparison
monthly_cloud['radiation_pct'] = (monthly_cloud['shortwave_radiation'] / 
                                   monthly_cloud['shortwave_radiation'].max()) * 100

fig5 = go.Figure()

fig5.add_trace(go.Bar(
    x=monthly_cloud['month_name'],
    y=monthly_cloud['cloud_cover'],
    name='Cloud Cover (%)',
    marker_color='rgba(100, 100, 100, 0.6)'
))

fig5.add_trace(go.Bar(
    x=monthly_cloud['month_name'],
    y=monthly_cloud['radiation_pct'],
    name='Solar Radiation (% of Max)',
    marker_color='rgba(255, 165, 0, 0.8)'
))

fig5.update_layout(
    title="Monthly Cloud Cover vs Solar Radiation",
    xaxis_title="Month",
    yaxis_title="Percentage",
    barmode='group',
    template='plotly_white',
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig5, use_container_width=True)

st.info("More clouds mean less solar radiation - they're inversely related.")

# Bonus: Radiation Heatmap by Hour and Month
st.markdown("---")
st.subheader("Bonus: Solar Radiation Heatmap (Hour × Month)")

heatmap_data = df.groupby(['month_name', 'hour'])['shortwave_radiation'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='hour', columns='month_name', values='shortwave_radiation')
heatmap_pivot = heatmap_pivot[month_order]  # Reorder columns

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='YlOrRd',
    colorbar=dict(title="W/m²")
))

fig_heat.update_layout(
    title="Average Solar Radiation by Hour and Month",
    xaxis_title="Month",
    yaxis_title="Hour of Day",
    template='plotly_white',
    height=500
)

st.plotly_chart(fig_heat, use_container_width=True)

st.warning("Peak solar radiation happens around midday during summer - between 11 AM and 2 PM in June through August.")

st.subheader("Solar Radiation Components Analysis")

# Monthly aggregation
monthly = df.groupby('month_name').agg({
    'shortwave_radiation': 'mean',
    'direct_radiation': 'mean',
    'diffuse_radiation': 'mean'
}).reindex([
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
])

# Calculate percentages
monthly['direct_pct'] = (monthly['direct_radiation'] / monthly['shortwave_radiation'] * 100)
monthly['diffuse_pct'] = (monthly['diffuse_radiation'] / monthly['shortwave_radiation'] * 100)

fig2 = go.Figure()

# Stacked area chart
fig2.add_trace(go.Scatter(
    x=monthly.index,
    y=monthly['direct_radiation'],
    mode='lines',
    name='Direct Radiation',
    line=dict(width=0.5, color='gold'),
    stackgroup='one',
    fillcolor='gold'
))

fig2.add_trace(go.Scatter(
    x=monthly.index,
    y=monthly['diffuse_radiation'],
    mode='lines',
    name='Diffuse Radiation',
    line=dict(width=0.5, color='lightblue'),
    stackgroup='one',
    fillcolor='lightblue'
))

fig2.update_layout(
    title="Solar Radiation Components: Direct vs Diffuse (Stacked)",
    xaxis_title="Month",
    yaxis_title="Solar Radiation (W/m²)",
    template='plotly_white',
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# Show percentages
st.subheader("☀️ Direct vs Diffuse Radiation Ratio")
col1, col2 = st.columns(2)

summer_direct = monthly.loc[['June', 'July', 'August'], 'direct_pct'].mean()
winter_direct = monthly.loc[['December', 'January', 'February'], 'direct_pct'].mean()

col1.metric("Summer Direct %", f"{summer_direct:.1f}%", 
            delta=f"+{summer_direct - winter_direct:.1f}% vs winter")
col2.metric("Winter Direct %", f"{winter_direct:.1f}%",
            delta=f"{winter_direct - summer_direct:.1f}% vs summer",
            delta_color="inverse")

st.info("""
- **Summer:** High direct radiation (clear skies) → optimal for concentrated solar power (CSP)
- **Winter:** High diffuse radiation (clouds) → better for photovoltaic panels (PV)
- **System selection:** Ireland's cloudy climate favors PV over CSP
- **Tracking value:** Solar tracking systems add less value when diffuse dominates
""")
