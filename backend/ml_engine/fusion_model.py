"""
SmartX-Fire Fusion Model V5
Trains a Random Forest on data that matches the generator's actual output ranges.
Uses the generator itself to produce training samples, ensuring zero disconnect
between training data and runtime data.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)

_model = None


def _generate_training_data():
    """
    Produces labeled training samples by running the data generator scenarios.
    This ensures the model has seen the full spectrum of values it will encounter.
    """
    from .data_generator import get_next_simulation_frame

    X_train = []
    y_train = []

    # Run each scenario multiple times with slight randomness
    for run in range(8):
        for scenario, label_fn in [
            ("electrical_fire", lambda phase: 1 if phase in ("smoldering", "flaming") else 0),
            ("kitchen_cooking", lambda phase: 0),  # Never fire
            ("dust_storm", lambda phase: 0),         # Never fire
        ]:
            for frame in range(200):
                raw_data, features, is_anomaly = get_next_simulation_frame(scenario, frame)
                phase = raw_data.get("phase", "ambient")
                label = label_fn(phase)
                X_train.append(features[0].tolist())
                y_train.append(label)

    return np.array(X_train), np.array(y_train)


def _initialize_model():
    """Train the Random Forest on generator-produced data."""
    global _model

    logger.info("Training fusion model on generator-produced data...")
    X_train, y_train = _generate_training_data()

    _model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced"  # Handle class imbalance (more SAFE than FIRE samples)
    )
    _model.fit(X_train, y_train)

    # Log training stats
    fire_count = int(np.sum(y_train == 1))
    safe_count = int(np.sum(y_train == 0))
    logger.info(f"Model trained. Samples: {len(y_train)} (FIRE={fire_count}, SAFE={safe_count})")


# Train on import
_initialize_model()


def penalize_features(features: np.ndarray) -> np.ndarray:
    """
    Adaptive Multi-Sensor Fusion logic.
    If smoke variance is excessively high (dust-like), penalize smoke reliance.
    """
    f = np.copy(features)
    variance = f[0][6]  # smoke_variance

    if variance > 1.0:
        # High noise regime: reduce smoke signal to prevent false alarms
        f[0][1] *= 0.3   # smoke raw
        f[0][4] *= 0.3   # smoke_roc
    return f


def predict_fire(features: np.ndarray):
    """
    Applies adaptive scaling and predicts Fire (1) or Normal (0).
    Returns (prediction, confidence).
    """
    f_scaled = penalize_features(features)

    prediction = _model.predict(f_scaled)[0]
    proba = _model.predict_proba(f_scaled)[0]

    confidence = float(proba[1]) if prediction == 1 else float(proba[0])
    return int(prediction), confidence


def get_model():
    return _model
