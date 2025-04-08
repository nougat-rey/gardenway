import os
from .common import *
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import environ

# Load environment variables from .env
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['gardenway-4e86e7894057.herokuapp.com']

SECRET_KEY = os.environ['SECRET_KEY']

# Database settings for production
DATABASES = {
    'default': dj_database_url.config()
}

# Cloudinary settings for production
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
    'CACHEABLE': True,  # To enable caching for faster delivery of media URLs
}

# Use Cloudinary for media storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
