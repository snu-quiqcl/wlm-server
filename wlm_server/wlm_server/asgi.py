"""
ASGI config for wlm_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path
from django.conf import settings
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wlm_server.settings.production')

asgi_application = get_asgi_application()

# pylint: disable=wrong-import-position
from cache.channel import ChannelCache
from operation.consumers import OperationConsumer
from setting.consumers import SettingConsumer
from measurement.consumers import MeasurementConsumer
from lock.consumers import LockConsumer
from pid_setting.consumers import DacControlConsumer
from event.consumers import EventConsumer

settings.CHANNEL_CACHE = ChannelCache()

application = ProtocolTypeRouter(
    {
        'http': asgi_application,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter([
                    path('ws/operation/<int:ch>/', OperationConsumer.as_asgi()),
                    path('ws/setting/<int:ch>/', SettingConsumer.as_asgi()),
                    path('ws/measurement/<int:ch>/', MeasurementConsumer.as_asgi()),
                    path('ws/lock/<int:ch>/', LockConsumer.as_asgi()),
                    path('ws/pid_setting/dac_control/<int:ch>/', DacControlConsumer.as_asgi()),
                    path('ws/event/', EventConsumer.as_asgi()),
                ])
            )
        ),
    }
)
