import os
from .common import *
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.exceptions import ImproperlyConfigured

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['https://gardenway-11a7983dd747.herokuapp.com']

# Fetch the SECRET_KEY from environment variables
SECRET_KEY = os.getenv('SECRET_KEY')

# Check if SECRET_KEY is missing (good for debugging)
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")

# Database settings for production
DATABASES = {
    'default': dj_database_url.config()
}

# Cloudinary settings for production
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'CACHEABLE': True,  # To enable caching for faster delivery of media URLs
}

# Use Cloudinary for media storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
