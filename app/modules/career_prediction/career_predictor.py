"""Career predictor module for making career predictions."""

from typing import List, Dict, Any
from .feature_builder import FeatureBuilder


class CareerPredictor:
    """Predict suitable career paths for users."""
    
    def __init__(self):
        """Initialize the career predictor."""
        self.feature_builder = FeatureBuilder()
        self.career_mappings = {
            'engineering': ['Software Engineer', 'Data Engineer', 'DevOps Engineer'],
            'data': ['Data Scientist', 'Data Analyst', 'Machine Learning Engineer'],
            'management': ['Project Manager', 'Product Manager', 'Technical Lead'],
            'design': ['UX Designer', 'UI Designer', 'Product Designer']
        }
    
    def predict_careers(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict suitable career paths for a user.
        
        Args:
            user_profile: User profile data
        
        Returns:
            Dictionary with predicted careers and confidence scores
        """
        features = self.feature_builder.build_features(user_profile)
        normalized_features = self.feature_builder.normalize_features(features)
        
        # TODO: Use trained model to predict
        predictions = self._get_base_predictions(user_profile)
        
        return predictions
    
    def _get_base_predictions(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate base predictions based on user skills."""
        skills = set(s.lower() for s in user_profile.get('skills', []))
        predictions = {}
        
        # Simple skill-based matching
        if any(skill in skills for skill in ['python', 'java', 'cpp', 'javascript']):
            predictions['Software Engineer'] = 0.85
            predictions['Data Engineer'] = 0.75
        
        if any(skill in skills for skill in ['sql', 'statistics', 'machine learning']):
            predictions['Data Scientist'] = 0.80
        
        if any(skill in skills for skill in ['project management', 'leadership']):
            predictions['Project Manager'] = 0.75
        
        if any(skill in skills for skill in ['design', 'ui', 'ux']):
            predictions['UX Designer'] = 0.80
        
        # Sort by confidence score
        sorted_predictions = dict(sorted(predictions.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True))
        
        return {
            'predicted_careers': list(sorted_predictions.keys()),
            'confidence_scores': list(sorted_predictions.values()),
            'top_match': list(sorted_predictions.keys())[0] if sorted_predictions else None
        }
