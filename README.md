# SmartX-Fire

**Adaptive Event Simulation System v2.0**

SmartX-Fire is a high-fidelity, adaptive multi-sensor fire detection simulation platform. It integrates a phase-based telemetry generator grounded in real fire science with an AI-driven classification engine, presented through a professional, brutalist "Industrial Intelligence" dashboard.

This project was built to address the flaws in simplistic fire simulators by introducing organic noise profiles, bounded physics, and Explainable AI (XAI).

## Features

- **Phase-Based Simulation Engine:** Generates realistic, stochastic sensor data (Heat, Smoke, Gas) matching the timelines of physical fire stages (Ambient, Incipient, Smoldering, Flaming).
- **ML Classification Pipeline:** Utilizes a Random Forest classifier trained dynamically on generator-produced data ranges for accurate, real-time threat detection.
- **Explainable AI (SHAP):** Features an XAI module that decomposes model predictions into human-readable bullet points and feature-weight bar charts.
- **Industrial Dashboard:** A React/Vite frontend using a data-dense, asymmetric grid layout with pure CSS styling (no generic UI libraries) optimized for professional telemetry monitoring.
- **Scenario Variants:** Pre-configured simulations including Electrical Fire, Kitchen Ops (Cooking), and a raw Dust Anomaly scenario capable of confusing simpler ML models.

## Tech Stack

**Backend:**

- Python 3.10+
- FastAPI
- WebSockets (Real-time data streaming)
- scikit-learn (Random Forest Classification)
- SHAP (Explainable AI)
- NumPy / Pandas

**Frontend:**

- React 19 (Vite)
- TypeScript
- Zustand (State Management)
- Recharts (Telemetry Visualization)
- Lucide React (Icons)
- Pure CSS variables & styling

## Project Structure

```
SmartX-Fire/
├── backend/
│   ├── ml_engine/
│   │   ├── data_generator.py   # Phase-based physics & noise simulation
│   │   ├── fusion_model.py     # Random Forest model & adaptive penalization
│   │   └── xai_explainer.py    # SHAP interpreter & textual output generator
│   ├── main.py                 # FastAPI application & WebSocket orchestrator
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/         # TelemetryMatrix, InferenceEngine, XaiInterpreter
    │   ├── store/              # Zustand global state (useSimulationStore)
    │   ├── App.tsx             # Main Grid Layout
    │   ├── App.css             # Layout Structural CSS
    │   └── index.css           # Global Theme Variables & Component CSS
    ├── package.json
    └── vite.config.ts
```

## Setup & Installation

### 1. Run the Backend

Navigate to the `backend` directory, create a virtual environment, and install dependencies:

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Unix/MacOS:
# source venv/bin/activate

pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server handles WebSocket connections at `ws://localhost:8000/ws/sensor-stream` and `ws://localhost:8000/ws/inference-stream`.

### 2. Run the Frontend

In a new terminal window, navigate to the `frontend` directory and install NPM packages:

```bash
cd frontend
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

## Architecture Details

- **Sensor Volatility:** Data lines are not drawn with linear approximations; they use an Ornstein-Uhlenbeck process adjusted for phase transitions to introduce organic, physical jitter.
- **Scale-Aware UI:** The core chart employs a dual Y-axis to correctly map temperature data alongside high-volume ppm gas measurements without flattening the visual scale.
- **Adaptive Logging:** During non-fire particulate spikes (e.g., Dust Storms), the ML model temporarily down-weights the smoke sensor to prevent false-positive alarms while logging the variance anomaly explicitly.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
