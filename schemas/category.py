"""
Category Schema script
"""
from enum import Enum


class Category(str, Enum):
    """
    Category class based on string ENUMs
    """
    ACTION: str = 'action'
    ADVENTURE: str = 'adventure'
    COMEDY: str = 'comedy'
    DRAMA: str = 'drama'
    FANTASY: str = 'fantasy'
    HORROR: str = 'horror'
    MUSICAL: str = 'musical'
    MYSTERY: str = 'mystery'
    ROMANCE: str = 'romance'
    SCIENCE: str = 'science'
    FICTION: str = 'fiction'
    SPORT: str = 'sport'
    THRILLER: str = 'thriller'
    WESTERN: str = 'western'
