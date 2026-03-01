"""
SmartX-Fire XAI Explainer V5
Phase-aware explanations grounded in the scenario's current stage.
"""

import shap
import numpy as np
from .fusion_model import get_model, penalize_features

FEATURE_NAMES = [
    "heat", "smoke", "gas",
    "heat_roc", "smoke_roc", "gas_roc",
    "smoke_variance"
]

# Phase display names for human readability
PHASE_DESCRIPTIONS = {
    "ambient": "Normal ambient conditions. All sensors within baseline parameters.",
    "incipient": "Incipient stage: early thermal rise detected. Wire insulation may be degrading. No visible smoke yet.",
    "smoldering": "Smoldering combustion confirmed. Elevated smoke and toxic gas emissions indicate active pyrolysis.",
    "flaming": "Open flaming detected. Rapid heat acceleration with peak toxic gas output.",
    "cooking": "Controlled cooking activity. Moderate heat and trace smoke consistent with food preparation.",
    "cooking_peak": "Peak cooking output. Elevated smoke from oil/grease is expected. No fire indicators.",
    "dust_onset": "Environmental particulate anomaly detected. Smoke sensor obscuration rising without thermal correlation.",
    "dust_peak": "Heavy dust/particulate saturation. Smoke readings unreliable. Cross-referencing heat and gas to filter false alarms.",
}

_explainer = None


def _get_explainer():
    global _explainer
    if _explainer is None:
        model = get_model()
        _explainer = shap.TreeExplainer(model)
    return _explainer


def explain_prediction(features: np.ndarray, phase_name: str = "unknown") -> dict:
    """
    SHAP-based explanation for FIRE predictions.
    """
    f_scaled = penalize_features(features)
    explainer = _get_explainer()

    shap_values = explainer.shap_values(f_scaled)

    # Handle different shap output formats
    if isinstance(shap_values, list):
        vals = shap_values[1][0]
    else:
        if len(shap_values.shape) == 3:
            vals = shap_values[0, :, 1]
        else:
            vals = shap_values[0]

    contributions = {FEATURE_NAMES[i]: float(vals[i]) for i in range(len(FEATURE_NAMES))}
    sorted_features = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    human_readable = _generate_fire_text(sorted_features, features[0], phase_name)

    return {
        "top_features": contributions,
        "human_readable": human_readable,
    }


def explain_safe(features: np.ndarray, phase_name: str = "ambient") -> dict:
    """
    Context-aware explanation for SAFE predictions.
    Uses the current phase to provide meaningful, specific context.
    """
    raw_f = features[0]
    heat, smoke, gas = raw_f[0], raw_f[1], raw_f[2]
    variance = raw_f[6]

    # Use phase description as primary explanation
    text = f"[STATUS] {phase_name.upper()} Phase.\n"
    text += f"• Indicator: {PHASE_DESCRIPTIONS.get(phase_name, 'Monitoring in progress.')}\n"

    # Add sensor-specific context
    if variance > 1.0:
        text += f"• Action: Smoke variance high ({variance:.1f}). Adaptive fusion engaged.\n"
    elif heat > 30.0 and smoke > 0.05:
        text += f"• Context: Heat at {heat:.1f}C with smoke at {smoke:.2f} obs/m. Consistent with non-fire thermal activity.\n"

    dummy_features = {
        "smoke": float(smoke),
        "heat": float(heat),
        "gas": float(gas),
        "smoke_roc": float(raw_f[4]),
        "heat_roc": float(raw_f[3]),
        "gas_roc": float(raw_f[5]),
        "smoke_variance": float(variance),
    }

    return {
        "top_features": dummy_features,
        "human_readable": text,
    }


def _generate_fire_text(sorted_features, raw_f, phase_name: str) -> str:
    """Generate human-readable explanation for FIRE classification."""
    top_name, top_val = sorted_features[0]
    phase_desc = PHASE_DESCRIPTIONS.get(phase_name, "")

    text = f"[ALARM] {phase_name.upper()} Phase Detected.\n"

    if "roc" in top_name:
        feature_clean = top_name.split("_")[0].capitalize()
        text += f"• Primary Trigger: Rapid {feature_clean} rate-of-change ({round(top_val, 3)} SHAP)\n"
    else:
        feature_clean = top_name.capitalize()
        text += f"• Primary Trigger: High {feature_clean} levels ({round(top_val, 3)} SHAP)\n"

    if phase_desc:
        text += f"• Secondary Indicator: {phase_desc}"

    return text
