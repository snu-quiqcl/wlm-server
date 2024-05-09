"""Server to communicate with a HighFinesse wavemeter."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Setting(BaseSettings):  # pylint: disable=too-few-public-methods
    """Setting to specify the target config file path."""
    config_path: str = "config.json"


setting = Setting()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan events.

    This function is set as the lifespan of the application.
    """
    yield


app = FastAPI(lifespan=lifespan)
