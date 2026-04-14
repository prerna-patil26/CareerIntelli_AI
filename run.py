#!/usr/bin/env python
"""Run CareerIntelli AI Flask application."""

import os
import logging
from dotenv import load_dotenv
from app import create_app
from app.config import config

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('careerIntelli.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Get configuration from environment or use default
config_name = os.environ.get('FLASK_ENV', 'development')

# Create Flask app
app = create_app(config_name)

if __name__ == '__main__':
    logger.info(f"Starting CareerIntelli AI in {config_name} mode")
    
    # Enable debug mode in development
    debug_mode = config_name == 'development'
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        use_reloader=True
    )
