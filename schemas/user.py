"""
User schema for Pydantic models
"""
from pydantic import BaseModel, EmailStr, Field
from helper.helper import password_regex


class User(BaseModel):
    """
    User Class that inherits from UserCreate Schema.
    """
    email: EmailStr = Field(
        ..., title='Email', description='Preferred e-mail address of the User',
        unique=True)
    password: str = Field(
        ..., title='New password', description='New password of the User',
        min_length=8, max_length=14, regex=password_regex)
