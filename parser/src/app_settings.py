import functools

import pydantic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    goszakup_token: str = pydantic.Field(..., alias="GOSZAKUP_TOKEN")


@functools.cache
def get_settings() -> Settings:
    return Settings()
