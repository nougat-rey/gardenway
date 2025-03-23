import os
from .common import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ["https://gardenway-4e86e7894057.herokuapp.com/"]
SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
        'default':dj_database_url.config()
    }
