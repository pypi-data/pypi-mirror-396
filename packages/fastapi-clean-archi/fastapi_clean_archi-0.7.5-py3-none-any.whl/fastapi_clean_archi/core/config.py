import os

from pydantic.v1 import BaseSettings


class AbstractSettings(BaseSettings):
    DATABASE = {
        "driver": "sqlite",
        "name": "sqlite.db",
        "user": "",
        "password": "",
        "host": "",
        "port": "",
    }

    DATABASE_URL: str = (
        f"{DATABASE['driver']}:///{DATABASE['name']}"
        if DATABASE["driver"] == "sqlite"
        else f"{DATABASE['driver']}://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['name']}"
    )

    class Config:
        env_file = os.environ.get("SETTINGS_ENV", ".env")
