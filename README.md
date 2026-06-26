# 🚀 DataPulse

> **An End-to-End GitHub Repository Intelligence Platform**
>
> Automatically ingests GitHub repository data using the GitHub REST API, stores it in PostgreSQL, and prepares structured data for analytics, reporting, and dashboards.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![GitHub API](https://img.shields.io/badge/API-GitHub-black?logo=github)
![Status](https://img.shields.io/badge/Status-Week%201%20Completed-success)

---

# 📌 Overview

**DataPulse** is a Data Engineering project built during my Summer Internship 2026 under the **Foundations of Data Engineering** track.

The goal is to build an end-to-end data pipeline that automatically collects GitHub repository data, stores it inside a PostgreSQL warehouse, and prepares it for future analytics and visualization.

This repository currently contains the **Week 1 Foundation** of the project.

---

# 🎯 Objectives

- Connect to GitHub REST API
- Fetch repository metadata
- Store data into PostgreSQL
- Build a modular Data Engineering project
- Prepare the project for future ETL pipelines
- Build a strong portfolio project

---

# 💼 Business Problem

Software companies often need insights into GitHub repositories to monitor project popularity, technology trends, and repository activity.

Manually collecting this information is:

- Time consuming
- Error-prone
- Difficult to scale
- Impossible to analyze historically

DataPulse automates this process by creating a reusable data ingestion pipeline.

---

# ✨ Features

✅ GitHub REST API Integration

✅ PostgreSQL Data Warehouse

✅ SQLAlchemy ORM

✅ Environment Variable Configuration

✅ Modular Project Structure

✅ Error Handling

✅ Logging Support

✅ Ready for Future Data Transformation

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
              SQLAlchemy ORM Models
                       │
                       ▼
               PostgreSQL Warehouse
                       │
                       ▼
          Future dbt Transformations
                       │
                       ▼
           Future Analytics Dashboard
```

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Core Programming Language |
| GitHub REST API | Data Source |
| Requests | API Communication |
| SQLAlchemy | ORM |
| PostgreSQL | Data Warehouse |
| psycopg2 | PostgreSQL Driver |
| python-dotenv | Environment Variables |
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
├── tests/
│
├── utils/
│
├── main.py
│
├── requirements.txt
│
├── README.md
│
├── .gitignore
│
└── .env.example
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/datapulse.git
```

## Navigate

```bash
cd datapulse
```

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate it.

## Install Requirements

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file.

Example:

```env
GITHUB_TOKEN=your_github_token
DATABASE_URL=postgresql://postgres:password@localhost:5432/datapulse
```

---

# ▶ Running

```bash
python main.py
```

The application will:

1. Connect to GitHub API
2. Fetch Repository Data
3. Validate Response
4. Connect PostgreSQL
5. Store Data
6. Display Success Logs

---

# 🗄 Database

Current repository stores:

- Repository Name
- Owner
- Description
- Stars
- Forks
- Watchers
- Open Issues
- Language
- Default Branch
- Repository URL
- Created Date
- Updated Date

---

# 📅 Week 1 Progress

- ✅ Project Initialized
- ✅ Folder Structure Created
- ✅ GitHub API Connected
- ✅ PostgreSQL Connected
- ✅ Data Ingestion Implemented
- ✅ Configuration Completed
- ✅ Initial Documentation Completed

---

# 🚀 Roadmap

## Week 2

- dbt
- Data Modeling
- SQL Transformations
- Architecture Decision Records

## Week 3

- Second API
- Data Quality Tests
- Mini Extension

## Week 4

- Docker
- Streamlit Dashboard
- Deployment

## Week 5

- Final Documentation
- Reflection
- Resume Bullets
- Presentation

---

# 📚 Learning Outcomes

This project helped me understand:

- REST APIs
- Python
- PostgreSQL
- SQLAlchemy
- Data Ingestion
- Data Warehousing
- Project Structure
- Version Control

---

# 🔮 Future Enhancements

- Docker Support
- GitHub Actions
- Streamlit Dashboard
- dbt Transformations
- Data Quality Checks
- Multiple APIs
- Monitoring
- Deployment
- CI/CD Pipeline

---

# 🤝 Contributing

This project is currently being developed as part of my Summer Internship.

Suggestions and improvements are always welcome.

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
- My mentors and faculty for their guidance.

---

## ⭐ If you found this project interesting, consider giving it a star!
