"""
Security module for core package
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from jose import jwt
from core import config


async def create_access_token(
        payload: dict, expires_delta: Optional[timedelta] = None,
        setting: config.Settings = Depends(config.get_setting)) -> str:
    """
    Function to create a new access token
    :param payload: claims for token
    :type payload: dict
    :param expires_delta: time expiration
    :type expires_delta: timedelta
    :return: encoded JWT
    :rtype: str
    """
    expire: datetime
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=setting.access_token_expire_minutes)
    payload.update({'exp': int(expire.timestamp())})
    claims: dict = jsonable_encoder(payload)
    encoded_jwt: str = jwt.encode(claims=claims, key=setting.secret_key,
                                  algorithm=setting.ALGORITHM)
    return encoded_jwt


async def create_refresh_token(
        payload: dict, setting: config.Settings = Depends(config.get_setting)
) -> str:
    """
    Create refresh token
    :param payload: Data to add to JWT
    :type payload: dict
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: New refresh token
    :rtype: str
    """
    expires: timedelta = timedelta(
        seconds=setting.refresh_token_expire_seconds)
    return await create_access_token(payload=payload, expires_delta=expires,
                                     setting=setting)


async def decode_token(
        token: str, setting: config.Settings = Depends(config.get_setting)
) -> Optional[dict]:
    """
    Decode a token with OAuth2
    :param token: Given token to decode
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: Payload with JWT claims
    :rtype: dict
    """
    payload: dict
    try:
        payload = jwt.decode(
            token=token, key=setting.secret_key,
            algorithms=[setting.ALGORITHM], options={"verify_subject": False},
            audience=setting.base_url + '/authentication/login',
            issuer=setting.base_url)
        return payload
    except jwt.ExpiredSignatureError as es_exc:
        print(es_exc, ' - ', 'Token expired')
        return None
    except jwt.JWTClaimsError as c_exc:
        print(c_exc, ' - ', 'Authorization claim is incorrect, '
                            'please check audience and issuer')
        return None
    except jwt.JWTError as exc:
        print(exc)
        return None
