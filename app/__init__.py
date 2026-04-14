"""Flask application initialization."""

import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import config
from app.database.db import db, init_db

# Import blueprints
from app.routes.auth_routes import auth_bp
from app.routes.profile_routes import profile_bp
from app.routes.resume_routes import resume_bp
from app.routes.career_routes import career_bp
from app.routes.interview_routes import interview_bp
from app.routes.engagement_routes import engagement_bp
from app.routes.report_routes import report_bp
from app.routes.home_routes import home_bp


# Load environment variables (.env)
load_dotenv()


def create_app(config_name="development"):

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Load configuration
    app.config.from_object(config[config_name])

    # Enable CORS
    CORS(app)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(engagement_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(home_bp)

    # Home route
    @app.route("/")
    def home():
        return render_template("login.html")

    # Health check
    @app.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    return app