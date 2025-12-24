"""Module for registry of DAC devices."""

import threading
from typing import Dict, Tuple, Type

from django.conf import settings
from django.utils.module_loading import import_string

from .base import BaseDAC

def get_dac_class(backend_alias: str) -> Type[BaseDAC]:
    """Looks up DAC driver class from settings.DAC_BACKENDS.
    
    Args:
        backend_alias: Alias of the DAC device defined in settings.DAC_BACKENDS.
    
    Returns:
        DAC driver class. if not found, raises ValueError.
    """
    try:
        path = settings.DAC_BACKENDS[backend_alias]
    except KeyError as e:
        raise ValueError(f'Unknown DAC backend alias: {backend_alias}') from e
    return import_string(path)


class DacManager:
    """Manager for DAC instances.
    
    Keys: (backend_alias, port)
    Values: DAC instance
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._instances: Dict[Tuple[str, str], BaseDAC] = {}

    def get_or_open(self, backend_alias: str, port: str) -> BaseDAC:
        """Gets existing DAC instance for (backend_alias, port), or creates one.

        Args:
            backend_alias: See get_dac_class().
            port: See BaseDAC.port.

        Returns:
            The DAC instance.
        """
        key = (backend_alias, port)
        with self._lock:
            dac = self._instances.get(key)
            if dac is not None:
                return dac
            dac_class = get_dac_class(backend_alias)
            dac = dac_class(port)
            dac.open()
            self._instances[key] = dac
            return dac

    def close(self, backend_alias: str, port: str):
        """Closes the DAC instance for (backend_alias, port).
        
        Args:
            backend_alias: See get_dac_class().
            port: See BaseDAC.port.
        """
        key = (backend_alias, port)
        with self._lock:
            dac = self._instances.get(key)
            if dac is None:
                print(f'DAC instance for (backend_alias, port) not found: {key}')
                return
            dac.close()
            del self._instances[key]

    def close_all(self):
        """Closes all DAC instances."""
        with self._lock:
            for dac in self._instances.values():
                if dac.is_open:
                   dac.close()
            self._instances.clear()
