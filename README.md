# SmartX-Fire

SmartX-Fire is a local simulation and dashboard for exploring how a classifier responds to synthetic heat, smoke, and gas readings. A FastAPI process advances one of three programmed scenarios, classifies each generated frame with a Random Forest model, and streams sensor and inference payloads to a React interface over WebSockets. This is a simulation project, not a deployed fire alarm, certified detector, or fire-safety product.

## The problem it explores

A detector demo should show more than a single threshold crossing. SmartX-Fire lets a developer inspect several scripted scenarios, including an electrical-fire timeline and non-fire cooking and dust profiles, then observe a classifier result and an explanation beside the generated telemetry. It is useful for learning and interface prototyping, not for protecting people or property.

## What works in the checked-in code

- `backend/ml_engine/data_generator.py` builds synthetic, phase-based heat, smoke, and gas readings for `electrical_fire`, `kitchen_cooking`, and `dust_storm`.
- `backend/ml_engine/fusion_model.py` trains a scikit-learn Random Forest when imported. The training examples come from the same generator, with labels assigned by scenario and phase.
- `backend/main.py` exposes simulation start/stop and status routes, and broadcasts sensor and inference JSON over two WebSocket routes.
- The frontend connects to both WebSockets, stores a bounded telemetry history in Zustand, and renders sensor charts, classification output, and a textual feature explanation.
- `backend/test_v5.py` is a print-based scenario smoke script. It is not a pytest suite and does not assert expected predictions.

Those statements describe the repository implementation. The smoke script was run on 2026-11-23; the API and frontend were not exercised end-to-end.

## Architecture

```text
SmartX-Fire/
├── README.md
├── LICENSE
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── test_v5.py
│   └── ml_engine/
│       ├── data_generator.py
│       ├── fusion_model.py
│       └── xai_explainer.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── App.css
        ├── index.css
        ├── components/
        │   ├── InferenceEngine.tsx
        │   ├── TelemetryMatrix.tsx
        │   └── XaiInterpreter.tsx
        └── store/useSimulationStore.ts
```

## Tech stack

| Area | Tools in the repository |
|---|---|
| Backend | Python, FastAPI, Uvicorn, WebSockets |
| Synthetic data and classifier | NumPy, scikit-learn Random Forest |
| Explanations | SHAP for FIRE predictions; phase/context text for SAFE predictions |
| Frontend | React 19, TypeScript, Vite 7 |
| Client state and charts | Zustand and Recharts |
| Icons and styling | Lucide React and project CSS |

The exact Python package versions are not pinned in `backend/requirements.txt`.

## Quickstart

Use Python 3.10 or newer and Node.js/npm. Open two terminals from the repository root.

Terminal 1:

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:

```bash
cd frontend
npm ci
npm run dev
```

Open the Vite URL printed in the frontend terminal, normally `http://localhost:5173`. `frontend/src/App.tsx` uses fixed `http://localhost:8000` and `ws://localhost:8000` addresses. It does not read a frontend API URL from environment configuration.

## Usage

Choose **Kitchen Ops**, **Dust Anomaly**, or **Electrical Fire** to start a scenario. The dashboard reads the current system status, subscribes to the sensor and inference sockets, and displays the latest chart history and explanation. Use **Halt** to stop the backend loop.

The HTTP API can be called directly:

```bash
curl http://127.0.0.1:8000/api/v1/system/status
curl --request POST "http://127.0.0.1:8000/api/v1/simulation/start?scenario_type=electrical_fire"
curl --request POST http://127.0.0.1:8000/api/v1/simulation/stop
```

WebSocket routes:

- `ws://127.0.0.1:8000/ws/sensor-stream`
- `ws://127.0.0.1:8000/ws/inference-stream`

Connect to the sockets before starting a simulation to receive the next broadcast frames. The backend keeps the most recent 60 telemetry frames in browser memory; it does not persist runs.

## API and stream surface

| Type | Path | Behavior |
|---|---|---|
| `GET` | `/api/v1/system/status` | Reports run state, scenario, and connected client counts |
| `POST` | `/api/v1/simulation/start?scenario_type=...` | Resets the frame counter and starts the background loop |
| `POST` | `/api/v1/simulation/stop` | Stops the shared simulation loop |
| WebSocket | `/ws/sensor-stream` | Broadcasts timestamp, heat, smoke, gas, phase, and anomaly flag |
| WebSocket | `/ws/inference-stream` | Broadcasts SAFE/FIRE status, classifier confidence, phase, and explanation |

