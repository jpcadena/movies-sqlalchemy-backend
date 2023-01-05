"""
Movie Schema Script.
"""
from pydantic import BaseModel, Field, PositiveInt
from schemas.category import Category


class Movie(BaseModel):
    """
    Movie class based on Pydantic Base Model
    """
    id: PositiveInt = Field(
        ..., title='Movie ID', description='ID of the Movie')
    title: str = Field(..., title='Title', description='Title of the Movie',
                       min_length=5, max_length=200)
    overview: str = Field(
        ..., title='Oveview', description='Oveview of the Movie',
        min_length=15, max_length=700)
    year: int = Field(
        ..., title='Year', description='Release year of the Movie',
        ge=1888, le=2023)
    rating: float = Field(
        ..., title='Rating', description='Rating of the Movie', ge=0.0,
        le=10.0, multiple_of=0.5)
    category: Category = Field(
        ..., title='Movie ID', description='ID of the Movie')

    class Config:
        """
        Config class for Movie
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "id": 1,
                "title": "My movie",
                "overview": "This is the movie description.",
                "year": 2022,
                "rating": 9.5,
                "category": "horror"
            }
        }
