"""
Unit tests for database operations.
Tests database functions with mocked psycopg2 connections.
"""

from typing import Any

import pytest
from pytest_mock import MockerFixture

from app.database import DB_CONFIG, get_db_connection, insert_user


@pytest.fixture
def mock_db_connection(mocker: MockerFixture) -> tuple[Any, Any]:
    """Create a properly configured mock database connection with context managers"""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()

    # Setup context manager behavior
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.__exit__.return_value = None

    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("app.database.get_db_connection", return_value=mock_conn)

    return mock_conn, mock_cursor


class TestDatabaseConfiguration:
    """Test database configuration"""

    def test_db_config_has_required_keys(self) -> None:
        """Test that DB_CONFIG contains all required keys"""
        required_keys = ["dbname", "user", "password", "host", "port"]
        for key in required_keys:
            assert key in DB_CONFIG


class TestGetDbConnection:
    """Test the get_db_connection function"""

    def test_get_db_connection_calls_psycopg2(self, mocker: MockerFixture) -> None:
        """Test that get_db_connection calls psycopg2.connect"""
        mock_connect = mocker.patch("app.database.psycopg2.connect")
        mock_conn = mocker.MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_db_connection()

        mock_connect.assert_called_once_with(**DB_CONFIG)
        assert conn == mock_conn


class TestInsertUser:
    """Test the insert_user function"""

    def test_insert_user_success(self, mock_db_connection: tuple[Any, Any]) -> None:
        """Test successful user insertion"""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [42]

        user_id = insert_user("John", "Doe", "john@example.com", "red")

        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO users" in sql
        assert "RETURNING id" in sql
        assert "%s" in sql
        assert params == ("John", "Doe", "john@example.com", "red")
        mock_conn.commit.assert_called_once()
        assert user_id == 42

    def test_insert_user_sql_injection_safety(
        self, mock_db_connection: tuple[Any, Any]
    ) -> None:
        """Test that insert_user uses parameterized queries"""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [1]

        malicious_input = "'; DROP TABLE users; --"
        insert_user(malicious_input, "Doe", "john@example.com", "red")

        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "%s" in sql
        assert malicious_input in params
        assert "DROP TABLE" not in sql
