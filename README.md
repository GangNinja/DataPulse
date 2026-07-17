# 🚀 DataPulse

> **An End-to-End GitHub Repository Intelligence Platform**
>
> DataPulse is a production-inspired Data Engineering project that collects GitHub repository data, performs comprehensive data quality validation and cleaning, transforms the data into analytics-ready datasets, calculates repository health metrics, and visualizes insights through an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![GitHub API](https://img.shields.io/badge/API-GitHub-black?logo=github)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)
![Status](https://img.shields.io/badge/Status-Week%204%20Completed-success)

---

# 📖 Overview

DataPulse is a complete Data Engineering pipeline developed as part of the **Foundations of Data Engineering Internship**.

The project automatically collects GitHub repository information through the GitHub REST API, validates and cleans the data, stores it inside PostgreSQL, transforms it into analytics-ready datasets, calculates Repository Health Scores, and presents business insights using an interactive Streamlit dashboard.

By the end of Week 4, the project demonstrates a complete ETL workflow along with data quality management and business intelligence visualization.

---

# 🎯 Project Objectives

## ✅ Week 1
- GitHub REST API integration
- PostgreSQL database setup
- SQLAlchemy ORM
- Modular project architecture
- Environment configuration

---

## ✅ Week 2
- Multi-repository ingestion
- Data transformation layer
- SQL analytics
- Logging
- Automated testing

---

## ✅ Week 3
- Repository Health Score
- Repository ranking
- Health categorization
- Mini Extension
- Documentation improvements

---

## ✅ Week 4
- Data Quality Framework
- Missing value handling
- Duplicate detection & removal
- Data validation
- Data cleaning
- Data Quality Reports
- Interactive Streamlit Dashboard
- Additional testing

---

# 💼 Business Problem

Organizations maintain hundreds of GitHub repositories.

Tracking repository popularity, activity, technology usage, and overall repository quality manually becomes increasingly difficult.

DataPulse automates this process by:

- Collecting repository metadata
- Cleaning inconsistent data
- Eliminating duplicate records
- Generating repository health metrics
- Producing analytics-ready datasets
- Displaying insights in a dashboard

---

# ✨ Features

## Week 1

- GitHub REST API Integration
- PostgreSQL Data Warehouse
- SQLAlchemy ORM
- Modular Architecture
- Environment Variables

---

## Week 2

- Multi Repository Support
- Data Transformation Layer
- SQL Analytics
- Logging
- Unit Testing

---

## Week 3

- Repository Health Score
- Repository Ranking
- Health Categories
- Extended Testing

---

## Week 4

- Data Quality Framework
- Missing Value Handling
- Duplicate Detection
- Duplicate Removal
- Data Validation
- Data Cleaning
- Data Quality Reports
- Streamlit Dashboard
- Interactive Analytics
- Dashboard KPIs
- Repository Health Visualization

---

# 🏗 System Architecture

```text
                GitHub REST API
                       │
                       ▼
               Repository Ingestion
                       │
                       ▼
             Data Quality Framework
        (Validation + Cleaning + Reports)
                       │
                       ▼
            Transformation Layer
                       │
                       ▼
             PostgreSQL Warehouse
                       │
                       ▼
          Repository Health Engine
                       │
                       ▼
             SQL Analytics Layer
                       │
                       ▼
            Streamlit Dashboard
```

---

# ⚙ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Programming |
| GitHub REST API | Data Source |
| Requests | API Requests |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| psycopg2 | PostgreSQL Driver |
| Streamlit | Dashboard |
| Plotly | Interactive Charts |
| Pytest | Testing |
| Logging | Monitoring |

---

# 📂 Project Structure

```text
DataPulse/
│
├── config/
├── dashboard/
│   └── streamlit_app.py
│
├── database/
├── docs/
│
├── extensions/
│   └── repository_health.py
│
├── ingestion/
│
├── quality/
│   ├── validation.py
│   ├── cleaning.py
│   ├── quality_checker.py
│   └── report.py
│
├── reports/
│
├── sql/
├── tests/
├── transformations/
├── utils/
├── logs/
│
├── README.md
├── requirements.txt
└── main.py
```

---

# 🔄 ETL Pipeline

```text
GitHub API

        │

        ▼

Repository Ingestion

        │

        ▼

Data Validation

        │

        ▼

Data Cleaning

        │

        ▼

Transformation Layer

        │

        ▼

PostgreSQL Warehouse

        │

        ▼

Repository Health Score

        │

        ▼

Analytics Queries

        │

        ▼

Streamlit Dashboard
```

---

# 🧹 Data Quality Framework

The Week 4 enhancement introduces a dedicated Data Quality Framework.

It automatically performs:

- Missing value detection
- NULL value handling
- Duplicate repository detection
- Duplicate removal
- URL validation
- Repository name validation
- Numeric field validation
- Data normalization

---

# 📊 Data Quality Report

Each execution generates a quality report summarizing:

- Total records processed
- Valid records
- Missing values fixed
- Duplicate records removed
- Invalid records rejected
- Overall Data Quality Score

Example:

```text
Records Processed : 250
Valid Records : 243
Missing Values Fixed : 11
Duplicates Removed : 5
Rejected Records : 2
Quality Score : 97%
```

---

# ❤️ Repository Health Score

The Repository Health Engine evaluates repositories using metrics such as:

- Stars
- Forks
- Watchers
- Repository activity

Repositories are classified into:

| Score | Category |
|--------|----------|
| 90–100 | Excellent |
| 75–89 | Very Good |
| 60–74 | Good |
| 40–59 | Average |
| 0–39 | Needs Attention |

---

# 📈 Dashboard

The interactive Streamlit dashboard provides:

- Total repositories
- Average stars
- Average forks
- Language distribution
- Top repositories
- Repository Health Score distribution
- Repositories needing attention
- Data Quality summary

---

# 📊 Analytics

Current analytics include:

- Top repositories by stars
- Top repositories by forks
- Programming language distribution
- Repository popularity
- Repository age
- Repository Health Score
- Data Quality metrics

---

# 🧪 Testing

Automated tests cover:

- API integration
- Database operations
- Data validation
- Data cleaning
- Duplicate detection
- Health Score calculation
- Dashboard utilities

---

# 📝 Logging

The project provides structured logging.

Example:

```text
INFO Fetching repositories...
INFO Running Data Quality Checks...
INFO Missing values cleaned.
INFO Duplicate repositories removed.
INFO Repository Health calculated.
INFO Dashboard started.
WARNING Invalid repository URL detected.
ERROR Validation failed.
```

---

# 🚀 Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/DataPulse.git
```

Navigate to the project.

```bash
cd DataPulse
```

Create a virtual environment.

```bash
python -m venv .venv
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Configure environment variables.

```bash
cp .env.example .env
```

Run the project.

```bash
python main.py
```

Launch the dashboard.

```bash
streamlit run dashboard/streamlit_app.py
```

---

# 📅 Project Progress

| Week | Status |
|------|--------|
| ✅ Week 1 | Completed |
| ✅ Week 2 | Completed |
| ✅ Week 3 | Completed |
| ✅ Week 4 | Completed |
| ⏳ Week 5 | Docker, Deployment & Final Documentation |

---

# 📌 Current Progress

```text
Week 1  ✅ Foundation

↓

Week 2  ✅ Analytics

↓

Week 3  ✅ Repository Health Score

↓

Week 4  ✅ Data Quality + Dashboard

↓

Week 5  ⏳ Docker + Deployment + Final Submission
```

**Overall Completion:** **80%**

---

# 🎓 Learning Outcomes

This project demonstrates practical knowledge of:

- REST APIs
- ETL Pipelines
- Data Engineering
- PostgreSQL
- SQLAlchemy
- Data Cleaning
- Data Validation
- Data Quality
- Repository Analytics
- Streamlit
- Plotly
- Testing
- Logging
- Software Architecture

---

# 🚀 Future Enhancements

- Docker Support
- Docker Compose
- Cloud Deployment
- CI/CD Pipeline
- GitHub Actions
- Advanced Analytics
- Automated Scheduling
- Real-time Repository Monitoring

---

# 🤝 Contributing

Contributions are welcome.

Please fork the repository and submit a pull request.

---

# 📜 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

- GitHub REST API
- PostgreSQL
- SQLAlchemy
- Streamlit
- Plotly
- Python Community
- Foundations of Data Engineering Internship
- Mentors and Faculty

---

# ⭐ Project Status

```
✅ Week 1 Completed

✅ Week 2 Completed

✅ Week 3 Completed

✅ Week 4 Completed

🚀 Ready for Week 5
```
