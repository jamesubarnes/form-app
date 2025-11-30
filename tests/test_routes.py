"""
Unit tests for Flask routes.
Tests the route handlers with mocked database operations.
"""

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from app import create_app


@pytest.fixture
def app() -> Flask:
    """Create and configure a test Flask application"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask application"""
    return app.test_client()


class TestIndexRoute:
    """Test the GET / route"""

    def test_index_returns_200(self, client: FlaskClient) -> None:
        """Test that index route returns 200 status code"""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_renders_form(self, client: FlaskClient) -> None:
        """Test that index route renders the form template"""
        response = client.get("/")
        assert b"Submission Form" in response.data
        assert b"first_name" in response.data
        assert b"last_name" in response.data
        assert b"email" in response.data
        assert b"favourite_colour" in response.data


class TestResultRoute:
    """Test the GET /result route"""

    def test_result_returns_200(self, client: FlaskClient) -> None:
        """Test that result route returns 200 status code"""
        response = client.get("/result")
        assert response.status_code == 200

    def test_result_renders_template(self, client: FlaskClient) -> None:
        """Test that result route renders the result template"""
        response = client.get("/result")
        assert b"Submission Result" in response.data
        assert b"Back to form" in response.data

    def test_result_shows_flash_messages(self, client: FlaskClient) -> None:
        """Test that result page displays flash messages"""
        with client.session_transaction() as session:
            session["_flashes"] = [("success", "Test message")]

        response = client.get("/result")
        assert b"Test message" in response.data


class TestSubmitRouteValidData:
    """Test the POST /submit route with valid data"""

    def test_submit_valid_data_success(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test successful form submission with valid data"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.return_value = 123

        response = client.post(
            "/submit",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "favourite_colour": "red",
            },
            follow_redirects=True,
        )

        mock_insert_user.assert_called_once_with(
            "John", "Doe", "john.doe@example.com", "red"
        )
        assert response.status_code == 200
        assert b"User id: 123" in response.data

    def test_submit_redirects_to_result(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test that successful submission redirects to result page"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.return_value = 456

        response = client.post(
            "/submit",
            data={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "favourite_colour": "green",
            },
        )

        assert response.status_code == 302
        assert "/result" in response.location

    def test_submit_names_with_spaces(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test submission with names containing spaces"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.return_value = 789

        response = client.post(
            "/submit",
            data={
                "first_name": "Mary Jane",
                "last_name": "Van Der Berg",
                "email": "mary@example.com",
                "favourite_colour": "blue",
            },
        )

        assert response.status_code == 302
        mock_insert_user.assert_called_once_with(
            "Mary Jane", "Van Der Berg", "mary@example.com", "blue"
        )

    def test_submit_trims_whitespace(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test that whitespace is trimmed from names"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.return_value = 999

        response = client.post(
            "/submit",
            data={
                "first_name": "  John  ",
                "last_name": "  Doe  ",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
        )

        assert response.status_code == 302
        mock_insert_user.assert_called_once_with(
            "John", "Doe", "john@example.com", "red"
        )


class TestSubmitRouteInvalidData:
    """Test the POST /submit route with invalid data"""

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {
                "first_name": "",
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
            {
                "first_name": "John",
                "last_name": "",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "not-an-email",
                "favourite_colour": "red",
            },
            {
                "first_name": "John123",
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "yellow",
            },
        ],
    )
    def test_submit_invalid_data_shows_error(
        self, mocker: MockerFixture, client: FlaskClient, invalid_data: dict[str, str]
    ) -> None:
        """Test that invalid data triggers validation error"""
        mock_insert_user = mocker.patch("app.routes.insert_user")

        response = client.post("/submit", data=invalid_data, follow_redirects=True)

        mock_insert_user.assert_not_called()
        assert b"Validation error" in response.data


class TestSubmitRouteDatabaseErrors:
    """Test the POST /submit route with database errors"""

    def test_submit_database_error(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test that database errors are handled gracefully"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.side_effect = Exception("Database connection failed")

        response = client.post(
            "/submit",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Server error" in response.data

    def test_submit_database_error_redirects(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test that database errors redirect to result page"""
        mock_insert_user = mocker.patch("app.routes.insert_user")
        mock_insert_user.side_effect = Exception("Database error")

        response = client.post(
            "/submit",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
        )

        assert response.status_code == 302
        assert "/result" in response.location


class TestMissingFormFields:
    """Test behavior when form fields are missing"""

    def test_submit_missing_first_name(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test submission without first_name field"""
        mock_insert_user = mocker.patch("app.routes.insert_user")

        response = client.post(
            "/submit",
            data={
                "last_name": "Doe",
                "email": "john@example.com",
                "favourite_colour": "red",
            },
            follow_redirects=True,
        )

        mock_insert_user.assert_not_called()
        assert b"Validation error" in response.data

    def test_submit_missing_all_fields(
        self, mocker: MockerFixture, client: FlaskClient
    ) -> None:
        """Test submission with no data"""
        mock_insert_user = mocker.patch("app.routes.insert_user")

        response = client.post("/submit", data={}, follow_redirects=True)

        mock_insert_user.assert_not_called()
        assert b"Validation error" in response.data
