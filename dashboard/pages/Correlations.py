import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.append('..')
from utils import *

st.set_page_config(page_title="Correlations", page_icon="�", layout="wide")

st.title("Cross-Dataset Correlation Analysis")
st.markdown("---")

# Load data
conn = get_db_connection()
df = load_fact_table(conn)

# Wind vs Radiation
st.subheader("Wind vs Solar Radiation")

# Sample for performance
scatter_df = df.sample(n=min(5000, len(df)), random_state=42)

fig10 = px.scatter(
    scatter_df,
    x='wind_speed_10m',
    y='shortwave_radiation',
    size='rain',
    color='month_name',
    hover_data=['temperature_2m', 'pressure_msl', 'cloud_cover'],
    title="Wind Speed vs Solar Radiation (sized by Rainfall)",
    labels={
        'wind_speed_10m': 'Wind Speed @ 10m (m/s)',
        'shortwave_radiation': 'Solar Radiation (W/m²)',
        'rain': 'Rainfall (mm)'
    },
    color_discrete_sequence=px.colors.qualitative.Vivid
)

fig10.update_layout(
    template='plotly_white',
    height=600,
    legend=dict(title="Month")
)

st.plotly_chart(fig10, use_container_width=True)


# Correlation Matrix
st.markdown("---")
st.subheader("Correlation Matrix: Key Variables")

# Define variables from actual schema
corr_vars = [
    'temperature_2m',
    'precipitation',
    'cloud_cover',
    'shortwave_radiation',
    'direct_radiation',
    'diffuse_radiation',
    'wind_speed_10m',
    'rain',
    'et0_fao_evapotranspiration',
    'vapor_pressure_deficit',
    'pressure_msl',
    'surface_pressure',
    'wind_speed_100m',
    'wind_gusts_10m'
]

# Filter to only existing columns
corr_vars = [col for col in corr_vars if col in df.columns]

st.info(f"Looking at correlations between {len(corr_vars)} weather variables")

# Calculate correlation matrix
corr_matrix = df[corr_vars].corr()

# Create heatmap with better labels
labels = [col.replace('_', ' ').title() for col in corr_matrix.columns]

fig_corr = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=labels,
    y=labels,
    colorscale='RdBu',
    zmid=0,
    text=corr_matrix.values.round(2),
    texttemplate='%{text}',
    textfont={"size": 9},
    colorbar=dict(title="Correlation")
))

fig_corr.update_layout(
    title="Pearson Correlation Matrix - Meteorological Variables",
    template='plotly_white',
    height=800,
    xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
    yaxis=dict(tickfont=dict(size=9))
)

st.plotly_chart(fig_corr, use_container_width=True)

# Show strongest correlations
st.markdown("---")
st.subheader("Strongest Correlations")

# Get correlation pairs (excluding diagonal)
corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        corr_pairs.append({
            'Variable 1': corr_matrix.columns[i].replace('_', ' ').title(),
            'Variable 2': corr_matrix.columns[j].replace('_', ' ').title(),
            'Correlation': corr_matrix.iloc[i, j]
        })

corr_df = pd.DataFrame(corr_pairs)
corr_df['Abs Correlation'] = corr_df['Correlation'].abs()
corr_df = corr_df.sort_values('Abs Correlation', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.write("**Top 5 Positive Correlations:**")
    positive = corr_df[corr_df['Correlation'] > 0].head(5)
    st.dataframe(
        positive[['Variable 1', 'Variable 2', 'Correlation']].style.format({'Correlation': '{:.3f}'}),
        hide_index=True,
        use_container_width=True
    )

with col2:
    st.write("**Top 5 Negative Correlations:**")
    negative = corr_df[corr_df['Correlation'] < 0].head(5)
    st.dataframe(
        negative[['Variable 1', 'Variable 2', 'Correlation']].style.format({'Correlation': '{:.3f}'}),
        hide_index=True,
        use_container_width=True
    )

st.info("Cloud cover and solar radiation are strongly inversely related - more clouds means less sun.")

# Bonus: 3D Scatter
st.markdown("---")
st.subheader("Bonus: 3D Analysis of Temperature, Wind, and Solar Radiation")

scatter_3d = df.sample(n=min(2000, len(df)), random_state=42)

fig_3d = go.Figure(data=[go.Scatter3d(
    x=scatter_3d['temperature_2m'],
    y=scatter_3d['wind_speed_10m'],
    z=scatter_3d['shortwave_radiation'],
    mode='markers',
    marker=dict(
        size=4,
        color=scatter_3d['rain'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Rain (mm)")
    ),
    text=scatter_3d['month_name'],
    hovertemplate='<b>%{text}</b><br>Temp: %{x:.1f}°C<br>Wind: %{y:.1f} m/s<br>Radiation: %{z:.0f} W/m²<extra></extra>'
)])

fig_3d.update_layout(
    title="3D Analysis: Temperature × Wind × Solar Radiation (colored by Rainfall)",
    scene=dict(
        xaxis_title='Temperature (°C)',
        yaxis_title='Wind Speed (m/s)',
        zaxis_title='Solar Radiation (W/m²)'
    ),
    template='plotly_white',
    height=700
)

st.plotly_chart(fig_3d, use_container_width=True)

st.caption("3D visualization helps spot relationships between three variables at once, which is harder to see in flat charts.")
