.PHONY: help build dev local-db-up local-db-down gcloud-db-up gcloud-db-down test gcloud-deploy

# Container runtime (docker or podman)
# Override with: CONTAINER_RUNTIME=podman make <target>
# Or set in your shell: export CONTAINER_RUNTIME=podman
CONTAINER_RUNTIME ?= docker

# GCP Configuration
GCP_PROJECT ?= actu-senior-dev-exercise
GCP_REGION ?= australia-southeast2
CLOUD_SQL_INSTANCE ?= my-instance

help:
	@echo "Available commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make build           - Build Docker image (verify image builds)"
	@echo "  make dev             - Start application in development mode with hot reloading"
	@echo "  make local-db-up     - Start local PostgreSQL container and initialize schema"
	@echo "  make local-db-down   - Stop and remove local PostgreSQL container and volume"
	@echo "  make test            - Run unit tests"
	@echo ""
	@echo "Google Cloud Deployment:"
	@echo "  make gcloud-db-up    - Create database and schema on Cloud SQL"
	@echo "  make gcloud-db-down  - Drop database from Cloud SQL (destructive!)"
	@echo "  make gcloud-deploy   - Deploy to Google Cloud Run"

build:
	@echo "Building Docker image..."
	$(CONTAINER_RUNTIME) build -t form-app:latest .
	@echo "Build complete"

dev:
	@echo "Starting application in development mode with hot reloading..."
	FLASK_APP=app FLASK_DEBUG=1 uv run flask run --port 8080

local-db-up:
	@echo "Starting local PostgreSQL container..."
	$(CONTAINER_RUNTIME) run -d \
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
	$(CONTAINER_RUNTIME) exec -i form-app-db psql -U postgres -d formapp < db/schema.sql
	@echo "Database schema created successfully"

local-db-down:
	@echo "Removing local PostgreSQL container and volume..."
	$(CONTAINER_RUNTIME) stop form-app-db || true
	$(CONTAINER_RUNTIME) rm form-app-db || true
	$(CONTAINER_RUNTIME) volume rm form-app-data || true
	@echo "Cleanup complete"

gcloud-db-up:
	@echo "Setting up Cloud SQL database..."
	@echo "Creating database 'formapp' on instance $(CLOUD_SQL_INSTANCE)..."
	@gcloud sql databases create formapp \
		--instance=$(CLOUD_SQL_INSTANCE) \
		--project=$(GCP_PROJECT) 2>/dev/null || echo "Database 'formapp' already exists, continuing..."
	@echo "Initializing database schema..."
	@echo "You will be prompted for the postgres user password..."
	@gcloud sql connect $(CLOUD_SQL_INSTANCE) \
		--user=postgres \
		--project=$(GCP_PROJECT) \
		--database=formapp < db/schema.sql
	@echo "Cloud SQL database setup complete"

gcloud-db-down:
	@echo "WARNING: This will permanently delete the 'formapp' database!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	@echo "Dropping database 'formapp' from Cloud SQL..."
	@gcloud sql databases delete formapp \
		--instance=$(CLOUD_SQL_INSTANCE) \
		--project=$(GCP_PROJECT)
	@echo "Database deleted"

test:
	@echo "Running tests..."
	uv run pytest -v

gcloud-deploy:
	@echo "Deploying to Google Cloud Run..."
	@if [ -z "$(DB_PASSWORD)" ]; then \
		echo "Error: DB_PASSWORD is not set"; \
		echo "Usage: DB_PASSWORD=yourpassword SECRET_KEY=yoursecretkey make gcloud-deploy"; \
		exit 1; \
	fi
	@if [ -z "$(SECRET_KEY)" ]; then \
		echo "Error: SECRET_KEY is not set"; \
		echo "Usage: DB_PASSWORD=yourpassword SECRET_KEY=yoursecretkey make gcloud-deploy"; \
		exit 1; \
	fi
	@echo "Building and deploying to $(GCP_REGION)..."
	gcloud run deploy form-app \
		--source . \
		--platform managed \
		--region $(GCP_REGION) \
		--project $(GCP_PROJECT) \
		--allow-unauthenticated \
		--set-env-vars="DB_NAME=$${DB_NAME:-formapp},DB_USER=$${DB_USER:-postgres},DB_PASSWORD=$${DB_PASSWORD},SECRET_KEY=$${SECRET_KEY},ENVIRONMENT=production,CLOUD_SQL_CONNECTION_NAME=$(GCP_PROJECT):$(GCP_REGION):$(CLOUD_SQL_INSTANCE)" \
		--add-cloudsql-instances=$(GCP_PROJECT):$(GCP_REGION):$(CLOUD_SQL_INSTANCE) \
		--memory=256Mi \
		--cpu=1 \
		--max-instances=5 \
		--timeout=60
	@echo "Deployment complete"
	@echo "Note: For production, consider using Google Secret Manager instead of environment variables"
