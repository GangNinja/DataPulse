# 🚀 DataPulse

> **An End-to-End GitHub Repository Intelligence Platform**
>
> Automatically collects GitHub repository data, transforms it into analytics-ready datasets, calculates repository health metrics, and stores everything in PostgreSQL for future analytics and dashboard development.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![GitHub API](https://img.shields.io/badge/API-GitHub-black?logo=github)
![Status](https://img.shields.io/badge/Status-Week%203%20Completed-success)

---

# 📌 Overview

**DataPulse** is a portfolio-oriented Data Engineering project developed as part of the **Foundations of Data Engineering Internship**.

The project builds a complete data pipeline that automatically retrieves GitHub repository data, stores it in PostgreSQL, transforms raw data into analytics-ready datasets, and generates repository health insights for business analysis.

After Week 3, DataPulse has evolved into a **GitHub Repository Intelligence Platform** capable of ingesting, transforming, analysing, and scoring repository data.

---

# 🎯 Objectives

## ✅ Week 1 Objectives

- Connect to GitHub REST API
- Fetch repository metadata
- Store data into PostgreSQL
- Build modular architecture
- Configure environment variables
- Create the project foundation

---

## ✅ Week 2 Objectives

- Improve API ingestion
- Support multiple repositories
- Create transformation layer
- Generate analytics metrics
- Write SQL analytical queries
- Add structured logging
- Add automated tests
- Improve documentation

---

## ✅ Week 3 Objectives

- Build a meaningful mini extension
- Calculate Repository Health Score
- Categorize repositories based on health
- Improve testing coverage
- Improve project documentation
- Prepare project for deployment

---

# 💼 Business Problem

Organizations often monitor hundreds of GitHub repositories.

Manually tracking:

- Repository popularity
- Community engagement
- Activity
- Repository health
- Technology trends

is inefficient.

DataPulse automates this process by collecting repository data, transforming it into useful business metrics, and generating a health score for each repository.

---

# ✨ Features

## Week 1

- ✅ GitHub REST API
- ✅ PostgreSQL Database
- ✅ SQLAlchemy ORM
- ✅ Modular Architecture
- ✅ Environment Configuration

---

## Week 2

- ✅ Multiple Repository Support
- ✅ Analytics Transformation Layer
- ✅ SQL Analytics Queries
- ✅ Logging
- ✅ Automated Testing
- ✅ Improved Documentation

---

## Week 3

- ✅ Repository Health Score
- ✅ Health Categories
- ✅ Repository Ranking
- ✅ Extended Test Coverage
- ✅ Mini Extension Completed

---

# 🏗 System Architecture

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
          Repository Health Engine
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
| Logging | Monitoring |
| Pytest | Automated Testing |
| Git | Version Control |

---

# 📂 Project Structure

```text
DataPulse/
│
├── config/
├── database/
├── docs/
├── ingestion/
├── transformations/
├── extensions/
│   └── repository_health.py
├── sql/
├── tests/
├── utils/
├── logs/
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
Repository Health Score
        │
        ▼
Analytics SQL Queries
```

---

# ❤️ Repository Health Score

The Repository Health Score is the **Week 3 Mini Extension**.

It evaluates repository quality using repository statistics and generates a score between **0 and 100**.

Example factors include:

- ⭐ Stars
- 🍴 Forks
- 👀 Watchers
- 📅 Repository Activity

Repositories are classified as:

| Score | Category |
|--------|----------|
| 90–100 | Excellent |
| 75–89 | Very Good |
| 60–74 | Good |
| 40–59 | Average |
| 0–39 | Needs Attention |

---

# 📊 Analytics

Current analytics include:

- Top repositories by stars
- Top repositories by forks
- Repository popularity
- Programming language distribution
- Repository age
- Repository Health Score
- Repository rankings

---

# 🧪 Testing

Automated tests cover:

- API integration
- Database operations
- Repository transformations
- Health score calculation
- Health category generation
- Duplicate handling

---

# 📝 Logging

The application provides structured logging.

Example:

```text
INFO Connecting to GitHub API...
INFO Fetching repositories...
INFO Repository stored successfully.
INFO Calculating Repository Health...
INFO Health Score Generated.
WARNING Duplicate repository skipped.
ERROR API request failed.
```

---

# ⚙ Installation

Clone the repository.

```bash
git clone https://github.com/YOUR_USERNAME/datapulse.git
```

Navigate into the project.

```bash
cd datapulse
```

Create a virtual environment.

```bash
python -m venv .venv
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Configure your `.env` file.

Run:

```bash
python main.py
```

---

# 🗄 Database

Current tables include:

- Repositories
- Repository Metrics
- Repository Health

The database stores repository metadata, analytics metrics, and health scores for reporting.

---

# 📅 Project Status

| Week | Status | Description |
|------|--------|-------------|
| ✅ Week 1 | Completed | Project Foundation |
| ✅ Week 2 | Completed | Analytics Layer |
| ✅ Week 3 | Completed | Repository Health Score (Mini Extension) |
| ⏳ Week 4 | Upcoming | Dashboard, Docker & Deployment |
| ⏳ Week 5 | Upcoming | Final Documentation & Presentation |

---

# 📈 Current Progress

```
Week 1  ✅ Foundation

↓

Week 2  ✅ Analytics Layer

↓

Week 3  ✅ Repository Health Score

↓

Week 4  ⏳ Dashboard & Deployment

↓

Week 5  ⏳ Final Showcase
```

**Overall Completion:** **60%**

---

# 🚀 Roadmap

## Week 4

- Streamlit Dashboard
- Docker Support
- Application Deployment
- Dashboard Analytics
- Final Documentation

---

## Week 5

- Final Presentation
- Reflection Report
- Portfolio Improvements
- Resume Ready Repository

---

# 📚 Learning Outcomes

This project demonstrates practical knowledge of:

- Data Engineering
- REST APIs
- PostgreSQL
- SQLAlchemy
- Data Transformation
- SQL Analytics
- Python Logging
- Automated Testing
- Software Architecture
- Repository Analytics

---

# 🔮 Future Enhancements

- Interactive Streamlit Dashboard
- Docker Compose
- dbt Models
- GitHub Actions
- CI/CD Pipeline
- Cloud Deployment
- Interactive Visualizations
- Advanced Repository Analytics

---

# 🤝 Contributing

This project is being developed as part of the **Foundations of Data Engineering Internship** and serves as a portfolio project.

Suggestions and improvements are welcome.

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 🙏 Acknowledgements

- GitHub REST API
- PostgreSQL
- SQLAlchemy
- Python Community
- Futurense Internship Program
- Internship Mentors & Faculty

---

# ⭐ Current Status

✅ Week 1 Completed

✅ Week 2 Completed

✅ Week 3 Completed

🚀 Ready for Week 4
