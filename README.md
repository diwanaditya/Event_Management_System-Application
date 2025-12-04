# Event_Management_System-Application

A complete RESTful API built using Django and Django REST Framework for managing events, RSVPs, and reviews. This project demonstrates production-grade backend engineering practices including authentication, access control, asynchronous task processing, and structured testing.

**Developer:** Aditya Diwan
**GitHub:** [https://github.com/diwanaditya](https://github.com/diwanaditya)

---

## Table of Contents

* Features
* Technology Stack
* Installation
* API Documentation
* Project Structure
* Running Tests
* Celery Setup
* Contributing

---

## Features

### Core Functionality

* User management with extended profile fields such as bio, location, and profile picture
* Event creation, listing, updating, and deletion
* Public and private event access control
* RSVP system with status categories (Going, Maybe, Not Going)
* Review system with event ratings and comments

### Security and Authentication

* JWT authentication
* Custom permissions with strict access control
* Organizer-only event modification
* Restricted access for private events

### Additional Capabilities

* Pagination
* Search and filtering
* Asynchronous email notifications using Celery
* Comprehensive backend unit testing

---

## Technology Stack

* Python 3.8+
* Django 4.2.7
* Django REST Framework 3.14.0
* PostgreSQL or SQLite
* djangorestframework-simplejwt
* Celery 5.3.4
* Redis 5.0.1

---

## Installation

### Prerequisites

```
python --version  
pip --version
```

### Steps

1. Clone the repository

```
git clone https://github.com/diwanaditya/Event_Management_System-Application.git
cd Event_Management_System-Application
```

2. Create and activate virtual environment

Windows:

```
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Create `.env` file

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/0
```

5. Apply migrations

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Run development server

```
python manage.py runserver
```

---

## API Documentation

### Authentication

#### Register

```
POST /api/auth/register/
```

#### Login (JWT)

```
POST /api/auth/token/
```

#### Refresh Token

```
POST /api/auth/token/refresh/
```

---

### Event Endpoints

#### Create Event

```
POST /api/events/
```

#### List Events

```
GET /api/events/
```

#### Event Details

```
GET /api/events/{id}/
```

#### Update Event

```
PUT /api/events/{id}/
```

#### Delete Event

```
DELETE /api/events/{id}/
```

---

### RSVP Endpoints

```
POST /api/events/{event_id}/rsvp/
PATCH /api/events/{event_id}/rsvp/{user_id}/
```

---

### Review Endpoints

```
POST /api/events/{event_id}/reviews/
GET /api/events/{event_id}/reviews/
```

---

## Project Structure

```
event-management-system/
│
├── event_management/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
│
├── events/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── tasks.py
│   ├── urls.py
│   └── tests.py
│
├── media/
├── staticfiles/
├── .env
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## Running Tests

Run all tests:

```
python manage.py test
```

Run specific module:

```
python manage.py test events.tests
```

Run with coverage:

```
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## Celery Setup

Install Redis

macOS:

```
brew install redis
```

Ubuntu:

```
sudo apt-get install redis-server
```

Windows: download from redis.io

Start services:

Redis:

```
redis-server
```

Celery worker:

```
celery -A event_management worker -l info
```

Celery beat:

```
celery -A event_management beat -l info
```

Run Django:

```
python manage.py runserver
```

---

## Key Implementations

### Custom Permissions

* Event modification restricted to organizer
* Private events available only to organizer and invited users
* Users may update only their own RSVPs and reviews

### Validation

* Event end time must be after start time
* Unique RSVP per user per event
* Unique review per user per event
* Review rating between 1–5

---

## Troubleshooting

Check migrations:

```
python manage.py showmigrations
```

Token issues:
Use refresh tokens when access token expires.

Celery issues:
Confirm Redis is running and inspect worker logs.

---

## Sample Responses

### Success

```
{
  "id": 1,
  "title": "Django Workshop",
  "description": "Learn DRF",
  "location": "San Francisco",
  "is_public": true
}
```

### Error

```
{
  "detail": "You do not have permission to perform this action."
}
```

### Paginated Response

```
{
  "count": 10,
  "results": [...]
}
```

---

## Contributing

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Push to branch
5. Open pull request

---

## License

This project was created for assessment and educational purposes.

---

## Contact

Aditya Diwan
GitHub: [https://github.com/diwanaditya](https://github.com/diwanaditya)

---

## Assignment Checklist

* User Profile model
* Event model
* RSVP model
* Review model
* JWT Authentication
* Custom permissions
* Event CRUD
* RSVP handling
* Review handling
* Pagination
* Search and filtering
* Celery email tasks
* Unit tests
* Error handling
* Documentation

Just tell me.
