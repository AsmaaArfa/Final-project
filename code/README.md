# SQLAlchemy PostgreSQL CRUD Example

This project provides SQLAlchemy models and CRUD helpers for Patients, Dentists, Surgeries, Addresses, Appointments, Users and Roles, with a PostgreSQL backend.

Setup

1. Create a Python 3.10+ virtual environment and activate it.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` (e.g. `postgresql+psycopg2://user:pass@localhost:5432/dbname`).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

Run example:

```bash
# Run the FastAPI server (development)
python -m uvicorn code.main:app --reload
```

Quick API examples (replace host/port if different):

```bash
# List patients
curl http://127.0.0.1:8000/adsweb/api/v1/patients

# Obtain token (password grant form)
curl -X POST -F "username=asmith" -F "password=notreallyhashed" http://127.0.0.1:8000/adsweb/api/v1/auth/token
```

Files

- `database.py` - SQLAlchemy engine, session and Base
- `models.py` - ORM models and relationships
- `crud.py` - CRUD helper functions
- `main.py` - Example usage that creates tables and demonstrates CRUD
