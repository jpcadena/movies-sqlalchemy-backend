"""
Movie router module for API endpoints.
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi import Depends, Path, status
from fastapi.responses import Response
from pydantic import PositiveInt
from sqlmodel.ext.asyncio.session import AsyncSession
from db.db import get_session
from schemas.category import Category
from schemas.movie import Movie
from services.movie import MovieService

router: APIRouter = APIRouter(prefix='/movie', tags=['movie'])


@router.post('/movies', response_model=dict,
             status_code=201)
async def create_movie(
        movie: Movie = Body(
            ..., title='New movie', description='New movie to create'),
        session: AsyncSession = Depends(get_session)) -> Movie:
    """
    Create a new movie into the system.
    - :param movie: Movie object to create
    - :type movie: Movie
    - :return: Created movie
    - :rtype: Movie
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    movie: Movie = await MovieService.create_movie(movie, session)
    return movie


@router.get('/movies/{movie_id}', response_model=Movie)
async def get_movie(
        movie_id: PositiveInt = Path(
            ..., title='Movie ID', description='ID of the Movie to searched',
            example=1), session: AsyncSession = Depends(get_session)) -> Movie:
    """
    Search for specific Movie by ID.
    - :param movie_id: ID of specific Movie to search
    - :type movie_id: PositiveInt
    - :return: Movie with given ID
    - :rtype: Movie
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    movie: Movie = await MovieService.read_movie_by_id(movie_id, session)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Movie with ID {movie_id} '
                                   f'not found in the system.')
    return movie


@router.get('/get-all-movies', response_model=list[Movie])
async def get_movies(
        session: AsyncSession = Depends(get_session)) -> list[Movie]:
    """
    Retrieve all movies from the system.
    - :return: All movies
    - :rtype: list[Movie]
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    movies: list[Movie] = await MovieService.read_all_movies(session)
    if not movies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user has no movies in the system.')
    return movies


@router.get('/get-movies-by-category/{category}', response_model=list[Movie])
async def get_movies_by_category(
        category: Category = Path(
            ..., title='Category', description='Category of the Movie',
            example=Category.ACTION.value),
        session: AsyncSession = Depends(get_session)) -> list[Movie]:
    """
    Retrieve all movies based on a category from the system.
    - :param category: Category to filter the movies
    - :type category: Category
    - :return: List of movies with specified category
    - :rtype: list[Movie]
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    movies: list[Movie] = await MovieService.read_movies_by_category(
        category, session)
    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'This user has no movies from category: {category.value}'
                   f' in the system.')
    return movies


@router.put('/update-movie/{movie_id}', response_model=dict,
            status_code=200)
async def update_movie(
        movie_id: PositiveInt = Path(
            ..., title='Movie ID', description='ID of the Movie to updated',
            example=1), movie: Movie = Body(
            ..., title='Movie data', description='New movie data to update'),
        session: AsyncSession = Depends(get_session)) -> dict:
    """
    Update movie information in the system.
    :param movie_id: Identifier of the movie to be updated
    :type movie_id: PositiveInt
    :param movie: New data from the movie to update
    :type movie: Movie
    :return: Updated movie with new information
    :rtype: Movie
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    found_movie: Movie = await MovieService.read_movie_by_id(movie_id, session)
    if not found_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Movie with ID {movie_id} '
                                   f'not found in the system.')
    updated_movie: Movie = await MovieService.update_movie_by_id(
        movie_id, movie, session)
    if not updated_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Movie not found in the system.')
    return updated_movie


@router.delete('/delete-movie/{movie_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
        movie_id: PositiveInt = Path(
            ..., title='Movie ID', description='ID of the Movie to deleted',
            example=1), session: AsyncSession = Depends(get_session)) -> dict:
    """
    Delete a specific movie given its ID
    :param movie_id: Identifier of the movie to be deleted
    :type movie_id: PositiveInt
    :return: Information about the delete process
    :rtype:dict
    \f
    :param session: Async session for database connection
    :type session: AsyncSession
    """
    found_movie: Movie = await MovieService.read_movie_by_id(movie_id, session)
    if not found_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Movie with ID {movie_id} '
                                   f'not found in the system.')
    data: dict = await MovieService.delete_movie_by_id(movie_id, session)
    response: Response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
        media_type='application/json')
    response.headers['deleted'] = str(data['ok']).lower()
    response.headers['deleted_at'] = str(data['deleted_at'])
    return response
