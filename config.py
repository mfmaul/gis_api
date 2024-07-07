# config.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s' % (os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_HOST'), os.environ.get('DB_PORT'), os.environ.get('DB_NAME'))
    SQLALCHEMY_BINDS = {
        'postgis': 'postgresql+psycopg2://%s:%s@%s:%s/%s' % (os.environ.get('POSTGIS_DB_USER'), os.environ.get('POSTGIS_DB_PASSWORD'), os.environ.get('POSTGIS_DB_HOST'), os.environ.get('POSTGIS_DB_PORT'), os.environ.get('POSTGIS_DB_NAME'))
    }

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_ECHO = True

class UatConfig(Config):
    ENV = "uat"
    DEBUG = True
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    SQLALCHEMY_ECHO = False
