"""
API Routes for Engagement Tracking
Flask routes for engagement tracking functionality
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from modules folder
from modules.engagement_tracker import EngagementTracker

# Create blueprint
engagement_bp = Blueprint('engagement', __name__)

# Create tracker instance (singleton)
tracker = EngagementTracker()

@engagement_bp.route('/test-camera', methods=['GET'])
def test_camera():
    """Test if camera is accessible"""
    try:
        is_working = tracker.test_camera()
        return jsonify({
            'success': is_working,
            'message': 'Camera is working' if is_working else 'Camera not available'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/start-tracking', methods=['POST'])
def start_tracking():
    """Start engagement tracking session"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 60)  # Default 60 seconds
        
        # In real API, this would be async
        # For now, we'll just return that tracking is starting
        return jsonify({
            'status': 'started',
            'duration': duration,
            'message': 'Tracking started. Check console for camera window.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/status', methods=['GET'])
def get_status():
    """Get current tracking status"""
    try:
        score_data = tracker.get_engagement_score()
        return jsonify({
            'status': 'active' if score_data['session_duration'] > 0 else 'inactive',
            'metrics': score_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/report', methods=['GET'])
def get_report():
    """Get latest engagement report"""
    try:
        report = tracker.generate_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/score', methods=['GET'])
def get_score():
    """Get just the engagement score"""
    try:
        score = tracker.get_engagement_score()
        return jsonify(score)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/save-report', methods=['POST'])
def save_report():
    """Save current report to file"""
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        
        filepath = tracker.save_report(filename)
        return jsonify({
            'success': True,
            'filepath': filepath,
            'message': 'Report saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@engagement_bp.route('/analyze-pattern', methods=['GET'])
def analyze_pattern():
    """Analyze engagement pattern"""
    try:
        pattern = tracker.analyze_pattern()
        return jsonify(pattern)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500