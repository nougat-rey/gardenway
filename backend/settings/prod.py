import os
from .common import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ["https://gardenway-2d10f268a969.herokuapp.com/"]
SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
        'default':dj_database_url.config()
    }
