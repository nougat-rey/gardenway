from .common import *
import environ

env = environ.Env()

SECRET_KEY = env('DEV_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'store',
        'USER': 'root',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306'
    }
}