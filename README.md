# Ajali! Backend API

Emergency Incident Reporting System — Django REST API powering the Ajali! platform, where citizens can report accidents and emergencies to the appropriate authorities and the public.

## Tech Stack

- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- Cloudinary (media hosting for incident images/videos)
- Geopy / Nominatim (geocoding)
- drf-yasg (Swagger / ReDoc API docs)
- pytest + pytest-django + factory-boy (testing)

## Project Structure

```
ajali-web-app-backend/
├── ajali/                  # Project settings, root urls, wsgi/asgi
├── apps/
│   ├── users/               # Auth, registration, profile, password reset
│   ├── incidents/           # Incident CRUD, media, status history, geocoding
│   ├── admin_api/           # Admin dashboard, stats, moderation
│   └── notifications/       # In-app notifications, preferences
├── core/                    # Shared utilities (exceptions, pagination,
│                             #   validators, cloudinary/geocoding helpers)
├── templates/emails/         # Email templates
├── manage.py
├── requirements.txt
└── pytest.ini
```

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (SQLite works fine for local development)
- pip

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/keithkamau/ajali-web-app-backend.git
cd ajali-web-app-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Email
SENDGRID_API_KEY=

# Maps / notifications (as needed)
GOOGLE_MAPS_API_KEY=
AFRICASTALKING_API_KEY=
```

For a full PostgreSQL setup instead of SQLite, set:

```env
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB_NAME
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## API Documentation

Interactive API docs are available once the server is running:

- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## Key Endpoints

| Area | Base path |
|---|---|
| Auth | `/api/auth/` — register, login, logout, refresh, `/me/`, password reset |
| Incidents | `/api/incidents/` — CRUD, search, filter, media upload/delete, status history, geocoding |
| Admin | `/api/admin/` — incident moderation, stats, user management |
| Notifications | `/api/notifications/` — list, mark read, preferences |
| Health check | `/health/` |

## Running Tests

```bash
pytest
```

Run a single app's tests:

```bash
pytest apps/incidents/tests.py -v
```

## Contributors

- Keith Kamau
- Newton Mwangi
- Ian Kinoti
- John Kingoo