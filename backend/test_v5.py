"""Quick test to verify V5 simulation pipeline."""
from ml_engine.data_generator import get_next_simulation_frame
from ml_engine.fusion_model import predict_fire

print("--- ELECTRICAL FIRE ---")
for t in [0, 29, 50, 80, 100, 130, 150, 170, 190]:
    raw, feat, anom = get_next_simulation_frame("electrical_fire", t)
    pred, conf = predict_fire(feat)
    status = "FIRE" if pred == 1 else "SAFE"
    phase = raw["phase"]
    print(f"  t={t:3d}  Phase={phase:15s}  Heat={raw['heat']:7.1f}  Smoke={raw['smoke']:6.3f}  Gas={raw['gas']:7.1f}  -> {status} ({conf:.2%})")

print()
print("--- KITCHEN COOKING ---")
for t in [0, 10, 30, 50, 80]:
    raw, feat, anom = get_next_simulation_frame("kitchen_cooking", t)
    pred, conf = predict_fire(feat)
    status = "FIRE" if pred == 1 else "SAFE"
    phase = raw["phase"]
    print(f"  t={t:3d}  Phase={phase:15s}  Heat={raw['heat']:7.1f}  Smoke={raw['smoke']:6.3f}  Gas={raw['gas']:7.1f}  -> {status} ({conf:.2%})")

print()
print("--- DUST STORM ---")
for t in [0, 15, 30, 50, 70]:
    raw, feat, anom = get_next_simulation_frame("dust_storm", t)
    pred, conf = predict_fire(feat)
    status = "FIRE" if pred == 1 else "SAFE"
    phase = raw["phase"]
    print(f"  t={t:3d}  Phase={phase:15s}  Heat={raw['heat']:7.1f}  Smoke={raw['smoke']:6.3f}  Gas={raw['gas']:7.1f}  -> {status} ({conf:.2%})")

print()
print("V5 PIPELINE TEST COMPLETE")
