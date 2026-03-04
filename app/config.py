"""Flask application configuration."""

import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///careintelli.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    
    # ML Models path
    MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'trained_models')
    
    # Datasets path
    DATASETS_PATH = os.path.join(os.path.dirname(__file__), '..', 'datasets')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # In production, require secure database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
