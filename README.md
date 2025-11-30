# Form Submission Application

A simple Flask web app that collects user information (name, email, favourite colour) and saves it to PostgreSQL. Designed to run on Google Cloud Run.

**Live URL:** [To be added after deployment]

## What You Need

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Docker or Podman - Container runtime for local development (docker used by default)
- Google Cloud account (for deployment)

## Running Locally

### Quick Start

```bash
# Clone and install
git clone <repository-url>
cd form-app
uv sync

# Set up environment
cp .env.example .env

# Start database
make db-up

# Run the app
make dev
```

Visit <http://localhost:8080>

The defaults in `.env.example` work fine for local development. Only change them if you need different database settings.

### Useful Commands

```bash
# Development
make dev         # Start app with hot reloading
make test        # Run all tests

# Containers (docker by default, or set CONTAINER_RUNTIME=podman)
make build       # Build container image
make run         # Run containerized app
make stop        # Stop container

# Database
make db-up       # Start and init database
make db-down     # Stop and remove database
```

**Using Podman instead of Docker:**
```bash
# One-time per session
export CONTAINER_RUNTIME=podman

# Or per command
CONTAINER_RUNTIME=podman make build
```

## Deploying to Google Cloud

### 1. Set Up Your Google Cloud Project

```bash
# Create project
gcloud projects create MY-PROJECT-ID
gcloud config set project MY-PROJECT-ID

# Enable required services
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com
```

### 2. Create PostgreSQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create form-app-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=australia-southeast1

# Set password
gcloud sql users set-password postgres \
  --instance=form-app-db \
  --password=MY-SECURE-PASSWORD

# Create database
gcloud sql databases create formapp --instance=form-app-db
```

### 3. Initialize Database Schema

Connect to your database and run the schema file:

```bash
gcloud sql connect form-app-db --user=postgres
```

Then at the psql prompt:

```sql
\c formapp
\i db/schema.sql
\q
```

### 4. Deploy the Application

```bash
export CLOUD_SQL_CONNECTION_NAME=MY-PROJECT-ID:australia-southeast1:form-app-db
make deploy
```

After deployment finishes, you'll get a URL like `https://form-app-app-XXXX-XX.a.run.app`

**Note:** For production, use Google Secret Manager for sensitive values instead of environment variables.

## How It Works

The app follows a simple flow:

1. User fills out form at `/` -> submits to `/submit`
2. Backend validates input with Pydantic
3. If valid -> save to PostgreSQL -> redirect to `/result` with success message
4. If invalid -> redirect to `/result` with error message
5. User clicks "Back to form" link to submit another entry

### Code Layout

- `app/__init__.py` - Flask app setup
- `app/models.py` - Pydantic validation (email format, name rules, colour options)
- `app/routes.py` - Routes for form (`/`), submission (`/submit`), and result (`/result`)
- `app/database.py` - PostgreSQL connection and data insertion
- `app/templates/form.html` - HTML form with client-side validation
- `app/templates/result.html` - Success/error result page with link back to form
- `db/schema.sql` - Database table definition

The app automatically switches between local database (TCP) and Cloud Run (Unix socket) based on environment variables.

## Security

What's covered:

- SQL injection prevented (parameterized queries)
- Input validation on frontend and backend
- Container runs as non-root user
- Environment variables for secrets

What's not:

- CSRF protection (could add Flask-WTF for production)

Never commit your `.env` file - it contains passwords and secret keys.

## Expected Costs

Running this on Google Cloud costs about $15-20/month:

- Cloud SQL (db-f1-micro): ~$10-15/month
- Cloud Run: ~$1-5/month with light traffic

The configuration limits max instances to 5 to prevent unexpected scaling costs.

## Things That Could Be Better

These aren't required for the exercise but might be nice for a production app:

- **CSRF tokens** - Protect against cross-site attacks
- **Logging** - Better debugging in production
- **Type hints** - Better IDE support
- **Form preservation** - Keep user input when validation fails
- **Email uniqueness** - Prevent duplicate submissions (if needed)
