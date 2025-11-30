.PHONY: help build dev run stop db-up db-down test deploy

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker image"
	@echo "  make dev         - Start application in development mode with hot reloading"
	@echo "  make run         - Run application container"
	@echo "  make stop        - Stop application container"
	@echo "  make db-up       - Start PostgreSQL container and initialize schema"
	@echo "  make db-down     - Stop and remove PostgreSQL container and volume"
	@echo "  make test        - Run unit tests"
	@echo "  make deploy      - Deploy to Google Cloud Run"

build:
	@echo "Building Docker image..."
	podman build -t form-app:latest .
	@echo "Build complete"

dev:
	@echo "Starting application in development mode with hot reloading..."
	FLASK_APP=app FLASK_DEBUG=1 uv run flask run --port 8080

run:
	@echo "Starting application..."
	podman run -d \
		--name form-app \
		-p 8080:8080 \
		--env-file .env \
		form-app:latest
	@echo "Application running on http://localhost:8080"

stop:
	@echo "Stopping application container..."
	podman stop form-app || true
	podman rm form-app || true

db-up:
	@echo "Starting PostgreSQL container..."
	podman run -d \
		--name form-app-db \
		-e POSTGRES_DB=formapp \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-p 5432:5432 \
		-v form-app-data:/var/lib/postgresql/data \
		postgres:16-alpine
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	@echo "PostgreSQL is running on localhost:5432"
	@echo "Initializing database schema..."
	podman exec -i form-app-db psql -U postgres -d formapp < db/schema.sql
	@echo "Database schema created successfully"

db-down:
	@echo "Removing PostgreSQL container and volume..."
	podman stop form-app-db || true
	podman rm form-app-db || true
	podman volume rm form-app-data || true
	@echo "Cleanup complete"

test:
	@echo "Running tests..."
	uv run pytest -v

deploy:
	@echo "Deploying to Google Cloud Run..."
	@if [ -z "$(CLOUD_SQL_CONNECTION_NAME)" ]; then \
		echo "Error: CLOUD_SQL_CONNECTION_NAME is not set"; \
		echo "Usage: CLOUD_SQL_CONNECTION_NAME=project:region:instance make deploy"; \
		exit 1; \
	fi
	@if [ -z "$(DB_PASSWORD)" ]; then \
		echo "Error: DB_PASSWORD is not set"; \
		echo "Usage: DB_PASSWORD=yourpassword make deploy"; \
		exit 1; \
	fi
	@if [ -z "$(SECRET_KEY)" ]; then \
		echo "Error: SECRET_KEY is not set"; \
		echo "Usage: SECRET_KEY=yoursecretkey make deploy"; \
		exit 1; \
	fi
	@echo "Building and deploying..."
	gcloud run deploy form-app \
		--source . \
		--platform managed \
		--region australia-southeast1 \
		--allow-unauthenticated \
		--set-env-vars="DB_NAME=$${DB_NAME:-formapp},DB_USER=$${DB_USER:-postgres},DB_PASSWORD=$${DB_PASSWORD},SECRET_KEY=$${SECRET_KEY},ENVIRONMENT=production" \
		--add-cloudsql-instances=$(CLOUD_SQL_CONNECTION_NAME) \
		--memory=256Mi \
		--cpu=1 \
		--max-instances=5 \
		--timeout=60
	@echo "Deployment complete"
	@echo "Note: For production, consider using Google Secret Manager instead of environment variables"
