# Personal Expense Tracker API

A simple REST API for tracking personal expenses, built with **FastAPI** and **SQLModel**. No authentication, no multi-user support — just a straightforward single-user CRUD tool for logging expenses, filtering them, and viewing monthly summaries.

## Features

- Full CRUD for expenses (create, read, update, delete)
- Filter expenses by category and/or date range
- Monthly summary endpoint — total spend and a breakdown by category
- Auto-generated interactive API docs via Swagger UI (`/docs`)
- SQLite database, zero external setup required

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) — ORM + validation (combines SQLAlchemy and Pydantic)
- SQLite — database (built into Python, no separate install needed)
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

## Project Structure

```
expense-tracker/
├── main.py           # App, models, and all routes
├── requirements.txt  # Python dependencies
├── database.db        # SQLite database (created automatically, gitignored)
└── README.md
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/dhwanit-bodiwala/CRUD-Expense-Tracker-API.git
cd CRUD-Expense-Tracker-API
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`, and interactive docs at `http://127.0.0.1:8000/docs`.

> On first run, the app seeds two sample expenses automatically.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check / welcome message |
| GET | `/expenses` | List all expenses (supports filters below) |
| GET | `/expenses/{id}` | Get a single expense by ID |
| POST | `/expenses` | Create a new expense |
| PUT | `/expenses/{id}` | Update an existing expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/summary/monthly` | Get total and category breakdown for a given month |

### Filtering `GET /expenses`

Optional query parameters:
- `category` — filter by category name (e.g. `Food`)
- `start_date` — only include expenses on/after this date (ISO format, e.g. `2026-07-01T00:00:00`)
- `end_date` — only include expenses on/before this date

Example:
```
GET /expenses?category=Food&start_date=2026-07-01T00:00:00
```

### Monthly Summary `GET /summary/monthly`

Required query parameters:
- `year` — e.g. `2026`
- `month` — e.g. `7`

Optional:
- `category` — restrict the summary to a single category

Example request:
```
GET /summary/monthly?year=2026&month=7
```

Example response:
```json
{
  "total": 700,
  "by category": {
    "Food": 500,
    "Transport": 200
  }
}
```

### Creating an Expense `POST /expenses`

Request body:
```json
{
  "name": "Lunch",
  "amount": 250,
  "category": "Food",
  "desc": "Office lunch with team"
}
```

## Expense Model

| Field | Type | Notes |
|-------|------|-------|
| `product_id` | int | Auto-generated primary key |
| `name` | str | Required |
| `amount` | int | Defaults to 0 |
| `category` | str | Required |
| `desc` | str \| null | Optional |
| `date` | datetime | Auto-set to current UTC time on creation |

## Notes

- This is a learning project — first hands-on FastAPI build using SQLModel + SQLite.
- No authentication; intended for single-user / local use only.
- `database.db` is excluded from version control via `.gitignore` — a fresh one is created automatically on first run.

## Possible Next Steps

- Dedicated `Category` model instead of free-text strings
- Basic test suite with `pytest` + `httpx`
- Pagination on `GET /expenses`
