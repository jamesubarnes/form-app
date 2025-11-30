# Form Submission Application

A simple Flask web app that collects user information (name, email, favourite colour) and saves it to PostgreSQL. Designed to run on Google Cloud Run.

**Live URL:** [To be added after deployment]

## What You Need

- Python 3.12+
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
make local-db-up

# Run the app
make dev
```

Visit <http://localhost:8080>

The defaults in `.env.example` work fine for local development. Only change them if you need different database settings.

### Useful Commands

```bash
# Development
make dev              # Start app with hot reloading
make test             # Run all tests
make build            # Build container image (verify it builds)

# Local Database
make local-db-up      # Start and init local PostgreSQL
make local-db-down    # Stop and remove local database
```

**Using Podman instead of Docker:**

```bash
# One-time per session
export CONTAINER_RUNTIME=podman

# Or per command
CONTAINER_RUNTIME=podman make build
```

## Deploying to Google Cloud

### Prerequisites

For this exercise, the Cloud SQL instance (`my-instance`) was created in the Google Cloud Console beforehand, and the postgres password was set and noted down.

In `cloudshell` set the project and enable the required services:

```bash
gcloud config set project actu-senior-dev-exercise

gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com
```

### Deployment Steps

**1. Create database and initialize schema:**

```bash
make gcloud-db-up

# Enter <POSTGRES-PASSWORD>
```

This will create the `formapp` database and run `db/schema.sql`.

**2. Deploy to Cloud Run:**

```bash
DB_PASSWORD=<POSTGRES-PASSWORD> SECRET_KEY=<MY-SECRET-KEY> make gcloud-deploy
```

Generate a secret key with: `python -c "import secrets; print(secrets.token_hex(32))"`

**3. Note the application URL:**

After deployment completes, Cloud Run will output a URL like:
`https://form-app-XXXX-uc.a.run.app`

### Configuration

The Makefile uses these known defaults:

```bash
GCP_PROJECT=actu-senior-dev-exercise
GCP_REGION=australia-southeast2
CLOUD_SQL_INSTANCE=my-instance
```

**Note:** For production, we should use Google Secret Manager for sensitive values instead of environment variables.

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

## Expected Costs

Running this on Google Cloud costs about $15-20/month:

- Cloud SQL (db-f1-micro): ~$10-15/month
- Cloud Run: ~$1-5/month with light traffic

The configuration limits max instances to 5 to prevent unexpected scaling costs.

## Things That Could Be Better

Improvements for a production app:

- **CSRF tokens** - Protect against cross-site attacks
- **Logging** - Better debugging in production
- **Email uniqueness** - Prevent duplicate submissions (if a requirement)
