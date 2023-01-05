"""
Movie DB Model module
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from schemas.movie import Movie as MovieSchema


class Movie(SQLModel, MovieSchema, table=True):
    """
    Movie Class for datatable movie inherited from SQLModel and
     Movie Model (Pydantic Base Model).
    """
    id: Optional[int] = Field(
        default=None, title='Movie ID', description='ID of the Movie',
        primary_key=True, index=True)
