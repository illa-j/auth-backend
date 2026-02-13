# Auth Backend API

Auth Backend API is a Django REST Framework service for authentication and account management. It provides JWT-based auth, email verification, password change confirmation via email token, Google OAuth login flows, API throttling, OpenAPI documentation with drf-spectacular, and background task processing with Celery + Redis.

## Features

- **Custom User Model**: Email is used as the primary login identifier.
- **JWT Authentication**: Login, refresh, and token verification endpoints using Simple JWT.
- **Registration & Email Verification**:
  - Register users with inactive accounts.
  - Send verification email asynchronously.
  - Activate account via verification token endpoint.
- **Password Change Flow**:
  - Authenticated user requests password change.
  - Confirmation link is sent by email.
  - Password is updated only after token confirmation.
- **Profile Management**: Retrieve and update current authenticated user profile.
- **Google Authentication**:
  - Get Google authorization URL.
  - Exchange Google auth code for JWT tokens.
  - Authenticate directly with Google ID token.
- **API Documentation**: OpenAPI schema + Swagger UI + ReDoc via drf-spectacular.
- **Rate Limiting**: Scoped throttling for auth, refresh, and token verification routes.
- **Background Tasks**: Celery worker and Celery beat for email and cleanup tasks.
- **Docker Support**: Docker Compose setup for app, PostgreSQL, Redis, worker, and beat.

## Technologies Used

- **Framework**: [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Authentication**: [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- **Documentation**: [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- **Task Queue**: [Celery](https://docs.celeryq.dev/) & [Redis](https://redis.io/)
- **OAuth**: [google-auth](https://google-auth.readthedocs.io/) & [google-auth-oauthlib](https://google-auth-oauthlib.readthedocs.io/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Config**: [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation & Setup

### Using Docker (Recommended)

1. Copy env file:

	```bash
	cp .env.sample .env
	```

2.  Then edit `.env` and set the values for your environment.

3. Build and run:

	```bash
	docker compose up --build
	```

4. API base URL:
	- `http://127.0.0.1:8000/`

### Local Development

1. Create and activate venv:

	```bash
	python -m venv .venv
	source .venv/bin/activate
	```

2. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

3. Prepare environment:

	```bash
	cp .env.sample .env
	```

4. Run migrations:

	```bash
	python manage.py migrate
	```

5. Start API server:

	```bash
	python manage.py runserver
	```

6. Start Celery worker:

	```bash
	celery -A auth_backend worker -l info
	```

7. Start Celery beat (separate terminal):

	```bash
	celery -A auth_backend beat -l info
	```

## Environment Variables

Create `.env` from `.env.sample`:

```bash
cp .env.sample .env
```

Required keys:

```env
SECRET_KEY=<secret_key_here>

POSTGRES_DB=<database_name_here>
POSTGRES_USER=<database_user_here>
POSTGRES_PASSWORD=<database_password_here>
POSTGRES_HOST=<database_host_here>
POSTGRES_PORT=<database_port_here>

CELERY_BROKER_URL=<celery_broker_url_here>
CELERY_RESULT_BACKEND=<celery_result_backend_here>

EMAIL_HOST_USER=<email_host_user_here>
EMAIL_HOST_PASSWORD=<email_host_password_here>

GOOGLE_CLIENT_ID=<google_client_id_here>
GOOGLE_CLIENT_SECRET=<google_client_secret_here>
GOOGLE_REDIRECT_URI=<google_redirect_uri_here>

CORS_ALLOWED_ORIGIN=<cors_allowed_origin_here>
ALLOWED_HOST=<allowed_host_here>
```

## API Documentation

This project uses drf-spectacular:

- **OpenAPI schema**: `GET /api/schema/`
- **Swagger UI**: `GET /api/docs/`
- **ReDoc**: `GET /api/redoc/`

Local links:

- `http://127.0.0.1:8000/api/schema/`
- `http://127.0.0.1:8000/api/docs/`
- `http://127.0.0.1:8000/api/redoc/`

### Authorizing in Swagger

1. Obtain access token from `POST /auth/login/`.
2. Open Swagger UI and click **Authorize**.
3. Enter: `Bearer <access_token>`.

## Authentication Flow

1. Register: `POST /auth/register/`
2. Verify email: `GET /auth/verify-email/?token=<uuid>`
3. Login: `POST /auth/login/`
4. Refresh token: `POST /auth/token/refresh/`
5. Access protected endpoints using:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

Base auth prefix: `/auth/`

- `POST /auth/register/` — register user and send verification email
- `POST /auth/login/` — obtain access/refresh JWT pair
- `POST /auth/token/refresh/` — refresh access token
- `POST /auth/token/verify/` — verify token validity
- `GET /auth/me/` — get current user profile
- `PATCH /auth/me/` — update current user profile
- `POST /auth/logout/` — blacklist refresh token
- `GET /auth/verify-email/?token=<uuid>` — verify email
- `POST /auth/password-change/` — request password change confirmation email
- `GET /auth/confirm-password-change/?token=<uuid>` — confirm password change
- `GET /auth/google/url/` — get Google OAuth authorization URL
- `POST /auth/google/` — authenticate with Google authorization code
- `GET /auth/google/login/` — Google callback token exchange
- `POST /auth/google/token/` — authenticate with Google ID token

## Background Tasks

Celery tasks are defined in [core/tasks.py](core/tasks.py):

- Send verification email
- Send password-change confirmation email
- Cleanup expired tokens (scheduled by Celery beat)

To verify worker connectivity:

```bash
celery -A auth_backend inspect ping
```
