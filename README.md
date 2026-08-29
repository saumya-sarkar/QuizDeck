# QuizDeck

A full-stack online quiz / assessment platform with role-based access (Admin & User), scheduled quizzes (Practice / Mock / Exam), a timed quiz-taking experience with autosave and auto-submit, analytics dashboards, async CSV exports, and automated email/chat notifications powered by Celery.

**Frontend:** Vue 3 (Vue CLI, Vuex, Vue Router, Bootstrap 5, Chart.js)
**Backend:** Flask + Flask-RESTful + Flask-Security, SQLAlchemy, Celery + Redis, MailHog

📹 Demo video: [QuizDeck Demo Video.mp4](https://drive.google.com/file/d/1LdXRJwR3bZ8Og86vCuTwC-rsihx-DP57/view?usp=drive_link)

For backend-only setup and the full REST API reference, see [`backend/README.md`](backend/README.md).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Features](#2-key-features)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Prerequisites](#5-prerequisites)
6. [Full Setup Guide](#6-full-setup-guide)
7. [What Runs Where (Quick Reference)](#7-what-runs-where-quick-reference)
8. [Default Login](#8-default-login)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

QuizDeck lets an **Admin** build a content hierarchy — **Subjects → Chapters → Quizzes → Questions** — and lets **Users** browse that hierarchy and take quizzes, with results, history, and personal analytics tracked over time.

Quizzes come in three flavors:
- **Practice** — always available, no schedule.
- **Mock** — open between a configured start and end time.
- **Exam** — starts at a fixed time and runs for a fixed duration.

Mock/Exam quizzes are automatically locked and unlocked at the right moment by Celery background tasks, without anyone needing to refresh anything.

## 2. Key Features

### Admin
- Token-based authentication with role-based access control (Flask-Security)
- CRUD for Subjects (with cover-image upload), Chapters, Quizzes, and Questions — all with **soft delete + restore**
- Quiz scheduling for Mock/Exam quizzes, auto lock/unlock via Celery
- User management — view stats, activate/deactivate accounts, inspect any user's quiz attempts and results
- Admin analytics dashboard — attempts by user, attempts by subject, average score by difficulty, daily activity
- Async CSV export of all quiz attempts (last 30 days or all-time), generated in the background and downloaded once ready

### User
- Browse Subjects → Chapters → Quizzes
- Take a quiz with a live countdown timer, a question navigator, per-answer autosave, and automatic submission when time runs out
- Resume an in-progress attempt after a refresh/disconnect
- Detailed per-attempt results (score, percentage, question-by-question breakdown, explanations)
- Personal analytics — subject performance, weekly activity, score distribution, recent trends
- Full quiz-attempt history

### Platform
- Toast notifications, breadcrumb navigation, and search/filter on every list page
- Redis-backed caching for dashboard stats and attempt history
- Scheduled background jobs: a monthly performance-report email per user, and a daily reminder of un-attempted quizzes posted to a Google Chat webhook
- Robust validation on both the frontend (real-time field checks) and backend (`reqparse`-based parsing/validation on every write endpoint)
- Auto-refreshing quiz cards — when a scheduled quiz's unlock time arrives, the page automatically re-fetches so the **Start Quiz** button becomes available without a manual refresh
- Glassmorphic UI design throughout (frosted-glass cards, gradients, backdrop blur)

## 3. Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Vue 3 (Options API), Vue Router 4, Vuex 4, Axios, Bootstrap 5, Chart.js / vue-chartjs, FontAwesome, vue-toastification |
| Backend | Flask 3, Flask-RESTful, Flask-Security (with Argon2 password hashing), Flask-SQLAlchemy (SQLite by default), Flask-CORS, Flask-Caching |
| Async / Scheduling | Celery 5 + Redis (broker & result backend), Celery Beat |
| Email / Notifications | Jinja2 email templates, SMTP via MailHog (local dev), Google Chat webhook |

## 4. Project Structure

```
quiz_deck/
├── README.md                  # you are here
├── backend/                   # Flask REST API + Celery workers
│   ├── app.py                  # app factory, API routes, Celery Beat schedule
│   ├── models.py                # SQLAlchemy models
│   ├── config_file.py            # env-driven configuration
│   ├── celery_init.py / celery_config.py
│   ├── caching.py
│   ├── tasks.py                   # Celery tasks
│   ├── mail.py / utils.py
│   ├── init_db.py                  # DB bootstrap + seed admin
│   ├── requirements.txt
│   ├── routes/                      # Flask-RESTful resources
│   ├── templates/                    # email templates
│   ├── static/uploads/                # cover images
│   ├── static/csv_exports/             # generated CSV reports
│   └── README.md                        # backend-specific docs (this is the important one to read for setup)
└── frontend/                  # Vue 3 SPA
    ├── src/
    │   ├── views/Admin, views/User      # route-level pages
    │   ├── components/Admin, components/User  # UI components, modals, charts
    │   ├── router/                        # AdminRoutes.js, UserRoutes.js, index.js (auth guards)
    │   ├── store/modules/auth.js           # Vuex auth module
    │   └── config/apiConfig.js              # backend base URL
    └── public/
```

## 5. Prerequisites

| Tool | Why |
|---|---|
| Python 3.10+ | Runs the Flask backend |
| Node.js 16+ and npm | Runs the Vue frontend |
| Redis | Celery broker/result backend **and** Flask-Caching store |
| MailHog | Local fake-SMTP server that captures the monthly report emails |
| Git | To clone the repo |
| WSL / Ubuntu (Windows users) | Redis and Celery are simplest to run inside a Linux shell — the original project notes (`Steps.txt`) assume this setup |

## 6. Full Setup Guide

You'll end up running **6 long-lived processes** in parallel (one per terminal): Redis, MailHog, a Celery worker, Celery Beat, the Flask API, and the Vue dev server.

### Step 0 — Get the code
```bash
git clone <your-repo-url> quiz_deck
cd quiz_deck
```

### Step 1 — Backend virtual environment & dependencies
```bash
cd backend
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```
> If Redis fails to start later with a version/format error, delete any stale `dump.rdb` left in `backend/` from a previous Redis install: `rm -f dump.rdb`

### Step 2 — Configure environment variables
Create `backend/.env` (full variable list and explanations in [`backend/README.md`](backend/README.md)); at minimum:
```dotenv
SECRET_KEY=change-me
SECURITY_PASSWORD_SALT=change-me-too
SECURITY_LOGIN_URL=/not_required
SECURITY_TOKEN_AUTHENTICATION_HEADER=Authorization
```
> `SECURITY_LOGIN_URL` just has to be set to *something* — the app uses its own custom `/api/login` endpoint (see `routes/user.py`) rather than Flask-Security's built-in login view, so this value is effectively a placeholder.

### Step 3 — Initialize the database
Still in `backend/`, with the venv active:
```bash
python init_db.py
```
This creates all tables, the `admin`/`user` roles, the `static/uploads` folder, and a default admin account — see [Default Login](#8-default-login).

### Step 4 — Start Redis  *(Terminal A)*
```bash
redis-server
```

### Step 5 — Start MailHog  *(Terminal B)*
```bash
mailhog
```
Web inbox: **http://localhost:8025** (SMTP on port 1025, used by the monthly report task).

### Step 6 — Start the Celery worker  *(Terminal C)*
```bash
cd backend && source env/bin/activate
celery -A app.celery worker --loglevel=info
```

### Step 7 — Start Celery Beat  *(Terminal D)*
```bash
cd backend && source env/bin/activate
celery -A app.celery beat --loglevel=info
```

### Step 8 — Start the Flask API  *(Terminal E)*
```bash
cd backend && source env/bin/activate
python app.py
```
API base URL: **http://localhost:5000/api**

### Step 9 — Start the Vue frontend  *(Terminal F)*
```bash
cd frontend
npm install
npm run serve
```
App URL: **http://localhost:8080**

### Step 10 — Open the app
Go to **http://localhost:8080**, click **Sign In**, and log in with the default admin account (or register a new regular user via **Register**).

## 7. What Runs Where (Quick Reference)

| # | Process | From directory | Command | Purpose |
|---|---|---|---|---|
| 1 | Redis | anywhere | `redis-server` | Celery broker/backend + cache |
| 2 | MailHog | anywhere | `mailhog` | Local SMTP + web inbox at `:8025` |
| 3 | Celery worker | `backend/` | `celery -A app.celery worker --loglevel=info` | Runs background tasks |
| 4 | Celery Beat | `backend/` | `celery -A app.celery beat --loglevel=info` | Fires scheduled tasks |
| 5 | Flask API | `backend/` | `python app.py` | REST API on `:5000` |
| 6 | Vue dev server | `frontend/` | `npm run serve` | SPA on `:8080` |

## 8. Default Login

`init_db.py` seeds one admin account so you can log in immediately:

- **Email:** `admin@quizdeck.com`
- **Password:** `admin`

⚠️ Change this password (or replace the account) before using the app beyond local testing/demo purposes.

Regular users can self-register from the **Register** page in the app.

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| Redis won't start / crashes on boot | Delete `backend/dump.rdb` (leftover from a different Redis version) and retry |
| Celery worker won't start on Windows | Run it inside WSL/Ubuntu, or append `-P solo` to the worker command |
| Frontend can't reach the API / network errors | Confirm `python app.py` is running on port 5000, and that `frontend/src/config/apiConfig.js` still points at `http://localhost:5000/api` |
| Login fails right after setup | Confirm `python init_db.py` finished and printed "Admin created." — check that Redis/DB paths in `.env` are correct |
| CSV export stays "processing" forever | Make sure **both** the Celery worker and Celery Beat are running, and Redis is reachable |
| No report emails arrive | Check MailHog is running and open its inbox at `http://localhost:8025` — emails never leave your machine |

---

See [`backend/README.md`](backend/README.md) for backend architecture, environment variables, the full REST API reference, and the Celery scheduled-task details.

## 10. Project Context & Credits

QuizDeck was built by **Saumya Sarkar** (IIT Madras, BS in Data Science and Applications) as a Modern Application Development project. AI/LLM assistance was used only for CSS/aesthetic styling — all backend logic and application code were hand-written.

- 📄 Full project report (approach, DB schema/ER diagram, API design rationale): [QuizDeck_Report.pdf](https://drive.google.com/file/d/1ZEYat4Yavi0gmjxu7GNc26LKoBj8pb6d/view?usp=drive_link)
- 📹 Demo video: [QuizDeck Demo Video.mp4](https://drive.google.com/file/d/1LdXRJwR3bZ8Og86vCuTwC-rsihx-DP57/view?usp=drive_link) *(download it for the best viewing experience)*
