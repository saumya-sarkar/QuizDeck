# QuizDeck — Backend

REST API service for QuizDeck, built with **Flask** + **Flask-RESTful** + **Flask-Security**, backed by **SQLAlchemy/SQLite**, with **Celery + Redis** for background and scheduled work.

> For the full application (frontend + backend + infra) setup walkthrough, see the [root README](../README.md). This document covers the backend in detail: configuration, running it standalone, scheduled tasks, and the API reference.

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Folder Structure](#2-folder-structure)
3. [Environment Variables](#3-environment-variables-backendenv)
4. [One-Time Setup](#4-one-time-setup)
5. [Running the Backend](#5-running-the-backend)
6. [Scheduled & Background Tasks (Celery)](#6-scheduled--background-tasks-celery)
7. [Authentication Model](#7-authentication-model)
8. [Data Model](#8-data-model-summary)
9. [API Reference](#9-api-reference)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Tech Stack

- **Flask 3 / Flask-RESTful** — all endpoints are registered as `Resource` classes and mounted under the `/api` prefix (see `app.py`)
- **Flask-Security** — authentication, role management (`admin`, `user`), token-based auth, with **Argon2** for secure password hashing
- **Flask-SQLAlchemy** — ORM; SQLite by default (`sqlite:///quiz_db.sqlite3`), swappable via `SQLALCHEMY_DATABASE_URI`
- **Flask-CORS** — allows the Vue dev server (a different origin/port) to call the API
- **Flask-Caching** — Redis-backed cache, used for admin dashboard stats and a user's cached attempt list
- **Celery 5 + Redis** — async tasks (CSV export, quiz auto lock/unlock) and Celery Beat for recurring jobs (monthly report, daily reminder)
- **Jinja2** — renders the HTML monthly-report email
- **MailHog** — local fake-SMTP server for development so no real email provider is required

## 2. Folder Structure

```
backend/
├── app.py                  # create_app(), Celery init, API resource registration, Beat schedule
├── models.py                 # SQLAlchemy models + IST datetime helpers
├── config_file.py              # Config classes (env-driven, via python-dotenv)
├── celery_init.py                # Wires Celery tasks into the Flask app context
├── celery_config.py               # broker_url / result_backend / timezone
├── caching.py                      # Flask-Caching instance
├── mail.py                          # SMTP sender (points at MailHog by default)
├── utils.py                          # Jinja2 report-template renderer
├── tasks.py                           # All Celery tasks
├── init_db.py                          # create_all() + seed roles + seed default admin
├── requirements.txt
├── routes/
│   ├── user.py                          # register / login / user-details / username & email checks
│   ├── subject.py                        # Subject CRUD (multipart, cover image upload)
│   ├── chapter.py                         # Chapter CRUD
│   ├── quiz.py                             # Quiz CRUD + scheduling/locking logic
│   ├── question.py                          # Question + Option CRUD
│   ├── option.py
│   ├── user_quiz.py                          # Start / save-answer / submit / result (quiz-taking flow)
│   ├── user_attempts.py                       # Cached list of a user's completed attempts
│   ├── admin_users.py                          # Admin user management + dashboard stats
│   ├── analytics.py                             # Admin & user analytics aggregation
│   └── csv_export.py                             # Async CSV export (generate / status / download)
├── templates/
│   └── mail_template_css.html                     # Monthly report email template
└── static/
    ├── uploads/                                     # Uploaded subject cover images
    └── csv_exports/                                   # Generated CSV export files
```

## 3. Environment Variables (`backend/.env`)

Configuration is loaded from environment variables via `python-dotenv` in `config_file.py`. Create a `.env` file inside `backend/`:

```dotenv
# .env

# General
DEBUG=True
SECRET_KEY=super secret key
SECURITY_PASSWORD_SALT=super password salt
SECURITY_TRACKABLE=True
SECURITY_LOGIN_URL=/not_required
SECURITY_TOKEN_AUTHENTICATION_HEADER=Authorization

# Uploads
UPLOAD_FOLDER=static/uploads
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif

# Database
# For localDev:
SQLALCHEMY_DATABASE_URI=sqlite:///quiz_db.sqlite3

# For Deployment (override this when deploying):
# SQLALCHEMY_DATABASE_URI=sqlite:///site.sqlite3
```

> **Important:** `SECURITY_TOKEN_AUTHENTICATION_HEADER` must be `Authorization` — the Vue frontend sends the login token back in that exact header (`Authorization: <token>`) on every authenticated request.
>
> `SECRET_KEY` and `SECURITY_PASSWORD_SALT` just need to be non-empty strings for local development (use long random values for anything beyond local testing). `SECURITY_LOGIN_URL` is effectively unused — the app defines its own `/api/login` endpoint in `routes/user.py` rather than using Flask-Security's built-in login view, so any placeholder value works.
>
> `config_file.py` also defines a `Deployment` config class that reads `SQLALCHEMY_DATABASE_URI` with a different default (`sqlite:///site.sqlite3`) — set `SQLALCHEMY_DATABASE_URI` explicitly if you deploy this beyond local dev.

Redis connections are configured separately:
- **Celery** broker/result backend — `celery_config.py` (`redis://localhost:6379/0` and `/1`)
- **Flask-Caching** — `config_file.py` (`CACHE_REDIS_HOST/PORT/DB`, DB `2`)

Edit those two files directly if your Redis instance isn't on `localhost:6379`.

## 4. One-Time Setup

```bash
cd backend
python3 -m venv env
source env/bin/activate          # Windows: env\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` as described above, then initialize the database:

```bash
python init_db.py
```

`init_db.py` will:
1. Run `db.create_all()` to create every table defined in `models.py`
2. Create the `admin` and `user` roles
3. Create a default admin user: **`admin@quizdeck.com` / `admin`** (skipped if it already exists)
4. Create the `static/uploads` upload folder if missing

## 5. Running the Backend

The backend needs **five processes** running at the same time. Run each from `backend/`, with the virtual environment activated (except Redis/MailHog, which are standalone binaries).

| Process | Command | Notes |
|---|---|---|
| Redis | `redis-server` | Required by both Celery and Flask-Caching. Delete a stale `dump.rdb` in `backend/` if it fails to boot after a Redis version change. |
| MailHog | `mailhog` | SMTP on `localhost:1025`; web inbox at `http://localhost:8025` |
| Celery worker | `celery -A app.celery worker --loglevel=info` | Executes CSV export, quiz lock/unlock, and report/reminder tasks |
| Celery Beat | `celery -A app.celery beat --loglevel=info` | Triggers the two scheduled tasks below on their cron schedule |
| Flask API | `python app.py` | Serves the REST API at `http://localhost:5000/api` |

On Windows, running Redis/Celery inside WSL/Ubuntu is the smoothest path; alternatively add `-P solo` to the Celery worker command.

## 6. Scheduled & Background Tasks (Celery)

Beat schedule, configured in `app.py`:

| Task | Schedule | Description |
|---|---|---|
| `monthly_report` | 19:00 IST on the 1st of every month | Emails every registered user a performance summary for the past 30 days, rendered from `templates/mail_template_css.html` and sent through MailHog/SMTP |
| `daily_reminder` | 19:30 IST, every day | Posts a message listing each user's un-attempted quizzes to a configured Google Chat webhook |

On-demand tasks (`tasks.py`), triggered by API calls rather than the schedule:

| Task | Triggered by | Description |
|---|---|---|
| `generate_admin_report` | `POST /csv-export/generate` | Builds the requested CSV (all quiz attempts, `last_30_days` or `all_time`) and writes it to `static/csv_exports/` |
| `unlock_quiz_task` | Quiz create/update (Mock/Exam) | Scheduled via `apply_async(eta=start_time)` to flip `is_locked = False` exactly when the quiz opens |
| `lock_quiz_task` | Quiz create/update (Mock/Exam) | Scheduled via `apply_async(eta=end_time)` to flip `is_locked = True` exactly when the quiz closes |

## 7. Authentication Model

- Registration and login are handled by **custom** resources in `routes/user.py` (not Flask-Security's default views), using `flask_security.hash_password` / `verify_password` under the hood — passwords are hashed with **Argon2**, the algorithm Flask-Security recommends.
- A successful `POST /login` returns an `authToken`; the frontend stores it in `sessionStorage` and sends it back as the `Authorization` header on every subsequent request.
- Protected endpoints use `@auth_required('token')`; admin-only endpoints add `@roles_accepted('admin')`.
- Two roles exist out of the box: `admin` and `user` (seeded by `init_db.py`).

## 8. Data Model (summary)

```
User ⟷ Role   (many-to-many via roles_users)
Subject → Chapter → Quiz → Question → Option
QuizAttempt  (User × Quiz)  →  UserAnswer  (per Question, per attempt)
```

`Subject`, `Chapter`, `Quiz`, and `Question` all support **soft delete** via a `deleted` boolean flag (plus `created_at`/`updated_at` audit columns), with dedicated restore/list-deleted endpoints so nothing is destructively removed until an admin explicitly hard-deletes it.

`Quiz` additionally carries `is_locked_by_celery` and `is_unlocked_by_celery` flags, which let an admin distinguish a quiz that Celery automatically locked/unlocked (via the scheduled `lock_quiz_task`/`unlock_quiz_task`) from one whose `is_locked` state was never touched by a background job.

`Option` is kept in its own table (rather than embedded in `Question`) to keep the schema normalized, and `UserAnswer` records one row per question per attempt, linking a `QuizAttempt` to the `Option` the user selected.

## 9. API Reference

Base URL: `http://localhost:5000/api`
Auth column: `–` = public, `token` = any logged-in user, `admin` = admin role required.

### Auth & Account
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | – | Register a new user |
| POST | `/login` | – | Log in; returns `authToken` |
| GET | `/qualifications` | – | List qualification enum options |
| POST | `/check-username` | – | Check if a username is available |
| POST | `/check-email` | – | Check if an email is available |
| GET | `/user-details` | token | Current logged-in user's profile |

### Subjects
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/subject` | token | List all subjects |
| POST | `/subject` | token | Get one subject with its chapters |
| POST | `/subject/update` | admin | Create a subject (multipart form, optional cover image) |
| PUT | `/subject/update` | admin | Update a subject |
| PATCH | `/subject/delete` | admin | Soft-delete a subject |
| DELETE | `/subject/delete` | admin | Permanently delete a subject (and its cover image) |
| GET | `/subject/delete` | admin | List soft-deleted subjects |
| POST | `/subject/delete` | admin | Restore a soft-deleted subject |

### Chapters
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/chapter` | token | List all chapters |
| POST | `/chapter` | token | Get one chapter with its quizzes |
| POST | `/chapter/update` | admin | Create a chapter |
| PUT | `/chapter/update` | admin | Update a chapter |
| PATCH / DELETE / GET / POST | `/chapter/delete` | admin | Soft-delete / hard-delete / list-deleted / restore |

### Quizzes
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/quiz` | token | List all quizzes |
| POST | `/quiz` | admin | Get one quiz with its questions |
| POST | `/quiz/update` | admin | Create a quiz — validates scheduling rules per `quiz_type` (Practice / Mock / Exam) |
| PUT | `/quiz/update` | admin | Update a quiz |
| PATCH / DELETE / GET / POST | `/quiz/delete` | admin | Soft-delete / hard-delete / list-deleted / restore |

### Questions
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/question` | token | Get a single question by id |
| POST | `/question/update` | admin | Create a question with its options (exactly one marked correct) |
| PUT | `/question/update` | admin | Update a question and diff/patch its options |
| PATCH / DELETE / GET / POST | `/question/delete` | admin | Soft-delete / hard-delete / list-deleted / restore |

### Taking a Quiz (user flow)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/quiz/start` | token | Start a new attempt, or resume an existing in-progress one |
| POST | `/quiz/data` | token | Get quiz questions plus any previously saved answers |
| POST | `/quiz/save-answer` | token | Autosave a single answer while the quiz is in progress |
| POST | `/quiz/submit` | token | Submit (or auto-submit) an attempt; scores it and returns the summary |
| POST | `/quiz/result` | token | Full question-by-question result for a completed attempt |

### Attempts, Users & Dashboards
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/user/quiz-attempts` | token | A user's completed attempts (cached in Redis for 7 days, invalidated on new activity) |
| GET | `/admin/users` | admin | List all users with attempt/score stats |
| POST | `/admin/users/details` | admin | One user's detailed stats + subject-wise performance |
| PATCH | `/admin/users/toggle-status` | admin | Activate/deactivate a user account |
| GET | `/admin/dashboard/stats` | admin | Totals for the admin dashboard (cached 30s) |
| GET | `/user/dashboard/stats` | token | Totals for a user's dashboard |

### Analytics
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/admin/analytics` | admin | Attempts by user, attempts by subject, average score by difficulty, daily activity |
| GET | `/user/analytics` | token | Subject performance, last-4-weeks activity, score distribution, last-10-attempts trend |

### CSV Export
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/csv-export/generate` | admin | Start an async CSV export job. Body: `{ "period": "last_30_days" \| "all_time" }` |
| POST | `/csv-export/status` | admin | Poll a job's status by `task_id` |
| GET | `/csv-export/download/<task_id>` | – | Download the finished CSV file |

## 10. Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError` on startup | Activate the venv and re-run `pip install -r requirements.txt` |
| App crashes on boot with a Flask-Security config error | A required `.env` variable (`SECRET_KEY`, `SECURITY_PASSWORD_SALT`, etc.) is missing |
| Every request returns 401, even right after login | Confirm `SECURITY_TOKEN_AUTHENTICATION_HEADER=Authorization` in `.env`, and that the token from `/login` is being sent back unmodified |
| Celery tasks never execute | Confirm Redis is running on `localhost:6379` and that **both** the worker and beat processes are running |
| Report emails never appear | Confirm MailHog is running and check its inbox at `http://localhost:8025` — no email actually leaves your machine in dev |
| Quiz doesn't unlock/lock at the scheduled time | Confirm the Celery worker was already running *when the quiz was created/edited* — the unlock/lock job is scheduled at that moment via `apply_async(eta=...)` |
