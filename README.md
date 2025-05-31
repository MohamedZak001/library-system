
# Library System

A Django library management system with Celery task scheduling, using Poetry and Docker Compose.

---

## Features
- **Book Borrowing**: Users can borrow up to 3 books at a time, with a maximum 1-month return period. Returning one book is required to borrow a 4th.
- **Penalty Calculation**: Automatic penalties for overdue returns based on a configurable daily rate.
- **Email Notifications**: Sends confirmation emails upon borrowing and daily reminders for books due within 3 days.
- **User Management**: Supports user registration, login, and password recovery.
- **Real-time Updates**: Tracks book availability and borrowing status.
---

## Prerequisites

- Docker & Docker Compose
- Poetry (for local dev if not using Docker)
- `.env.example` file with your environment variables

---

## Quickstart with Docker Compose

The project includes a Docker Compose setup with the following services:

- `django`: Django app server
- `db`: PostgreSQL + PostGIS database
- `redis`: Redis broker for Celery
- `celery`: Celery worker
- `celery-beat`: Celery Beat scheduler
- `mailhog`: SMTP testing server

---

### Run the full stack

```bash
docker-compose up --build
```

This command will:

- Build and start all containers
- Mount your code into the Django container for live updates
- Run Django via `/app/run.sh`
- Start Celery workers and Beat scheduler with respective run scripts

---

### Access services

- Django API: [http://localhost:8000](http://localhost:8000)
- Mailhog UI (for emails): [http://localhost:8025](http://localhost:8025)
- PostgreSQL on port `5432`
- Redis on port `6379`

---

## ⏱ Periodic Tasks (via Celery Beat)

* `update_borrows`: Runs daily at **00:00 UTC**
* `send_daily_borrow_reminders`: Runs daily at **00:10 UTC**

---



## 📃 Swagger Documentation

Interactive API documentation is available at:

```
http://localhost:8000/api/docs/swagger/
```

---

## 🔐 Authentication

We use JWT. Add this to your request headers:

```
Authorization: Bearer <your_token>
```

Obtain token:

```bash
POST /api/token/
{
  "email": "email",
  "password": "password"
}
```

---

## 📬 Mailhog

Access Mailhog UI at:

```
http://localhost:8025
```

