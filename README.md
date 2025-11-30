# Form Submission Application

A simple Flask web app that collects user information (name, email, favourite colour) and saves it to PostgreSQL. Designed to be developed locally and deployed to Google Cloud Run. See [Requirements](REQUIREMENTS.md) for exercise details.

The final deployed application is at <https://form-app-334412769754.australia-southeast2.run.app>

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Docker or Podman - Container runtime for local development (docker used by default)
- Correctly configured Google Cloud account (for production deployment)

## Local Development

### Quick Start

```bash
# Clone and install
git clone https://github.com/jamesubarnes/form-app
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

For this exercise, the Cloud SQL instance (`my-instance`) was created in the Google Cloud Console beforehand, and a strong Postgres password was set and noted down.

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
DB_PASSWORD=<POSTGRES-PASSWORD> SECRET_KEY=<SECRET-KEY> make gcloud-deploy
```

Generate a secret key with: `python -c "import secrets; print(secrets.token_hex(32))"`

**3. Note the application URL:**

After deployment completes, Google Cloud Run will output the deployed application URL.  It should be something like:
`https://form-app-XXXX.australia-southeast2.run.app`

## Notes

### Scope Considerations

This stood out as key to me:

`You don’t need to use a framework like react, nor does it need to look pretty.`

So let's keep things simple for this exercise.

- Don't create a complex polyglot monorepo with a Typescript frontend SPA and Python backend server
- Use `flask` to serve a simple HTML server-rendered form and handle submission requests

Also there was no explicit requirement that email address be unique so that was not included in this solution for simplicity sake.  A more complete solution would of course and that include that unique constraint in the database schema and code.

### AI Usage

Claude Code was used in various capacities to help complete this exercise:

- The basic skeleton of the app code and infrastructure was cobbled together by hand initially from the official docs and prior experience.
- I use Claude Code a lot as a rubber duck during this phase because I know more or less what needs to be done and I prefer to bounce ideas off Claude and confirm against the official docs rather than let it drive the process at this point.
- I also use Claude Code for scaffolding tests, refining the solution and maintain documentation.
- I prefer using AI only for small focused snippets of functionality where I can heavily scrutinse the  output for correctness.

### Overview

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
- `tests/test_*.py` - Unit tests

### Database

As noted, in the Google Cloud console I first created a new PostgreSQL Sandbox instance with the following details:

```text
Choose a Cloud SQL edition: Enterprise
Edition preset: Sandbox

Database version: PostgreSQL 16
Instance ID: my-instance
Password: <strong password>
Region: australia-southeast2 (Melbourne)

Zonal availability: Single zone
Customise your instance: [reviewed and accepted defaults]
```

The app switches between connection methods based on the `ENVIRONMENT` variable:

- **Local development**: Connects via TCP to `localhost:5432`
- **Cloud Run (production)**: Connects via Unix socket at `/cloudsql/PROJECT:REGION:INSTANCE`

### Testing

As mentioned earlier, `make test` will run the unit test suite.

For the deployed application I submitted a number of test submissions.  Here's the resulting `psql` output on the Google Cloud SQL instance:

```text
formapp=> select * from users;
 id | first_name | last_name |          email           | favourite_colour |         created_at         
----+------------+-----------+--------------------------+------------------+----------------------------
  1 | James      | U         | james.u.barnes@gmail.com | red              | 2025-11-30 11:06:02.932079
  2 | Helen      | Barnes    | helenbarnes@gmail.com    | green            | 2025-11-30 11:06:22.324269
  3 | Curtis     | Barnes    | curtisbarnes@gmail.com   | blue             | 2025-11-30 11:06:42.312325
(3 rows)
```

## Some Improvements to Consider

- **Styling** - Add some CSS
- **CSRF tokens** - Protect against cross-site attacks
- **Logging** - Add log statements for better debugging
- **Email uniqueness** - Prevent duplicate submissions
- **Rate limiting** - Prevent abuse of the public endpoint
- **Secret Manager** - Use Google Secret Manager instead of environment variables for sensitive data
