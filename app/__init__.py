"""Flask application initialization."""

from flask import Flask
from flask_cors import CORS
from app.config import config
from app.database.db import db, init_db
from app.routes import (
    auth_bp, profile_bp, resume_bp, career_bp,
    interview_bp, engagement_bp, report_bp
)


def create_app(config_name='development'):
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    init_db(app)
    
    # Register blueprints (routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(engagement_bp)
    app.register_blueprint(report_bp)
    
    # Home route
    @app.route('/')
    def home():
        """Home page."""
        return {'message': 'Welcome to CareerIntelli AI API'}, 200
    
    # Health check
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy'}, 200
    
    return app
