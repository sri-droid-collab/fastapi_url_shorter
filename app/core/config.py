import os
from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # MongoDB Atlas credentials — set these four values in .env
    MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD")
    MONGODB_HOSTNAME: str = os.getenv("MONGODB_HOSTNAME")
    MONGODB_DATABASE_NAME: str = os.getenv("MONGODB_DATABASE_NAME")

    @computed_field  # type: ignore[misc]
    @property
    def MONGODB_URL(self) -> str:  # noqa: N802
        return (
            f"mongodb+srv://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}"
            f"@{self.MONGODB_HOSTNAME}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_NAME(self) -> str:  # noqa: N802
        return self.MONGODB_DATABASE_NAME

    class Config:
        env_file = ".env"


# Single shared instance — import this everywhere you need settings
settings = Settings()
