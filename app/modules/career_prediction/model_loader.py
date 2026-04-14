"""Model loading utilities for career prediction."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Tuple


def _resolve_artifact_paths(
    model_filename: str = "model.pkl",
    vectorizer_filename: str = "vectorizer.pkl",
) -> Tuple[Path, Path]:
    """Build artifact paths relative to this module directory."""
    base_dir = Path(__file__).resolve().parent
    return base_dir / model_filename, base_dir / vectorizer_filename


def _load_pickle_file(file_path: Path) -> Any:
    """Load one pickled object from disk."""
    with file_path.open("rb") as file_obj:
        return pickle.load(file_obj)


def load_model_and_vectorizer(
    model_filename: str = "model.pkl",
    vectorizer_filename: str = "vectorizer.pkl",
) -> Tuple[Any, Any]:
    """Load and return trained model and vectorizer from pickle files."""
    model_path, vectorizer_path = _resolve_artifact_paths(
        model_filename=model_filename,
        vectorizer_filename=vectorizer_filename,
    )

    missing_files = [str(path) for path in (model_path, vectorizer_path) if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing artifact file(s): {', '.join(missing_files)}")

    model = _load_pickle_file(model_path)
    vectorizer = _load_pickle_file(vectorizer_path)
    return model, vectorizer
