"""
Config script
"""
from functools import lru_cache
from typing import Union, Optional, Any
from pydantic import AnyHttpUrl, BaseSettings, validator, EmailStr, AnyUrl


class Settings(BaseSettings):
    """
    Settings class based on Pydantic Base Settings
    """

    class Config:
        """
        Config class for Settings
        """
        env_file: str = ".env"
        env_file_encoding: str = 'utf-8'

    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str
    OPENAPI_FILE_PATH: str = "/openapi.json"
    ENCODING: str = "UTF-8"
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    # 60 minutes * 24 hours * 8 days = 8 days in minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SERVER_NAME: str
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    # ["http://localhost:5000", "http://localhost:3000",
    # "http://localhost:8080"]
    ALGORITHM: str = "HS256"

    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[
        list[str], str]:
        """
        Assemble Backend CORS origins validator.
        :param v:
        :type v: Union[str, list[str]]
        :return:
        :rtype: Union[list[str], str]
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SMTP_PORT: Optional[int]
    SMTP_HOST: Optional[str]
    SMTP_USER: Optional[str]
    SMTP_PASSWORD: Optional[str]
    EMAILS_FROM_EMAIL: Optional[EmailStr]
    EMAILS_FROM_NAME: Optional[str]
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int
    EMAIL_TEMPLATES_DIR: str
    EMAILS_ENABLED: bool

    @validator("EMAILS_ENABLED", pre=True, allow_reuse=True)
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        """
        Get emails enabled validator.
        :param v:
        :type v: bool
        :param values:
        :type values: dict[str, Any]
        :return: boolean condition if SMTP data is available
        :rtype: bool
        """
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )


@lru_cache()
def get_setting() -> Settings:
    """
    Get settings cached
    :return: settings object
    :rtype: Settings
    """
    return Settings()
