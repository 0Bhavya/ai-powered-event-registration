# AI-Powered Event Registration System

Secure event registration with AI verification, payments, QR attendance, and analytics.

## Phase 1 Status

Current phase: **Project structure + FastAPI + animated landing page**

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** PostgreSQL (Phase 2+)

## Project Structure

```
ai-event-registration/
├── api/index.py          # Vercel entry point
├── app/
│   ├── main.py           # FastAPI application
│   └── config.py         # Settings
├── templates/            # Jinja2 HTML templates
├── static/               # CSS, JS, images
├── requirements.txt
├── .env.example
└── vercel.json
```

## Local Setup

### 1. Create virtual environment

```bash
cd ai-event-registration
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)

```bash
cp .env.example .env
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open in browser

- Landing page: http://localhost:8000
- Health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/api/docs

## Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project structure + FastAPI + landing page | ✅ Current |
| 2 | Database + models + migrations | Pending |
| 3 | Authentication | Pending |
| 4 | Event management | Pending |
| 5+ | Registration, fraud, payments, etc. | Pending |

## License

MIT
