"""Database initialization and configuration module."""

from flask_sqlalchemy import SQLAlchemy
import os


# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application instance
    """
    #db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully")


def drop_all_tables(app):
    """
    Drop all database tables (for development only).
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        print("All tables dropped")
