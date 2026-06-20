# SocialPulse — Social Media Analytics Platform

A full-stack social media analytics platform that aggregates Twitter and YouTube engagement data, surfaces AI-generated insights via Claude, and delivers real-time updates through WebSockets.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Django](https://img.shields.io/badge/Django-5.1-green) ![React](https://img.shields.io/badge/React-Vite-61DAFB) ![Celery](https://img.shields.io/badge/Celery-5.6-brightgreen) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **Multi-platform analytics** — connects to Twitter (X) and YouTube APIs to pull live engagement metrics
- **AI insights** — uses the Anthropic Claude API to generate natural-language summaries of your performance data
- **Real-time dashboard** — Django Channels + WebSockets push updates to the React frontend instantly
- **Automated data sync** — Celery Beat schedules periodic background tasks; no manual refresh needed
- **Smart alerts** — configurable rules that trigger notifications when engagement crosses thresholds
- **Auto-generated API docs** — drf-spectacular exposes a Swagger UI at `/api/schema/swagger-ui/`
- **Production-ready deploy** — ships with a `render.yaml` for one-click deploy on Render.com

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Django 5.1 + Django REST Framework |
| Database | PostgreSQL (via psycopg2) |
| Task queue | Celery 5.6 + Redis |
| Task scheduler | django-celery-beat (DB-backed cron) |
| Real-time | Django Channels (WebSockets) |
| AI | Anthropic Claude API |
| Frontend | React + Vite |
| Static serving | WhiteNoise |
| Production server | Gunicorn |
| Deployment | Render.com |

---

## Project Structure

```
social-analytics-app/
├── backend/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py         # Celery app init + autodiscover
├── analytics/            # Core app — models, views, tasks, consumers
│   ├── models.py         # SocialAccount, Post, Metric, AnalyticsSnapshot
│   ├── views.py          # DRF ViewSets
│   ├── serializers.py
│   ├── tasks.py          # Celery tasks for Twitter/YouTube data fetch
│   ├── consumers.py      # Django Channels WebSocket consumer
│   ├── urls.py
│   └── services/
│       ├── twitter.py    # Twitter API integration
│       ├── youtube.py    # YouTube Data API v3 integration
│       └── ai.py         # Claude API calls
├── alerts/               # Alert rules and notification logic
│   ├── models.py         # AlertRule, Notification
│   ├── views.py
│   └── urls.py
├── frontend/             # React + Vite app
│   ├── src/
│   └── package.json
├── staticfiles/          # collectstatic output (gitignored at runtime)
├── manage.py
├── requirements.txt
└── render.yaml           # Render.com deploy config
```

---

## How It Works

```
Celery Beat (scheduler)
    ↓  triggers every N minutes
Celery Worker
    ↓  runs fetch_twitter_metrics() / fetch_youtube_metrics()
External APIs (Twitter / YouTube)
    ↓  returns engagement data
Django ORM → PostgreSQL
    ↓
Django Channels → WebSocket push
    ↓
React dashboard → live chart update
    ↓  (user requests AI summary)
Claude API → insight text → stored + displayed
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### 1. Clone and install

```bash
git clone https://github.com/shatakshi-1404/social-analytics-app.git
cd social-analytics-app
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/socialpulse
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=your-anthropic-api-key
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
YOUTUBE_API_KEY=your-youtube-api-key
```

### 3. Run migrations and start Django

```bash
python manage.py migrate
python manage.py runserver
```

### 4. Start Celery worker (new terminal)

```bash
celery -A backend worker --loglevel=info
```

### 5. Start Celery Beat scheduler (new terminal)

```bash
celery -A backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 6. Start React dev server (new terminal)

```bash
cd frontend
npm install
npm run dev
```

The React app runs on `http://localhost:5173` and proxies API calls to Django on `http://localhost:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/accounts/` | List connected social accounts |
| POST | `/api/accounts/` | Connect a new account |
| GET | `/api/metrics/` | Fetch engagement metrics |
| GET | `/api/insights/` | Get AI-generated insights |
| GET | `/api/alerts/` | List alert rules |
| POST | `/api/alerts/` | Create an alert rule |
| GET | `/api/schema/swagger-ui/` | Interactive API docs |

WebSocket endpoint: `ws://<host>/ws/analytics/`

---

## Deployment on Render

This repo includes a `render.yaml` that provisions everything automatically:

- **Web service** — Django + React static (Gunicorn)
- **Worker** — Celery worker
- **Beat** — Celery scheduler
- **PostgreSQL** database
- **Redis** instance

To deploy:

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repo — Render reads `render.yaml` and creates all services
4. Add secret environment variables (`ANTHROPIC_API_KEY`, `TWITTER_BEARER_TOKEN`, `YOUTUBE_API_KEY`) in the Render dashboard

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key (auto-generated on Render) |
| `DEBUG` | Yes | Set to `False` in production |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `ANTHROPIC_API_KEY` | Yes | Claude API key from console.anthropic.com |
| `TWITTER_BEARER_TOKEN` | Yes | From Twitter Developer Portal |
| `YOUTUBE_API_KEY` | Yes | From Google Cloud Console |

---

## License

MIT
