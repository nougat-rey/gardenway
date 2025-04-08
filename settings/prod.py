import os
from .common import *
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import environ

# Load environment variables from .env
env = environ.Env()
env = environ.Env()
env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
environ.Env.read_env(env_file_path)

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['https://gardenway-11a7983dd747.herokuapp.com']

SECRET_KEY = env('SECRET_KEY')

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

