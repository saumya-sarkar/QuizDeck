import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

class localDev(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///quiz_db.sqlite3")
    
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_TRACKABLE = os.getenv("SECURITY_TRACKABLE", "True").lower() == "true"
    SECURITY_LOGIN_URL = os.getenv("SECURITY_LOGIN_URL")
    SECURITY_TOKEN_AUTHENTICATION_HEADER = os.getenv("SECURITY_TOKEN_AUTHENTICATION_HEADER")

    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        os.getenv("UPLOAD_FOLDER", "static/uploads")
    )
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif").split(","))

class Deployment(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///site.sqlite3")


class celeryConfig():
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/1"
    timezone = "Asia/Kolkata"
    broker_connection_retry_on_startup = True
