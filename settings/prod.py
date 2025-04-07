import os
from .common import *
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import environ

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Optional if using .env


DEBUG = False
ALLOWED_HOSTS = ['gardenway-4e86e7894057.herokuapp.com']

SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
        'default':dj_database_url.config()
    }

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
    'CACHEABLE': True,  # To enable caching for faster delivery of media URLs
}
# Cloudinary settings
MEDIA_URL = 'https://res.cloudinary.com/{}/'.format(os.getenv('CLOUDINARY_CLOUD_NAME'))


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'