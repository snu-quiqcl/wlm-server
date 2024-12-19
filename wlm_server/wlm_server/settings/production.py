from .base import *

SECRET_KEY = config('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['localhost', config('SERVER_IP')]

CSRF_TRUSTED_ORIGINS = [
    'https://localhost', f'https://{config('SERVER_IP')}']
