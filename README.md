# Weather Analytics Dashboard

A comprehensive weather analytics dashboard built with Streamlit, Plotly, and MongoDB Atlas. Analyzes meteorological data including solar radiation, agricultural metrics, and marine conditions.

## Features

- 🌡️ **Temperature Analysis** - Land and marine temperature trends
- ☀️ **Solar Analytics** - Shortwave and diffuse radiation analysis
- 🌾 **Agricultural Insights** - Water balance and stress index monitoring
- 💨 **Wind & Marine** - Wind speed, direction, and pressure analysis
- 📊 **Correlations** - Cross-variable correlation matrix
- 🗓️ **Temporal Analysis** - Time-series weather patterns

## Local Setup

### Prerequisites
- Python 3.8+
- MongoDB Atlas account with connection string

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/weather-analytics-dashboard.git
   cd weather-analytics-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create `.env` file in the project root:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
   ```

5. **Run the dashboard**
   ```bash
   cd dashboard
   streamlit run app.py
   ```

The app will open at `http://localhost:8501`

## Deployment on Streamlit Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/weather-analytics-dashboard.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repository
4. Configure deployment:
   - **Repository**: yourusername/weather-analytics-dashboard
   - **Branch**: main
   - **Main file path**: dashboard/app.py

5. Click **Deploy**

### Step 3: Add Secrets
1. In Streamlit Cloud dashboard, go to **Advanced settings** → **Secrets**
2. Add your MongoDB credentials:
   ```toml
   MONGO_URL = "mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0"
   ```
3. Click **Save**

The app will automatically redeploy with your secrets.

## Project Structure

```
├── dashboard/
│   ├── app.py                    # Main app entry point
│   ├── utils.py                  # Utility functions & MongoDB connection
│   └── pages/
│       ├── Agricultural_Insights.py
│       ├── Correlations.py
│       ├── map.py
│       ├── Solar_Analytics.py
│       ├── Temporal_Analysis.py
│       └── Wind_Marine.py
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml             # Local secrets (not versioned)
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Data Source

- **Weather Data**: [Open-Meteo API](https://open-meteo.com/)
- **Database**: MongoDB Atlas
- **ETL Pipeline**: Dagster
- **Visualization**: Plotly

## Technologies Used

- **Frontend**: Streamlit
- **Database**: MongoDB Atlas
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **ETL**: Dagster
- **Hosting**: Streamlit Cloud

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URL` | MongoDB Atlas connection string | Yes |

## Troubleshooting

### Connection Issues
- Verify MongoDB IP whitelist includes Streamlit Cloud IP: `0.0.0.0/0`
- Test connection locally before deploying

### Missing Data
- Ensure ETL pipeline has run and populated the `fact_weather` collection
- Check MongoDB database name is `weather_analytics`

### Performance
- Data is cached for 10 minutes - adjust TTL in `utils.py` if needed
- For large datasets, consider aggregation pipelines in MongoDB

## License

MIT License - feel free to use this project as a template

## Contact & Support

For issues or questions, please open an issue on GitHub.
