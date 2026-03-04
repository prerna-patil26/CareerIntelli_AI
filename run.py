#!/usr/bin/env python
"""Run CareerIntelli AI Flask application."""

import os
from app import create_app
from app.config import config

# Get configuration from environment or use default
config_name = os.environ.get('FLASK_ENV', 'development')

# Create Flask app
app = create_app(config_name)

if __name__ == '__main__':
    # Enable debug mode in development
    debug_mode = config_name == 'development'
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        use_reloader=True
    )
