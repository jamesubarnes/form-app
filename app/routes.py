from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from pydantic import ValidationError

from app.database import insert_user
from app.models import User

bp = Blueprint("main", __name__)


@bp.route("/")
def index() -> str:
    return render_template("form.html")


@bp.route("/result")
def result() -> str:
    return render_template("result.html")


@bp.route("/submit", methods=["POST"])
def submit() -> Response:
    try:
        # Validate form data using Pydantic
        user = User(
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            email=request.form.get("email", ""),
            favourite_colour=request.form.get("favourite_colour", ""),
        )

        # Insert into database
        user_id = insert_user(
            user.first_name, user.last_name, user.email, user.favourite_colour
        )

        flash(f"Form submitted successfully! User id: {user_id}", "success")
        return redirect(url_for("main.result"))

    except ValidationError as e:
        # Aggregate validation errors
        errors = []
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            errors.append(f"{field}: {message}")

        flash(f"Validation error(s): {'; '.join(errors)}", "error")
        return redirect(url_for("main.result"))

    except Exception as e:
        flash(f"Server error: {str(e)}", "error")
        return redirect(url_for("main.result"))
