# Qliqy WebAPI

![CI](https://github.com/QliqyService/webapi/actions/workflows/webapi-build.yml/badge.svg)
![Status](https://img.shields.io/badge/status-active%20development-b4492f)
![Access](https://img.shields.io/badge/access-closed%20beta-7e2f1b)

Core backend service for the Qliqy platform.

## Overview

`webapi` is the central application service of Qliqy. It exposes the main REST API used by the React frontend, stores and returns user-controlled contact forms, accepts public comments, and orchestrates downstream integrations such as QR generation, Telegram delivery, and mail delivery.

The service is built for a product model where a user can publish a public contact page without exposing personal contact data directly.

Typical scenarios include:

- private contact via QR code on a vehicle
- public “contact me” or “found/lost” pages
- event-specific or temporary contact channels
- comment collection with Telegram and email notifications

## Current Product Status

Public self-registration is intentionally disabled at this stage.

The team is currently using a controlled access model to validate the interface, public flow, QR logic, and notification delivery before opening the product to general users.

For testing, the following account can be used:

```json
{
  "email": "admin@admin.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "admin123"
}
```

## Technology Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- RabbitMQ
- MinIO
- Gunicorn / Uvicorn

## Architecture Summary

`webapi` is the system's orchestration backend. It is the only service that understands the full business flow from authenticated user management to public comment delivery.

At a high level:

- the React frontend calls `webapi` for all dashboard and public-form data
- `webapi` validates and persists state in PostgreSQL
- binary assets such as avatars are stored through object storage
- asynchronous side effects are delegated through RabbitMQ
- dedicated workers consume those events for QR generation, Telegram delivery, and email delivery

This separation keeps the main API focused on business logic while long-running or external integrations are handled by specialized workers.

## Responsibilities

`webapi` is responsible for:

- authentication-facing API integration with the auth service
- user profile access and updates
- form CRUD operations
- QR code orchestration
- public form retrieval
- public comment submission
- comment retrieval for owners
- notification event publishing to Telegram and Mailer workers

`webapi` is not responsible for:

- rendering the main user interface
- direct Telegram bot interaction
- direct SMTP delivery
- direct QR image generation

Those concerns are intentionally delegated to other services.

## API Base

Production base URL:

```text
https://qliqy.org/api/v1
```

Documentation:

- Swagger UI: `https://qliqy.org/api/docs`
- ReDoc: `https://qliqy.org/api/redoc`
- OpenAPI JSON: `https://qliqy.org/api/openapi.json`

## Authentication Model

Protected endpoints require a bearer token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Access tokens are obtained through:

```http
POST /api/v1/auth/login
```

with `application/x-www-form-urlencoded` payload:

```text
username=admin@admin.com
password=admin123
```

Example response:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

In practical terms:

- public endpoints do not require authentication
- dashboard endpoints require a valid bearer token
- identity is delegated to the `auth` service
- `webapi` uses the authenticated user context to resolve ownership, permissions, and notification targets

## Core Domain Objects

The API is built around a small set of domain entities:

### User

Represents the authenticated account owner. A user can manage profile settings, upload an avatar, own multiple forms, and configure notification preferences.

Important fields include:

- `email`
- `first_name`
- `last_name`
- `phone`
- `notify_email_enabled`
- `notify_email`
- `tg_account`
- `tg_username`
- `tg_notify_enabled`

### Form

Represents a public contact surface owned by a user.

Important fields include:

- `id`
- `title`
- `description`
- `is_enabled`
- `qrcode`
- `user_id`

Each form can be exposed through a public React route and through a public API endpoint.

### Comment

Represents an inbound public message left on a form.

Important fields include:

- `id`
- `first_name`
- `last_name`
- `title`
- `description`
- `phone`
- `created_at`
- `form_id`

Comments are written publicly, but read and managed by the form owner through authenticated endpoints.

## Endpoint Groups

### Shared

- `GET /shared/healthcheck`

Example:

```bash
curl https://qliqy.org/api/v1/shared/healthcheck
```

Example response:

```json
{
  "msg": "OK",
  "release": "not-set"
}
```

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/request_verify_token`
- `POST /auth/verify_token`
- `POST /auth/forgot_password`
- `POST /auth/reset_password`

Example login:

```bash
curl -X POST https://qliqy.org/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@admin.com&password=admin123"
```

Additional authentication flows cover:

- account registration endpoint support
- email verification token request and confirmation
- forgot-password initiation
- password reset completion
- logout

### Users

- `GET /user/me`
- `PATCH /user/me`
- `GET /user/my_code`
- `POST /user/me/avatar`
- `GET /user/me/avatar`

Example:

```bash
curl https://qliqy.org/api/v1/user/me \
  -H "Authorization: Bearer <access_token>"
```

Example response:

```json
{
  "id": "73f95129-1fcd-43d9-821d-00ce650b4624",
  "email": "admin@admin.com",
  "phone": null,
  "first_name": "John",
  "last_name": "Doe",
  "tg_account": "123456789",
  "tg_username": "ernestothoughtsbot_user",
  "tg_notify_enabled": true,
  "notify_email_enabled": true,
  "notify_email": "admin@admin.com"
}
```

Example profile update:

```bash
curl -X PATCH https://qliqy.org/api/v1/user/me \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "notify_email_enabled": true,
    "notify_email": "admin@admin.com",
    "tg_notify_enabled": true
  }'
```

The user profile area is also where Telegram linking state and notification preferences are surfaced to the frontend.

### User Forms

- `POST /form/forms`
- `GET /form/forms`
- `GET /form/forms/all`
- `GET /form/forms/{form_id}`
- `PATCH /form/forms/{form_id}`
- `DELETE /form/forms/{form_id}`

Create form:

```bash
curl -X POST https://qliqy.org/api/v1/form/forms \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Parking Contact",
    "description": "Scan this page if my car blocks the exit."
  }'
```

Example response:

```json
{
  "id": "0aa0bd89-d4d3-40ad-be50-58ab88f65176",
  "title": "Parking Contact",
  "description": "Scan this page if my car blocks the exit.",
  "user_id": "73f95129-1fcd-43d9-821d-00ce650b4624",
  "is_enabled": true
}
```

Get form details:

```bash
curl https://qliqy.org/api/v1/form/forms/0aa0bd89-d4d3-40ad-be50-58ab88f65176 \
  -H "Authorization: Bearer <access_token>"
```

List forms returns QR data in base64 form through the `qrcode` field.

Typical usage:

- create a form from the dashboard
- receive a generated QR image
- publish or print the public form URL
- collect comments through the public page
- receive notifications through email and Telegram

### Public Form Access

- `GET /public/{form_id}`
- `GET /public/{form_id}/qrcode`

These endpoints are intentionally public and are used by the React frontend public page.

Example:

```bash
curl https://qliqy.org/api/v1/public/0aa0bd89-d4d3-40ad-be50-58ab88f65176
```

Example response:

```json
{
  "id": "0aa0bd89-d4d3-40ad-be50-58ab88f65176",
  "title": "Parking Contact",
  "description": "Scan this page if my car blocks the exit.",
  "is_enabled": true,
  "qrcode": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

These endpoints are consumed by the React public page at:

```text
https://qliqy.org/public/forms/{form_id}
```

Get QR image:

```bash
curl -L https://qliqy.org/api/v1/public/0aa0bd89-d4d3-40ad-be50-58ab88f65176/qrcode --output form.png
```

### Comments

- `POST /comments/forms/{form_id}/comments`
- `GET /comments/forms/{form_id}/comments`
- `GET /comments/comments/{comment_id}`
- `PATCH /comments/comment/{comment_id}`
- `DELETE /comments/comment/{comment_id}`

Public comment creation:

```bash
curl -X POST https://qliqy.org/api/v1/comments/forms/0aa0bd89-d4d3-40ad-be50-58ab88f65176/comments \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alex",
    "last_name": "Martin",
    "title": "Your car blocks the gate",
    "description": "Please move it when you can.",
    "phone": 15551234567
  }'
```

Example response:

```json
{
  "id": "9f3b6c77-98a9-4b08-bf25-27d89ed4a146",
  "title": "Your car blocks the gate",
  "description": "Please move it when you can.",
  "first_name": "Alex",
  "last_name": "Martin",
  "phone": 15551234567
}
```

From the product perspective, this is the main public conversion event in the system.

## Request Lifecycle

The typical request lifecycle for the core product flow is:

1. An authenticated user creates a form through the frontend.
2. `webapi` stores the form in PostgreSQL.
3. `webapi` requests QR generation through RabbitMQ.
4. The QR worker returns image data.
5. `webapi` stores and exposes that QR through the API.
6. A public visitor opens the React public page.
7. The frontend fetches form data from `GET /api/v1/public/{form_id}`.
8. The visitor submits a comment.
9. `webapi` stores the comment and publishes notification events.
10. Telegram and/or Mailer workers deliver outbound notifications depending on user settings.

## Error Handling

The API follows standard FastAPI / REST patterns:

- `200 OK` for successful reads and updates
- `201 Created` for successful resource creation
- `400 Bad Request` for invalid business input
- `401 Unauthorized` for missing or invalid auth
- `403 Forbidden` for ownership or permission violations
- `404 Not Found` for missing resources
- `422 Unprocessable Entity` for schema validation errors
- `500 Internal Server Error` for unexpected backend failures

Typical error response:

```json
{
  "detail": "Not Found"
}
```

Validation failures usually return a structured `detail` array generated by FastAPI / Pydantic.

## Service Integration

`webapi` is the orchestration layer of the system.

It integrates with:

- `auth` for identity and token-related operations
- `frontend` as the primary UI consumer
- `qrcode_generator` through RabbitMQ for QR creation
- `telegram` through RabbitMQ for Telegram notifications
- `mailer` through RabbitMQ for email notifications
- PostgreSQL for persistence
- MinIO for avatar storage

## Notification Flow

When a public comment is created:

1. `webapi` stores the comment.
2. It resolves the form owner.
3. It checks notification settings.
4. It publishes an event to:
   - Telegram worker if Telegram is linked and enabled
   - Mailer worker if email notifications are enabled

This means notification delivery is preference-aware and channel-specific rather than globally hardcoded.

## Storage and Infrastructure Dependencies

`webapi` expects the following infrastructure to exist:

- PostgreSQL for relational persistence
- RabbitMQ for asynchronous integration
- MinIO or compatible object storage for avatar assets
- Auth service for identity and token workflows

In production, the service is typically run behind Traefik or another reverse proxy and exposed under `/api`.

## Local Development

Typical local run depends on your environment setup, but the service is designed to run with PostgreSQL, RabbitMQ, and related infrastructure available.

At minimum, you should provide:

- database connection settings
- RabbitMQ connection settings
- auth service settings
- object storage settings

## Notes

- public signup is not yet part of the intended current product flow
- the current environment is optimized for internal testing and interface validation
- the test account above is the recommended entry point for demo and QA

- Developer: Ilia Fedorenko
- Developer: Ernest Berezin
