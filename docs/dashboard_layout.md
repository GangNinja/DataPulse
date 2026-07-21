# Week 4 Session 2: Streamlit Dashboard

This session adds an interactive dashboard for the existing DataPulse warehouse.

## Pages

- Home
- Repository Analytics
- Repository Health
- Data Quality Report

## Dashboard Content

- Total repositories
- Average stars
- Average forks
- Average health score
- Language distribution
- Repository size distribution
- Repository health distribution
- Top repositories
- Healthiest repositories
- Repositories needing attention
- Latest data quality report

## Run Command

```powershell
streamlit run dashboard/streamlit_app.py
```

Run `python main.py` before opening the dashboard so the PostgreSQL tables and
latest data quality report are refreshed.

## Note

Docker support is intentionally not included in this session. It belongs to
Week 4 Session 3.
