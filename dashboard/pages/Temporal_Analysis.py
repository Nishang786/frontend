import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Temporal Analysis", page_icon="", layout="wide")

st.title("Time Specific & Behavioral Analysis")
st.markdown("---")

# Load data
conn = get_db_connection()
df = load_fact_table(conn)

# Weekday vs Weekend
st.subheader("Weekday vs Weekend Weather Patterns")

weekend_compare = df.groupby('is_weekend').agg({
    'temperature_2m': 'mean',
    'rain': 'mean',
    'wind_speed_10m': 'mean'
}).reset_index()

weekend_compare['day_type'] = weekend_compare['is_weekend'].map({0: 'Weekday', 1: 'Weekend'})

fig8 = go.Figure()

metrics = ['temperature_2m', 'rain', 'wind_speed_10m']
metric_labels = ['Avg Temperature (°C)', 'Avg Rain (mm)', 'Avg Wind Speed (m/s)']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors)):
    fig8.add_trace(go.Bar(
        x=weekend_compare['day_type'],
        y=weekend_compare[metric],
        name=label,
        marker_color=color,
        text=weekend_compare[metric].round(2),
        textposition='auto'
    ))

fig8.update_layout(
    title="Weekday vs Weekend: Weather Comparison",
    xaxis_title="Day Type",
    yaxis_title="Value",
    barmode='group',
    template='plotly_white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig8, use_container_width=True)

st.info("Check if weather patterns change between weekdays and weekends.")

# Temperature patterns by hour and month
st.markdown("---")
st.subheader("Temperature Heatmap (Hour × Month)")

month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

heatmap_data = df.groupby(['month_name', 'hour'])['temperature_2m'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='hour', columns='month_name', values='temperature_2m')
heatmap_pivot = heatmap_pivot[month_order]

fig9 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='RdYlBu_r',
    colorbar=dict(title="Temperature (°C)"),
    hovertemplate='Month: %{x}<br>Hour: %{y}<br>Temp: %{z:.1f}°C<extra></extra>'
))

fig9.update_layout(
    title="Average Temperature by Hour and Month (Seasonal + Diurnal Patterns)",
    xaxis=dict(title="Month", tickangle=-45),
    yaxis=dict(title="Hour of Day"),
    template='plotly_white',
    height=600
)

st.plotly_chart(fig9, use_container_width=True)

st.success("You can see seasonal patterns (side to side) and daily temperature swings (top to bottom) - warmest in July afternoons, coldest in January mornings.")

# Day of Week Pattern
st.markdown("---")
st.subheader("Bonus: Day-of-Week Temperature Pattern")

dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_data = df.groupby('day_of_week')['temperature_2m'].agg(['mean', 'std']).reset_index()
dow_data['day_of_week'] = pd.Categorical(dow_data['day_of_week'], categories=dow_order, ordered=True)
dow_data = dow_data.sort_values('day_of_week')

fig_dow = go.Figure()

fig_dow.add_trace(go.Scatter(
    x=dow_data['day_of_week'],
    y=dow_data['mean'],
    mode='lines+markers',
    name='Mean Temperature',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=10),
    error_y=dict(
        type='data',
        array=dow_data['std'],
        visible=True,
        color='rgba(31, 119, 180, 0.3)'
    )
))

fig_dow = apply_custom_theme(fig_dow, "Temperature Variability by Day of Week")
fig_dow.update_xaxes(title="Day of Week")
fig_dow.update_yaxes(title="Temperature (°C)")

st.plotly_chart(fig_dow, use_container_width=True)

# Create composite risk score
df['severe_weather_risk'] = (
    (df['wind_gusts_10m'] > 15).astype(int) * 0.3 +  # High wind
    (df['rain'] > 10).astype(int) * 0.3 +             # Heavy rain
    (df['pressure_msl'] < 1000).astype(int) * 0.2 +   # Low pressure
    (df['cloud_cover'] > 90).astype(int) * 0.2        # Thick clouds
)

# Time series with risk zones
daily_risk = df.groupby(df['time'].dt.date)['severe_weather_risk'].max().reset_index()

fig_risk = go.Figure()

fig_risk.add_trace(go.Scatter(
    x=daily_risk['time'],
    y=daily_risk['severe_weather_risk'],
    mode='lines',
    fill='tozeroy',
    line=dict(color='darkred', width=2),
    fillcolor='rgba(139, 0, 0, 0.2)'
))

# Add threshold lines
fig_risk.add_hline(y=0.5, line_dash="dash", line_color="orange", 
                   annotation_text="Moderate Risk")
fig_risk.add_hline(y=0.7, line_dash="dash", line_color="red", 
                   annotation_text="High Risk")

fig_risk.update_layout(
    title="Severe Weather Risk Index (Composite Indicator)",
    xaxis_title="Date",
    yaxis_title="Risk Score (0-1)",
    template='plotly_white',
    height=400
)

st.plotly_chart(fig_risk, use_container_width=True)

st.error("""
- Score > 0.7: Emergency protocols
- Score 0.5-0.7: Issue weather warnings  
- Score < 0.5: Normal monitoring

""")

