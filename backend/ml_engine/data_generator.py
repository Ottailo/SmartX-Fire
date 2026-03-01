"""
SmartX-Fire Data Generator V5
Phase-based scenario engine grounded in NFPA/IAFSS fire science research.

Each scenario is a timeline of phases. Each phase defines realistic sensor
target ranges. The generator smoothly interpolates between phases using
sigmoid transitions, producing organic, noisy curves.

Reference values (from fire science literature):
  Ambient:    Heat 20-24°C,  Smoke 0.00-0.02 obs/m,  Gas 0-5 ppm
  Incipient:  Heat 24-35°C,  Smoke 0.02-0.5 obs/m,   Gas 5-30 ppm
  Smoldering: Heat 35-150°C, Smoke 0.5-3.0 obs/m,    Gas 30-200 ppm
  Flaming:    Heat 150-600°C,Smoke 3.0-8.0 obs/m,     Gas 200-1500 ppm
"""

import math
import numpy as np
from collections import deque
from typing import Tuple, Dict, List

# ---- Phase Definitions ----
# Each phase: (name, start_frame, heat_target, smoke_target, gas_target, heat_noise, smoke_noise, gas_noise)

SCENARIOS: Dict[str, List[dict]] = {
    "electrical_fire": [
        {"name": "ambient",    "start": 0,   "heat": 22.0,  "smoke": 0.01, "gas": 3.0,    "h_noise": 0.3,  "s_noise": 0.005, "g_noise": 1.0},
        {"name": "incipient",  "start": 30,  "heat": 32.0,  "smoke": 0.15, "gas": 25.0,   "h_noise": 0.8,  "s_noise": 0.03,  "g_noise": 4.0},
        {"name": "smoldering", "start": 80,  "heat": 120.0, "smoke": 2.5,  "gas": 180.0,  "h_noise": 5.0,  "s_noise": 0.4,   "g_noise": 20.0},
        {"name": "flaming",    "start": 150, "heat": 450.0, "smoke": 6.0,  "gas": 800.0,  "h_noise": 25.0, "s_noise": 0.8,   "g_noise": 80.0},
    ],
    "kitchen_cooking": [
        {"name": "ambient",    "start": 0,   "heat": 22.0,  "smoke": 0.01,  "gas": 3.0,   "h_noise": 0.3,  "s_noise": 0.005, "g_noise": 1.0},
        {"name": "cooking",    "start": 15,  "heat": 48.0,  "smoke": 0.4,   "gas": 12.0,  "h_noise": 2.0,  "s_noise": 0.08,  "g_noise": 3.0},
        {"name": "cooking_peak","start": 60, "heat": 55.0,  "smoke": 0.6,   "gas": 18.0,  "h_noise": 3.0,  "s_noise": 0.12,  "g_noise": 4.0},
    ],
    "dust_storm": [
        {"name": "ambient",    "start": 0,   "heat": 22.0,  "smoke": 0.01, "gas": 3.0,    "h_noise": 0.3,  "s_noise": 0.005, "g_noise": 1.0},
        {"name": "dust_onset", "start": 20,  "heat": 22.5,  "smoke": 5.0,  "gas": 4.0,    "h_noise": 0.5,  "s_noise": 2.0,   "g_noise": 1.5},
        {"name": "dust_peak",  "start": 50,  "heat": 23.0,  "smoke": 10.0, "gas": 5.0,    "h_noise": 0.5,  "s_noise": 4.0,   "g_noise": 1.5},
    ],
}

# Rolling history for feature extraction
WINDOW_SIZE = 30
_history_heat = deque(maxlen=WINDOW_SIZE)
_history_smoke = deque(maxlen=WINDOW_SIZE)
_history_gas = deque(maxlen=WINDOW_SIZE)

# Internal state
_current_heat = 22.0
_current_smoke = 0.01
_current_gas = 3.0


def _reset():
    global _current_heat, _current_smoke, _current_gas
    _history_heat.clear()
    _history_smoke.clear()
    _history_gas.clear()
    _current_heat = 22.0
    _current_smoke = 0.01
    _current_gas = 3.0


def _sigmoid(x: float) -> float:
    """Smooth S-curve transition between 0 and 1."""
    return 1.0 / (1.0 + math.exp(-x))


