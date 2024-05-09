"""Server to communicate with a HighFinesse wavemeter."""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

configs = {}

class Setting(BaseSettings):  # pylint: disable=too-few-public-methods
    """Setting to specify the target config file path."""
    config_path: str = "config.json"


setting = Setting()


def load_configs():
    """Loads config information from the config file.

    The file should have the following JSON structure:

      {
        "version": {version},
        "dll_path": {dll_path},
        "app_path": {app_path}
      }
    """
    with open(setting.config_path, encoding="utf-8") as config_file:
        configs.update(json.load(config_file))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan events.

    This function is set as the lifespan of the application.
    """
    yield


app = FastAPI(lifespan=lifespan)
