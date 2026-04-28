# HireTrackr

Web app for job search: tracking job applications, CV and motivation-letter tools, overview, and data collection from sent applications, with AI-based recommendations.

I'm building this project while learning full-stack basics with FastAPI + PostgreSQL.

## Project status
This project is still in progress and not finished yet.

## What it does

- User registration and login
- Input validation with toast messages
- Email verification
- CSRF protection
- CV workshop page (`CV Dílna`)
  - upload CV versions
  - preview PDF versions
  - delete versions
  - download versions
- Convert files to PDF (DOC/DOCX)

## Planned features

- **Dashboard insights**
  - Overall application progress
  - Follow-up rate, interview rate
- **CV tools**
  - CV scoring + recommendations (neural-network based)
  - CV groups for different job types / tailored versions
- **Motivation letter helper**
  - Job-posting URL scraper
  - Generate tailored motivation letter from posting details
- **Job tracking**
  - Central job-application database (what was sent, where, and when)
  - Real-time status tracking for each job offer
  - Company scoring based on collected review data (neural-network based)
- **Interview planning**
  - Notification schedules and reminders for upcoming interviews
- **Engineering improvements**
  - More automated tests
  - Better CI pipeline

## Tech stack

- **Language:** Python
- **Backend:** FastAPI
- **Templates:** Jinja2
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL + SQLAlchemy + Alembic
- **Storage:** Cloudflare R2 (S3 API)
- **Containerization:** Docker + Docker Compose
- **Database tools:** pgAdmin (Docker service, optional)

## How to run

- Clone the repo: git clone https://github.com/risandiro/hiretrackr.git && cd hiretrackr
- Copy env file: cp .env.example .env
- Fill values in .env (DB, SMTP, R2, secrets)
- Start app: docker compose up --build
- Run migrations: docker compose exec api alembic upgrade head
- Open app: http://localhost:8000

## External services (free tier / low-cost examples)

- **File storage:** [Cloudflare R2](https://developers.cloudflare.com/r2/)
- **DNS:** [Cloudflare DNS](https://developers.cloudflare.com/dns/)
- **SMTP:** [Resend](https://resend.com/docs/send-with-smtp)

## Project structure

```bash
.
├── app/
│   ├── routers/        # FastAPI endpoint handlers and backend logic for each route
│   ├── services/       # business and security services
│   ├── templates/      # Jinja HTML templates
│   ├── static/         # static files (CSS, JS)
│   ├── models.py       # SQLAlchemy models
│   ├── deps.py         # shared dependencies
│   └── main.py         # app bootstrap, middleware, static mount, router includes
├── alembic/            # DB migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example