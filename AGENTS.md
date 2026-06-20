# Inventory & Order Management System 

## Project Goal

Build a production-ready Inventory & Order Management System.

Tech Stack:

* Backend: FastAPI
* Frontend: React + Vite
* Database: PostgreSQL
* ORM: SQLAlchemy
* Validation: Pydantic
* Containerization: Docker
* Deployment: Render + Vercel

## Development Principles

* Write production-quality code.
* Favor readability over cleverness.
* Follow REST API conventions.
* Use dependency injection where appropriate.
* Avoid duplicated logic.
* Keep business logic inside service layer.
* API routers should remain thin.

## Backend Structure

backend/
app/
api/
models/
schemas/
services/
database/
core/

### Rules

* SQLAlchemy models only in models/
* Request/response DTOs only in schemas/
* Business logic only in services/
* Database session management in database/
* Environment configuration in core/

## Database Rules

Products:

* SKU must be unique
* Quantity cannot be negative

Customers:

* Email must be unique

Orders:

* Must validate stock before creation
* Must reduce inventory atomically
* Must calculate total server-side

## Error Handling

Always return meaningful HTTP errors.

Examples:

* 400 validation errors
* 404 resource not found
* 409 duplicate SKU/email
* 422 invalid request
* 500 unexpected failures

## Frontend Rules

Pages:

* Dashboard
* Products
* Customers
* Orders

Requirements:

* Responsive design
* Loading states
* Error states
* Form validation
* Reusable components

## Docker Requirements

Use:

* python:3.12-slim
* node:22-alpine
* postgres:16-alpine

Requirements:

* .dockerignore
* Environment variables
* Named volume for postgres

## Testing

Generate:

* Product API tests
* Customer API tests
* Order creation tests

## Deployment

Backend:

* Render

Frontend:

* Vercel

Database:

* Render PostgreSQL

## Code Quality

Before completing any task:

1. Verify imports.
2. Verify API routes.
3. Verify Docker build.
4. Verify docker-compose startup.
5. Verify frontend-backend integration.
6. Verify database migrations.

Never leave TODO comments in final code.
