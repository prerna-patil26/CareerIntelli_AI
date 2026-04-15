"""
Database initialization and configuration module for CareerIntelli AI.
"""

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance (not attached to app yet)
db = SQLAlchemy()


def init_db(app):
    """
    Create database tables.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")


def drop_all_tables(app):
    """
    Drop all database tables (for development/testing only).

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        print("⚠️ All database tables dropped")


def reset_database(app):
    """
    Drop and recreate all tables (development helper).

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("🔄 Database reset successfully")