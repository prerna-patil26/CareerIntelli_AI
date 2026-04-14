"""Model training module for career prediction."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from . import data_preprocessing, feature_builder


class ModelTrainer:
    """Train and persist a Random Forest model for career prediction."""

    def __init__(self) -> None:
        """Initialize model state and default artifact paths."""
        base_dir = Path(__file__).resolve().parent
        self.model_path = base_dir / "model.pkl"
        self.vectorizer_path = base_dir / "vectorizer.pkl"

        self.model: Optional[RandomForestClassifier] = None
        self.vectorizer = None
        self.is_trained = False

    def _artifacts_exist(self) -> bool:
        """Check whether both model and vectorizer are already saved."""
        return self.model_path.exists() and self.vectorizer_path.exists()

    def _save_pickle(self, obj: Any, path: Path) -> None:
        """Persist an object to disk using pickle."""
        with path.open("wb") as file_obj:
            pickle.dump(obj, file_obj)

    def train_from_dataset(self, csv_path: str, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train model from a CSV dataset and save artifacts.

        Args:
            csv_path: Path to dataset CSV containing skills and career columns.
            force_retrain: Retrain even if artifacts already exist.

        Returns:
            Dictionary containing status, accuracy, and artifact paths.
        """
        if self.is_trained and not force_retrain:
            return {
                "status": "already_trained",
                "message": "Training skipped in current session.",
                "model_path": str(self.model_path),
                "vectorizer_path": str(self.vectorizer_path),
            }

        if self._artifacts_exist() and not force_retrain:
            self.load_saved_artifacts()
            return {
                "status": "already_trained",
                "message": "Existing saved artifacts found. Training skipped.",
                "model_path": str(self.model_path),
                "vectorizer_path": str(self.vectorizer_path),
            }

        skills_text, y = data_preprocessing.preprocess_career_dataset(csv_path)
        X, vectorizer = feature_builder.build_training_features(skills_text)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.4f}")

        # Refit on complete dataset so saved model has access to all training data.
        model.fit(X, y)

        self.model = model
        self.vectorizer = vectorizer
        self.is_trained = True

        self._save_pickle(self.model, self.model_path)
        self._save_pickle(self.vectorizer, self.vectorizer_path)

        return {
            "status": "trained",
            "accuracy": float(accuracy),
            "model_path": str(self.model_path),
            "vectorizer_path": str(self.vectorizer_path),
        }

    def load_saved_artifacts(self) -> bool:
        """Load saved model and vectorizer from disk."""
        if not self._artifacts_exist():
            return False

        with self.model_path.open("rb") as model_file:
            self.model = pickle.load(model_file)

        with self.vectorizer_path.open("rb") as vectorizer_file:
            self.vectorizer = pickle.load(vectorizer_file)

        self.is_trained = True
        return True
