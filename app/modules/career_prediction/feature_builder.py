"""Feature building module for career prediction."""

from typing import List, Dict, Any
import numpy as np


class FeatureBuilder:
    """Build features for career prediction model."""
    
    def __init__(self):
        """Initialize the feature builder."""
        self.feature_names = []
    
    def build_features(self, user_profile: Dict[str, Any]) -> np.ndarray:
        """
        Build feature vector from user profile.
        
        Args:
            user_profile: User profile data
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Encode skills
        skills = user_profile.get('skills', [])
        features.append(len(skills))
        
        # Encode experience
        experience = user_profile.get('experience', 0)
        features.append(experience)
        
        # Encode education level
        education = user_profile.get('education', 0)
        features.append(education)
        
        # Encode previous roles
        previous_roles = user_profile.get('previous_roles', 0)
        features.append(previous_roles)
        
        return np.array(features)
    
    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize feature vector.
        
        Args:
            features: Feature vector
        
        Returns:
            Normalized feature vector
        """
        # Min-max normalization
        min_vals = np.array([0, 0, 0, 0])
        max_vals = np.array([100, 50, 10, 20])
        
        return (features - min_vals) / (max_vals - min_vals)