def _get_phase_targets(scenario_type: str, t: int):
    """
    Given the current frame, return interpolated target values and noise levels
    by blending between the two nearest phases using a sigmoid transition.
    Also returns the current phase name and whether it's an anomaly.
    """
    phases = SCENARIOS.get(scenario_type, SCENARIOS["kitchen_cooking"])

    # Find which two phases we are between
    current_phase = phases[0]
    next_phase = None

    for i in range(len(phases) - 1):
        if t >= phases[i]["start"]:
            current_phase = phases[i]
            next_phase = phases[i + 1]

    # If we're past the last phase start, we're fully in the last phase
    if next_phase is None or t >= next_phase["start"]:
        final_phase = phases[-1] if t >= phases[-1]["start"] else current_phase
        is_anomaly = final_phase["name"] not in ("ambient",)
        return (
            final_phase["heat"], final_phase["smoke"], final_phase["gas"],
            final_phase["h_noise"], final_phase["s_noise"], final_phase["g_noise"],
            final_phase["name"], is_anomaly
        )

    # Sigmoid blend between current and next phase
    # transition_width controls how "sharp" the transition is (lower = sharper)
    transition_width = max(5.0, (next_phase["start"] - current_phase["start"]) * 0.15)
    midpoint = (current_phase["start"] + next_phase["start"]) / 2.0
    blend = _sigmoid((t - midpoint) / transition_width)

    heat_target = current_phase["heat"] + blend * (next_phase["heat"] - current_phase["heat"])
    smoke_target = current_phase["smoke"] + blend * (next_phase["smoke"] - current_phase["smoke"])
    gas_target = current_phase["gas"] + blend * (next_phase["gas"] - current_phase["gas"])

    h_noise = current_phase["h_noise"] + blend * (next_phase["h_noise"] - current_phase["h_noise"])
    s_noise = current_phase["s_noise"] + blend * (next_phase["s_noise"] - current_phase["s_noise"])
    g_noise = current_phase["g_noise"] + blend * (next_phase["g_noise"] - current_phase["g_noise"])

    # Determine phase name based on which side of the blend we're closer to
    phase_name = next_phase["name"] if blend > 0.5 else current_phase["name"]
    is_anomaly = phase_name not in ("ambient",)

    return heat_target, smoke_target, gas_target, h_noise, s_noise, g_noise, phase_name, is_anomaly


def get_next_simulation_frame(scenario_type: str, frame_counter: int) -> Tuple[Dict, np.ndarray, bool]:
    """
    Generates one frame of synthetic sensor data for the given scenario.

    Returns:
        raw_data: Dict with timestamp, heat, smoke, gas, phase_name
        features: numpy array for ML engine
        is_anomaly: whether we're in a non-ambient phase
    """
    global _current_heat, _current_smoke, _current_gas

    if frame_counter == 0:
        _reset()

    t = frame_counter

    # Get interpolated targets and noise for this frame
    h_target, s_target, g_target, h_noise, s_noise, g_noise, phase_name, is_anomaly = \
        _get_phase_targets(scenario_type, t)

    # Mean-revert toward target with proportional pull + random noise
    # theta controls how quickly we track the target (0.05 = smooth, 0.3 = snappy)
    theta = 0.08

    _current_heat += theta * (h_target - _current_heat) + np.random.normal(0, h_noise)
    _current_smoke += theta * (s_target - _current_smoke) + np.random.normal(0, s_noise)
    _current_gas += theta * (g_target - _current_gas) + np.random.normal(0, g_noise)

    # Add dust-specific rolling waves (sine modulation on smoke only)
    if scenario_type == "dust_storm" and phase_name != "ambient":
        wave = math.sin(t * 0.15) * 2.0 + math.sin(t * 0.07) * 1.5
        _current_smoke += wave

    # Clamp to physical limits
    _current_heat = max(18.0, min(850.0, _current_heat))
    _current_smoke = max(0.0, min(100.0, _current_smoke))
    _current_gas = max(0.0, min(5000.0, _current_gas))

    raw_heat = round(_current_heat, 2)
    raw_smoke = round(_current_smoke, 3)
    raw_gas = round(_current_gas, 2)

    # Append to rolling history
    _history_heat.append(raw_heat)
    _history_smoke.append(raw_smoke)
    _history_gas.append(raw_gas)

    # Feature extraction
    heat_avg = sum(_history_heat) / len(_history_heat)
    smoke_avg = sum(_history_smoke) / len(_history_smoke)
    gas_avg = sum(_history_gas) / len(_history_gas)

    heat_roc = raw_heat - heat_avg
    smoke_roc = raw_smoke - smoke_avg
    gas_roc = raw_gas - gas_avg

    smoke_var = float(np.var(list(_history_smoke))) if len(_history_smoke) > 1 else 0.0

    # Feature vector: [heat, smoke, gas, heat_roc, smoke_roc, gas_roc, smoke_variance]
    features = np.array([[raw_heat, raw_smoke, raw_gas, heat_roc, smoke_roc, gas_roc, smoke_var]])

    raw_data = {
        "timestamp": t,
        "heat": raw_heat,
        "smoke": raw_smoke,
        "gas": raw_gas,
        "phase": phase_name,
    }

    return raw_data, features, is_anomaly
