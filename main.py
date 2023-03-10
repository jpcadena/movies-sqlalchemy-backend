"""
Main script to execute API.
"""
import json
from typing import Optional
from anyio.streams.file import FileWriteStream, FileReadStream
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.router import movie, authentication
from core import config
from db.db import create_db_and_tables
from helper.helper import update_json
from middleware.error_handler import ErrorHandler

DESCRIPTION: str = """**Movies API** helps you do awesome stuff. 🚀\n\n
 ![Movies](https://ichef.bbci.co.uk/childrens-responsive-ichef-live/r/400/1.5x/cbbc/bp-film-review-title.jpg)"""
tags_metadata = [
    {
        "name": "movies",
        "description": "Operations with movies, such as register, get, update "
                       "and delete.",
    },
    {
        "name": "authentication",
        "description": "The **login** logic is here as well as password "
                       "recovery and reset",
    },
]


def custom_generate_unique_id(route: APIRoute) -> Optional[str]:
    """
    Generate a custom unique ID for each route in API
    :param route: endpoint route
    :type route: APIRoute
    :return: new ID based on tag and route name
    :rtype: string or None
    """
    if route.name == 'root':
        return None
    return f"{route.tags[0]}-{route.name}"


settings: config.Settings = config.get_setting()

app: FastAPI = FastAPI(
    title='Movies Backend based on FastAPI and Async SQLite',
    description=DESCRIPTION,
    openapi_url=settings.API_V1_STR + settings.OPENAPI_FILE_PATH,
    openapi_tags=tags_metadata,
    contact={
        "name": "Juan Pablo Cadena Aguilar",
        "url": "https://www.github.com/jpcadena",
        "email": "jpcadena@espol.edu.ec"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
    generate_unique_id_function=custom_generate_unique_id)
app.include_router(movie.router, prefix=settings.API_V1_STR)
app.include_router(authentication.router, prefix=settings.API_V1_STR)
app.add_middleware(ErrorHandler)


@app.get("/")
async def root() -> dict[str, str]:
    """
    Function to retrieve homepage.
    - :return: Welcome message
    - :rtype: dict[str, str]
    """
    return {"message": "Hello World"}


@app.on_event('startup')
async def startup_event() -> None:
    """
    Startup API
    :return: None
    :rtype: NoneType
    """
    setting: config.Settings = config.get_setting()
    async with await FileWriteStream.from_path(
            setting.OPENAPI_FILE_PATH) as stream:
        await stream.send(json.dumps(app.openapi()).encode(
            encoding=setting.ENCODING))
    async with await FileReadStream.from_path(
            setting.OPENAPI_FILE_PATH) as stream:
        async for chunk in stream:
            print(chunk.decode(), end='')
    await update_json(setting)
    await create_db_and_tables()


app.add_middleware(
    CORSMiddleware, allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/static/images', StaticFiles(directory='static/images'),
          name='images')
