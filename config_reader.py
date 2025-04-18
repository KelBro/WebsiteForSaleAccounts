from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: SecretStr
    bot_token: SecretStr
    admins: list[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
