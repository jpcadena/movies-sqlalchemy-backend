"""
Authentication module
"""
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from core import config
from core.security import create_access_token, create_refresh_token
from helper.helper import send_test_email

router: APIRouter = APIRouter(
    prefix='/authentication', tags=['authentication'])


@router.post('/login')
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        setting: config.Settings = Depends(config.get_setting)) -> dict:
    """
    Login method.
    - :param user: Object from request body with username and password
    - :type user: OAuth2PasswordRequestForm
    - :return: Access Token, type, user ID and username
    - :rtype: dict
    \f
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    payload: dict = {
        "iss": setting.SERVER_HOST, "sub": "username:" + user.username,
        "aud": setting.SERVER_HOST + '/authentication/login',
        "exp": int(time.time()) + setting.ACCESS_TOKEN_EXPIRE_MINUTES,
        "nbf": int(time.time()) - 1, "iat": int(time.time()),
        "jti": uuid.uuid4(),
        "preferred_username": user.username,
        "updated_at": datetime.now()}
    access_token: str = await create_access_token(
        payload=payload, setting=setting)
    refresh_token: str = await create_refresh_token(
        payload=payload, setting=setting)
    sent_email: bool = await send_test_email(user.username, setting)
    if not sent_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Mail could not be delivered.')
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }
