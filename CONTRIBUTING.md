# Contributing

Thank you for your interest in DataPulse.

This project is currently maintained as a portfolio data engineering project.
Contributions should keep the codebase simple, readable, and suitable for a
junior data engineer portfolio.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with local values, then run:

```powershell
python main.py
python -m pytest
streamlit run dashboard\streamlit_app.py
```

## Contribution Guidelines

- Keep changes small and focused.
- Do not commit `.env`, logs, generated reports, or local caches.
- Add or update tests for behavior changes.
- Keep business logic in reusable modules.
- Keep dashboard code focused on presentation and simple data loading.
- Avoid adding new dependencies unless they clearly improve the project.
- Update documentation when commands, architecture, or behavior changes.

## Pull Request Checklist

- Tests pass with `python -m pytest`.
- Docker Compose validates with `docker compose config --quiet`.
- README instructions are still accurate.
- No real credentials are committed.
- Generated files are not included.

## Code Style

- Use type hints.
- Use docstrings for public functions.
- Prefer small functions over large blocks.
- Use clear exception messages.
- Follow the existing modular folder structure.
