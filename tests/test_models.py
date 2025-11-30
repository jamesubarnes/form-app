"""
Unit tests for Pydantic models and validation.
Tests the User model and Colour enum validation logic.
"""

import pytest
from pydantic import ValidationError

from app.models import Colour, User


class TestUserModelValidCases:
    """Test User model with valid input data"""

    def test_valid_user_all_fields(self) -> None:
        """Test creating a user with all valid fields"""
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            favourite_colour="red",
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.favourite_colour == Colour.RED

    @pytest.mark.parametrize(
        "first_name,last_name,email,colour,expected_colour",
        [
            ("Jane", "Smith", "jane@example.com", "green", Colour.GREEN),
            ("Bob", "Jones", "bob@example.com", "blue", Colour.BLUE),
            ("Mary Jane", "Van Der Berg", "mary@example.com", "red", Colour.RED),
        ],
    )
    def test_valid_user_variations(
        self,
        first_name: str,
        last_name: str,
        email: str,
        colour: str,
        expected_colour: Colour,
    ) -> None:
        """Test user creation with various valid inputs"""
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            favourite_colour=colour,
        )
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.email == email
        assert user.favourite_colour == expected_colour

    def test_whitespace_trimmed(self) -> None:
        """Test that leading/trailing whitespace is trimmed from names"""
        user = User(
            first_name="  John  ",
            last_name="  Doe  ",
            email="john@example.com",
            favourite_colour="red",
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"


class TestUserModelInvalidNames:
    """Test User model validation failures for names"""

    @pytest.mark.parametrize(
        "field,value",
        [
            ("first_name", ""),
            ("last_name", ""),
            ("first_name", "   "),
            ("last_name", "   "),
        ],
    )
    def test_empty_or_whitespace_names(self, field: str, value: str) -> None:
        """Test that empty or whitespace-only names fail validation"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "favourite_colour": "red",
        }
        data[field] = value

        with pytest.raises(ValidationError) as exc_info:
            User(**data)

        errors = exc_info.value.errors()
        assert any("cannot be empty" in str(error["ctx"]["error"]) for error in errors)

    @pytest.mark.parametrize(
        "first_name,last_name",
        [
            ("John123", "Doe"),
            ("John", "Doe123"),
            ("John@", "Doe"),
            ("John", "Doe#$%"),
        ],
    )
    def test_names_with_invalid_characters(
        self, first_name: str, last_name: str
    ) -> None:
        """Test that names with numbers or special characters fail validation"""
        with pytest.raises(ValidationError) as exc_info:
            User(
                first_name=first_name,
                last_name=last_name,
                email="john@example.com",
                favourite_colour="red",
            )
        errors = exc_info.value.errors()
        assert any(
            "only contain letters" in str(error["ctx"]["error"]) for error in errors
        )


class TestUserModelInvalidEmail:
    """Test User model validation failures for email"""

    @pytest.mark.parametrize(
        "email",
        [
            "notanemail.com",  # no @ sign
            "john@",  # no domain
            "",  # empty
        ],
    )
    def test_invalid_email_formats(self, email: str) -> None:
        """Test that invalid email formats fail validation"""
        with pytest.raises(ValidationError):
            User(
                first_name="John", last_name="Doe", email=email, favourite_colour="red"
            )


class TestUserModelInvalidColour:
    """Test User model validation failures for colour"""

    @pytest.mark.parametrize(
        "colour",
        [
            "yellow",  # not in enum
            "",  # empty
            "RED",  # wrong case
        ],
    )
    def test_invalid_colours(self, colour: str) -> None:
        """Test that invalid colours fail validation"""
        with pytest.raises(ValidationError) as exc_info:
            User(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                favourite_colour=colour,
            )
        errors = exc_info.value.errors()
        assert errors[0]["type"] == "enum"
