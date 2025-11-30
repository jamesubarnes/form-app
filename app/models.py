from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class Colour(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    favourite_colour: Colour

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Ensure names are not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError("This field cannot be empty")
        if not v.replace(" ", "").isalpha():
            raise ValueError("This field can only contain letters")
        return v.strip()
