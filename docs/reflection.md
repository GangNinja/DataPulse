# Project Reflection

DataPulse is a GitHub Repository Intelligence Platform that I built as a
portfolio-ready data engineering project. The project started as a simple
pipeline that could fetch one repository from the GitHub REST API and store it
in PostgreSQL. Over several weeks, it grew into a more complete data platform
with ingestion, validation, transformation, scoring, analytics SQL, a Streamlit
dashboard, Docker support, tests, and documentation.

The first major thing I built was the ingestion foundation. I created a GitHub
API client that reads configuration from environment variables, connects to the
GitHub REST API, handles API errors, and transforms repository responses into a
database-ready structure. This helped me understand how production data
pipelines separate responsibilities. The API client fetches data, the ingestion
module validates and transforms responses, and the database layer handles
persistence. That separation made later weeks much easier because each feature
had a natural place to live.

The second major part was the PostgreSQL warehouse. I used SQLAlchemy ORM to
define tables for repositories, derived metrics, and repository health. The
core table stores GitHub repository metadata such as owner, repository name,
stars, forks, watchers, open issues, language, repository size, created date,
updated date, URL, and last synced timestamp. I added constraints and indexes so
the database is not just a storage location, but a more reliable analytical
store. I also implemented duplicate protection so repeated pipeline runs do not
create duplicate repository rows.

In Week 2, I expanded the project from single-repository ingestion to bulk
organization or user ingestion. This required handling pagination from the
GitHub API and thinking about duplicates at more than one layer. The pipeline
deduplicates incoming records before writing to the database, and the database
also has a unique constraint on owner and repository name. This taught me that
good data engineering should not trust only one layer for data correctness. The
application and database should both protect data quality.

The transformation layer was another important milestone. I created
`repository_metrics`, an analytics-ready table with repository age, popularity
score, days since last update, size category, and language category. This gave
the project a warehouse-style design where raw-ish source data is stored in one
table and derived analysis fields are stored separately. It also made the SQL
analytics queries and dashboard easier to build because they could query
prepared fields instead of recalculating everything every time.

In Week 3, I added the Repository Health Score extension. The score combines
stars, forks, watchers, and repository activity into a normalized value between
0 and 100. I learned that scoring systems need careful explanation. When I ran
the project against a large organization like Microsoft, most repositories
scored below 20 because the normalization compares every repository against the
largest repository in the warehouse. That result is technically correct, but it
can be surprising to a user. This helped me understand that data products need
interpretability, not just calculations. I documented this as a future dashboard
consideration and added a note about possible log-scaled normalization.

In Week 4, I focused on polish and readiness. The data quality framework checks
missing values, NULL values, duplicate repositories, duplicate IDs, invalid
URLs, empty names, negative metrics, and invalid dates. It also performs safe
cleaning such as trimming whitespace, replacing missing descriptions, replacing
missing languages with `Unknown`, normalizing repository names, and converting
timestamps when possible. After each run, it generates a data quality report.
This made the project feel much closer to a real data pipeline because it
provides visibility into what happened during processing.

The Streamlit dashboard helped turn the project from a backend pipeline into an
interactive analytics product. The dashboard shows KPIs, language distribution,
repository size distribution, health score distribution, top repositories,
repositories needing attention, and the latest data quality report. Building
the dashboard taught me that data engineering work becomes more valuable when
stakeholders can explore the output. It also made me think more about UI/UX,
especially around explaining the health score and organizing charts so they are
easy to read.

Docker support was another useful learning step. I added a Dockerfile and a
Docker Compose setup with PostgreSQL, the dashboard, and an optional pipeline
service. This made the project easier to reproduce because someone can start
the database and dashboard with Docker Compose. I learned about service
dependencies, container networking, volumes, and port mapping. I also learned
why environment variables and secrets should be handled carefully.

Preparing the project for final submission was also an important part of the
work. I cleaned generated logs and reports from the repository, added a clearer
README, created deployment notes, added architecture diagrams, and organized
supporting documents such as resume bullets, interview notes, and a future
roadmap. This reminded me that a portfolio project is judged not only by the
code, but also by how clearly another developer can understand, run, and
evaluate it. Good documentation reduces confusion and makes the technical work
more credible.

The biggest challenges were around integration. Individual modules were easier
to build than the full system. For example, the dashboard initially had import
path issues because Streamlit ran from a different working directory. PostgreSQL
also required a numeric cast for rounding floating-point health scores. Pytest
had Windows temp directory permission issues, so I adjusted tests to avoid
depending on blocked temp paths. These problems were valuable because they felt
like real engineering issues: not just writing code, but making the project
work reliably on an actual machine.

If I improved DataPulse further, I would add scheduled ingestion, better schema
migrations, CI/CD, and cloud deployment. I would also improve the health score
with log scaling or percentile-based scoring so medium repositories are not
overly punished by a few very large repositories. I would consider adding dbt
for transformation modeling and Kafka for streaming event data if the project
expanded beyond GitHub repository snapshots.

Overall, DataPulse helped me practice API ingestion, PostgreSQL modeling,
SQLAlchemy, data quality, analytics transformations, dashboarding, testing,
Docker, and documentation. More importantly, it helped me understand how small
data engineering pieces connect into a complete product. The final result is a
project I can explain clearly in interviews and continue improving as my skills
grow.
