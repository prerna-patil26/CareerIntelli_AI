"""
Flask Application Configuration
CareerIntelli AI Project
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///careerintelli.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    # ML Models path
    MODELS_PATH = os.path.join(BASE_DIR, "..", "trained_models")

    # Datasets path
    DATASETS_PATH = os.path.join(BASE_DIR, "..", "datasets")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False

    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable must be set in production")
        self.SQLALCHEMY_DATABASE_URI = db_url


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}