The scenario name is not validated by the HTTP handler; an unknown value falls back to the kitchen profile in the data generator. There are no HTTP routes for model training, alarm acknowledgement, device enrollment, or real sensor input.

## Simulation and model data

Each sensor frame contains heat in °C, smoke in the generator's optical-density-like scale, gas in ppm, a phase name, and a Boolean `is_anomaly` value. The model receives a seven-value feature vector: the three raw readings, three differences from their rolling averages, and rolling smoke variance.

The generator uses smooth phase interpolation, mean reversion, random noise, and clamping. `fusion_model.py` builds training samples from the same generator at import time. Its labels mark only the `smoldering` and `flaming` phases of `electrical_fire` as FIRE; all kitchen and dust frames are labeled non-fire. When smoke variance is high, the classifier scales down the smoke value and smoke rate-of-change features before prediction.

`xai_explainer.py` uses a SHAP `TreeExplainer` for FIRE output. SAFE output is generated from phase and sensor context rather than SHAP values. These outputs explain this synthetic model only and do not establish real-world detection performance.

## Tests

There is one provided backend smoke script:

```bash
cd backend
python test_v5.py
```

It prints frames and predictions for three scenarios. It has no assertions, does not test the FastAPI routes or WebSocket lifecycle, and does not validate detection quality. The frontend `package.json` defines `build`, `lint`, and `dev`; it does not define a test command.

The inference display also contains hard-coded `12.4ms` and `FR-XGB-V10` labels in `frontend/src/components/InferenceEngine.tsx`. Those values are presentation text, not measured runtime latency or the classifier implementation. Do not use them as performance claims.

Verified on 2026-11-23: `npm run build` passes, and `python test_v5.py` runs all three scenarios and prints classifier output. The smoke script still has no assertions, and the API/WebSocket lifecycle was not exercised in a browser.

## Deployment

No deployment manifests, container files, or hosting setup are present in the inspected repository. For a local demo, run the API and Vite development server in separate terminals as shown above. Do not connect this simulator to building alarms or use it to make safety decisions. It has no physical sensors, certified hardware integration, monitoring, or evidence of fire-code compliance.

The backend currently allows all CORS origins, binds to `0.0.0.0` in its script entry point, and shares one process-wide simulation state across all clients. These defaults are for development, not a production service.

## Design decisions

- Generate input data in code so scenario timelines can be replayed without a physical sensor feed.
- Train a Random Forest from synthetic samples produced by the same generator, keeping the training and simulation feature formats aligned.
- Use separate WebSocket channels for sensor data and inference results.
- Keep chart history in the browser with a 60-frame cap.
- Use a Random Forest explanation path for predicted fire states and phase-aware narrative for safe states.

## Limitations

- This is a simulation, not a deployed or certified fire-safety product. Values and labels are synthetic and must not be treated as measurements or validated fire science.
- Scenario timelines encode their labels. The model's accuracy on generator-produced data would not show how well it detects a real fire.
- `is_anomaly` is set true for every non-ambient phase, including cooking and dust. It means “non-ambient scenario phase” in this implementation, not necessarily sensor anomaly or fire.
- The generator and classifier hold module-level global state. Multiple simultaneous simulation requests or concurrent sessions are not isolated.
- The backend's `simulation_loop()` catches unexpected exceptions and logs them, but does not reset `state.is_running` after an error.
- WebSocket handlers wait for incoming text to keep a connection open; clients do not need to send a documented command protocol.
- The UI does not expose the simulation's `phase` and `is_anomaly` fields consistently across every panel, and its engine-status label is not a measurement of process health.
- The frontend URLs are fixed to localhost. Cross-host configuration and production deployment have not been verified.
- The checked-in smoke script prints results but does not provide regression assertions or test route behavior.

## Roadmap

1. Add deterministic generator tests, model behavior assertions, and API/WebSocket integration tests.
2. Separate synthetic training labels from simulation evaluation, then report metrics only against held-out, documented synthetic datasets.
3. Make scenario selection, backend URLs, and model settings configurable; isolate run state per session.
4. Add a clear simulation-only warning in the UI and remove the hard-coded latency and algorithm labels.
5. Document the assumptions behind each synthetic scenario and keep all future hardware or safety claims out of scope until separately validated and certified.

## License

The repository includes an MIT License. See [`LICENSE`](LICENSE).
