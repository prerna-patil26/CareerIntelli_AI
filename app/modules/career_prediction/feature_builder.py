"""Feature building module for career prediction text data."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple, Union

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

TextInput = Union[str, Sequence[str]]


def _normalize_text_input(text_data: TextInput) -> List[str]:
    """Normalize supported text input formats into a list of strings."""
    if isinstance(text_data, str):
        return [text_data]
    return [str(item) for item in text_data]


def build_training_features(
    text_data: TextInput,
    vectorizer: TfidfVectorizer | None = None,
) -> Tuple[csr_matrix, TfidfVectorizer]:
    """Fit TF-IDF vectorizer on training text and return transformed features."""
    train_text = _normalize_text_input(text_data)
    tfidf_vectorizer = vectorizer or TfidfVectorizer()
    features = tfidf_vectorizer.fit_transform(train_text)
    return features, tfidf_vectorizer


def build_prediction_features(
    text_data: TextInput,
    vectorizer: TfidfVectorizer,
) -> csr_matrix:
    """Transform new text input using an already fitted vectorizer."""
    if vectorizer is None:
        raise ValueError("A fitted TF-IDF vectorizer is required for prediction.")

    predict_text = _normalize_text_input(text_data)
    return vectorizer.transform(predict_text)


class FeatureBuilder:
    """Reusable wrapper around TF-IDF functions for training and prediction."""

    def __init__(self) -> None:
        self.vectorizer: TfidfVectorizer | None = None

    def train(self, text_data: TextInput) -> Tuple[csr_matrix, TfidfVectorizer]:
        """Fit and transform training text, storing the fitted vectorizer."""
        features, self.vectorizer = build_training_features(text_data, self.vectorizer)
        return features, self.vectorizer

    def predict(self, text_data: TextInput) -> csr_matrix:
        """Transform new text using the same vectorizer fitted during training."""
        if self.vectorizer is None:
            raise ValueError("Vectorizer is not fitted. Run train() before predict().")
        return build_prediction_features(text_data, self.vectorizer)

    def build_features(self, user_profile: Dict[str, Any]) -> np.ndarray:
        """Backward-compatible numeric feature builder for existing callers."""
        features = []
        skills = user_profile.get("skills", [])
        features.append(len(skills))
        features.append(user_profile.get("experience", 0))
        features.append(user_profile.get("education", 0))
        features.append(user_profile.get("previous_roles", 0))
        return np.array(features)

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Backward-compatible min-max feature normalization."""
        min_vals = np.array([0, 0, 0, 0])
        max_vals = np.array([100, 50, 10, 20])
        return (features - min_vals) / (max_vals - min_vals)
