"""
Services for Movie Models.
"""
from datetime import datetime
from typing import Optional
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pydantic import PositiveInt
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db.db import get_session
from models.movie import Movie as MovieDB
from schemas.category import Category
from schemas.movie import Movie


class MovieService:
    """
    Movie Service class for database CRUD.
    """

    @staticmethod
    async def create_movie(movie: Movie, session: AsyncSession = Depends(
                                         get_session)) -> MovieDB:
        """
        Create a new movie into the database
        :param movie: Movie with id, title, overview, year, rating
         and category
        :type movie: Movie
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: Movie created with id, title, overview, year, rating
         and category
        :rtype: MovieDB
        """
        new_movie: MovieDB = MovieDB.from_orm(movie)
        session.add(new_movie)
        await session.commit()
        await session.refresh(new_movie)
        return new_movie

    @staticmethod
    async def read_movie_by_id(
            movie_id: PositiveInt, session: AsyncSession = Depends(get_session)
    ) -> Optional[MovieDB]:
        """
        Read Movie from database with given ID
        :param movie_id: Identifier of specific Movie
        :type movie_id: PositiveInt
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: Movie with given id retrieved from database and also includes
         title, overview, year, rating and category
        :rtype: MovieDB
        """
        statement = select(MovieDB).where(MovieDB.id == movie_id)
        result = await session.exec(statement)
        try:
            found_movie: MovieDB = result.one()
        except NoResultFound as exc:
            print(exc)
            found_movie = None
        return found_movie

    @staticmethod
    async def read_movies_by_category(
            category: Category, session: AsyncSession = Depends(get_session)
    ) -> Optional[list[MovieDB]]:
        """
        Read Movie from database with given ID
        :param category: Category of specific Movie
        :type category: Category
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: List of Movies with given category
        :rtype: list[MovieDB]
        """
        statement = select(MovieDB).where(MovieDB.category == category)
        result = await session.exec(statement)
        try:
            found_movie: list[MovieDB] = result.all()
        except NoResultFound as exc:
            print(exc)
            found_movie = None
        return found_movie

    @staticmethod
    async def read_all_movies(
            session: AsyncSession = Depends(get_session)) -> list[MovieDB]:
        """
        Read Movies
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: list of Movies with ID, title, overview, year, rating
         and category
        :rtype: list[MovieDB]
        """
        statement = select(MovieDB)
        result = await session.exec(statement)
        found_movies: list[MovieDB] = result.all()
        return found_movies

    @staticmethod
    async def update_movie_by_id(
            movie_id: PositiveInt, movie: Movie,
            session: AsyncSession = Depends(get_session)) -> Optional[MovieDB]:
        """
        Update Movie by its id
        :param movie_id: Identifier of the movie
        :type movie_id: PositiveInt
        :param movie: Movie object with new data to update
        :type movie: Movie
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: Movie from database with data updated
        :rtype: MovieDB
        """
        statement = select(MovieDB).where(MovieDB.id == movie_id)
        result = await session.exec(statement)
        try:
            found_movie: MovieDB = result.one()
        except NoResultFound as exc:
            print(exc)
            found_movie = None
        obj_data = jsonable_encoder(found_movie)
        if isinstance(movie, dict):
            update_data = movie
        else:
            update_data = movie.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(found_movie, field, update_data[field])
        session.add(found_movie)
        await session.commit()
        await session.refresh(found_movie)
        return found_movie

    @staticmethod
    async def delete_movie_by_id(
            movie_id: PositiveInt,
            session: AsyncSession = Depends(get_session)) -> dict:
        """
        Delete Movie from database by its ID
        :param movie_id: Identifier of specific Movie
        :type movie_id: PositiveInt
        :param session: Async session for database connection
        :type session: AsyncSession
        :return: Information about deleted confirmation and timestamp
        :rtype: dict
        """
        deleted: bool = True
        statement = select(MovieDB).where(MovieDB.id == movie_id)
        result = await session.exec(statement)
        try:
            movie_to_delete: MovieDB = result.one()
        except NoResultFound as exc:
            print(exc)
            movie_to_delete = None
        if movie_to_delete:
            await session.delete(movie_to_delete)
            await session.commit()
        else:
            deleted = False
        return {"ok": deleted, 'deleted_at': datetime.now()}
