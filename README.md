# 🚀 DataPulse

> **An End-to-End GitHub Repository Intelligence Platform**
>
> Automatically collects GitHub repository data, transforms it into analytics-ready datasets, and stores it in PostgreSQL for reporting and future dashboard development.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![GitHub API](https://img.shields.io/badge/API-GitHub-black?logo=github)
![Status](https://img.shields.io/badge/Status-Week%202%20Completed-success)

---

# 📌 Overview

**DataPulse** is a portfolio-focused Data Engineering project developed as part of the **Foundations of Data Engineering Internship**.

The project aims to build an end-to-end data pipeline that automatically collects GitHub repository data, stores it in PostgreSQL, performs data transformations, and prepares analytics-ready datasets for dashboards and business insights.

**Week 2** extends the Week 1 foundation by introducing transformation logic, analytics queries, logging, testing, and improved database design.

---

# 🎯 Week 1 Objectives

- Connect to the GitHub REST API
- Fetch GitHub repository metadata
- Store data into PostgreSQL
- Build a modular project structure
- Configure environment variables
- Create the foundation for an end-to-end data pipeline

---

# 🎯 Week 2 Objectives

- Improve GitHub API ingestion
- Support multiple repository collection
- Improve database schema
- Create analytics-ready transformations
- Build SQL analytics queries
- Implement structured logging
- Add automated testing
- Improve project documentation

---

# 💼 Business Problem

Organizations often need to analyze GitHub repositories to understand:

- Repository popularity
- Programming language trends
- Organization activity
- Repository growth
- Community engagement

Collecting and analyzing this information manually is inefficient.

**DataPulse** automates this process by creating a scalable data pipeline that continuously prepares repository data for analysis.

---

# ✨ Features

## Week 1

- ✅ GitHub REST API Integration
- ✅ PostgreSQL Warehouse
- ✅ SQLAlchemy ORM
- ✅ Environment Variable Configuration
- ✅ Modular Project Structure

## Week 2

- ✅ Improved API Ingestion
- ✅ Multiple Repository Support
- ✅ Data Transformation Layer
- ✅ Repository Metrics
- ✅ Analytics SQL Queries
- ✅ Structured Logging
- ✅ Unit Testing
- ✅ Improved Documentation

---

# 🏗 System Architecture

```text
                GitHub REST API
                       │
                       ▼
             Python Ingestion Layer
                       │
                       ▼
             Data Validation Layer
                       │
                       ▼
             Transformation Layer
                       │
                       ▼
             SQLAlchemy ORM Models
                       │
                       ▼
              PostgreSQL Warehouse
                       │
                       ▼
            Analytics SQL Queries
                       │
                       ▼
          Future Dashboard (Week 4)
```

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Core Programming Language |
| GitHub REST API | Data Source |
| Requests | API Communication |
| PostgreSQL | Data Warehouse |
| SQLAlchemy | ORM |
| psycopg2 | PostgreSQL Driver |
| python-dotenv | Environment Variables |
| Pytest | Unit Testing |
| Logging | Application Monitoring |
| Git | Version Control |

---

# 📂 Project Structure

```text
DataPulse/
│
├── config/
│
├── database/
│
├── docs/
│
├── ingestion/
│
├── transformations/
│
├── sql/
│
├── tests/
│
├── utils/
│
├── logs/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

---

# 🔄 Data Pipeline

```text
GitHub REST API
        │
        ▼
Repository Ingestion
        │
        ▼
Data Validation
        │
        ▼
Transformation Layer
        │
        ▼
PostgreSQL Warehouse
        │
        ▼
Analytics Queries
        │
        ▼
Future Dashboard
```

---

# 📊 Transformation Layer

Week 2 introduces analytics-ready fields such as:

- Repository Age
- Popularity Score
- Days Since Last Update
- Repository Size Category
- Language Classification

These derived metrics simplify future reporting and dashboard development.

---

# 📈 Analytics Queries

The project now includes SQL queries to answer questions such as:

- Top repositories by stars
- Top repositories by forks
- Most popular programming languages
- Recently updated repositories
- Repository age analysis
- Average repository statistics
- Organization-level insights

---

# 📝 Logging

The application now uses structured logging.

Example:

```text
INFO Connecting to GitHub API...
INFO Fetching repositories...
INFO Connected to PostgreSQL...
INFO Stored 50 repositories
WARNING Duplicate repository skipped
ERROR API request failed
```

---

# 🧪 Testing

Week 2 introduces automated tests for:

- GitHub API client
- Database operations
- Transformation functions
- Duplicate detection
- Repository validation

---

# ⚙ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/datapulse.git
```

Navigate into the project:

```bash
cd datapulse
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your `.env` file and run:

```bash
python main.py
```

---

# 🗄 Database

The warehouse stores:

- Repository Name
- Owner
- Description
- Stars
- Forks
- Watchers
- Open Issues
- Programming Language
- Default Branch
- Repository URL
- Created Date
- Updated Date
- Last Synced Timestamp

The transformation layer generates additional analytics fields for reporting.

---

# 📅 Progress

## ✅ Week 1

- Project Setup
- GitHub API
- PostgreSQL
- Initial Data Ingestion

## ✅ Week 2

- Improved API Ingestion
- Analytics Transformation Layer
- SQL Queries
- Logging
- Testing
- Documentation
- Improved Database Design

---

# 🚀 Roadmap

## Week 3

- Second API Integration
- Data Quality Validation
- Multi-source Data Pipeline
- Enhanced Analytics

## Week 4

- dbt Models
- Docker
- Streamlit Dashboard
- Deployment

## Week 5

- Final Documentation
- Reflection Report
- Presentation
- Portfolio Polish

---

# 📚 Learning Outcomes

This project demonstrates practical knowledge of:

- Data Engineering Fundamentals
- REST APIs
- PostgreSQL
- SQLAlchemy
- Data Transformation
- SQL Analytics
- Logging
- Testing
- Software Architecture
- Git & GitHub

---

# 🔮 Future Enhancements

- dbt Data Models
- Docker Compose
- GitHub Actions
- Streamlit Dashboard
- Interactive Visualizations
- Multi-source API Integration
- CI/CD Pipeline
- Monitoring
- Cloud Deployment

---

# 🤝 Contributing

This project is being developed as part of a Summer Internship and serves as a portfolio project. Suggestions and improvements are always welcome.

---

# 📜 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

- GitHub REST API
- PostgreSQL
- SQLAlchemy
- Python Community
- Futurense Internship Program
- Internship Mentors & Faculty

---

## ✅ Week 1 Completed

- Project initialized
- Professional folder structure created
- GitHub REST API integrated
- PostgreSQL database configured
- SQLAlchemy ORM implemented
- Environment variable management
- Initial documentation completed

---

## ⭐ Week 2 Status

**Project Foundation:** ✅ Completed

**Analytics Layer:** ✅ Completed

**Ready for Week 3:** 🚀

---

# 🚀 Current Project Stage

```
Week 1 ✅ Foundation
        │
        ▼
Week 2 ✅ Analytics Layer
        │
        ▼
Week 3 ⏳ Multi-Source Data Integration
        │
        ▼
Week 4 ⏳ Dashboard & Deployment
        │
        ▼
Week 5 ⏳ Final Showcase
```

Current Completion Progress:

**████████░░░░░░░░░░ 40%**
