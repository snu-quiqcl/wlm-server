"""Server to communicate with a HighFinesse wavemeter."""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings
from pylablib.devices.HighFinesse.wlm import WLM

logger = logging.getLogger(__name__)

configs = {}

wlm: WLM

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


def open_connection():
    """Opens the connection to the wavelength meter."""
    global wlm  # pylint: disable=global-statement
    wlm = WLM(configs["version"], configs["dll_path"], configs["app_data"])
    wlm.open()


def close_connection():
    """Closes the connection to the wavelength meter."""
    wlm.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan events.

    This function is set as the lifespan of the application.
    """
    load_configs()
    open_connection()
    yield
    close_connection()


app = FastAPI(lifespan=lifespan)
