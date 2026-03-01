import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set

# Local imports
from ml_engine.data_generator import get_next_simulation_frame
from ml_engine.fusion_model import predict_fire
from ml_engine.xai_explainer import explain_prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartX-Fire Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State for the simulation
class SimulationState:
    def __init__(self):
        self.is_running = False
        self.scenario_type = "kitchen_cooking"
        self.sensor_clients: Set[WebSocket] = set()
        self.inference_clients: Set[WebSocket] = set()
        self.simulation_task = None
        self.frame_counter = 0

state = SimulationState()

@app.get("/api/v1/system/status")
async def system_status():
    return {
        "status": "online",
        "simulation_active": state.is_running,
        "scenario": state.scenario_type,
        "connected_clients": {
            "sensor": len(state.sensor_clients),
            "inference": len(state.inference_clients)
        }
    }

@app.post("/api/v1/simulation/start")
async def start_simulation(scenario_type: str = "kitchen_cooking"):
    state.scenario_type = scenario_type
    state.frame_counter = 0
    if not state.is_running:
        state.is_running = True
        state.simulation_task = asyncio.create_task(simulation_loop())
    logger.info(f"Simulation started: {scenario_type}")
    return {"message": "Simulation started", "scenario": scenario_type}

@app.post("/api/v1/simulation/stop")
async def stop_simulation():
    state.is_running = False
    if state.simulation_task:
        state.simulation_task.cancel()
        state.simulation_task = None
    logger.info("Simulation stopped")
    return {"message": "Simulation stopped"}

# --- WebSockets ---
@app.websocket("/ws/sensor-stream")
async def websocket_sensor_stream(websocket: WebSocket):
    await websocket.accept()
    state.sensor_clients.add(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.sensor_clients.remove(websocket)

@app.websocket("/ws/inference-stream")
async def websocket_inference_stream(websocket: WebSocket):
    await websocket.accept()
    state.inference_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.inference_clients.remove(websocket)

# --- Background Simulation Loop ---
async def simulation_loop():
    logger.info("Background simulation loop started.")
    last_status = None
    
    try:
        while state.is_running:
            # 1. Generate Data (V5: phase-based)
            raw_data, features, is_anomaly_region = get_next_simulation_frame(state.scenario_type, state.frame_counter)
            state.frame_counter += 1
            phase_name = raw_data.get("phase", "ambient")
            
            # Broadcast Sensor Data
            sensor_payload = {
                "timestamp": raw_data["timestamp"],
                "sensors": {
                    "heat": raw_data["heat"],
                    "smoke": raw_data["smoke"],
                    "gas": raw_data["gas"]
                },
                "phase": phase_name,
                "is_anomaly": is_anomaly_region
            }
            await _broadcast(state.sensor_clients, sensor_payload)

            # 2. ML Inference
            loop = asyncio.get_running_loop()
            prediction, confidence = await loop.run_in_executor(None, predict_fire, features)
            
            # 3. Determine status and generate explanation
            current_status = "FIRE" if prediction == 1 else "SAFE"
            
            if current_status == "FIRE":
                xai_result = await loop.run_in_executor(None, explain_prediction, features, phase_name)
                inference_payload = {
                    "status": "FIRE",
                    "confidence": float(confidence),
                    "phase": phase_name,
                    "xai_explanation": xai_result
                }
                await _broadcast(state.inference_clients, inference_payload)
                last_status = current_status
            elif current_status == "SAFE":
                if last_status == "FIRE" or state.frame_counter % 3 == 0:
                    from ml_engine.xai_explainer import explain_safe
                    safe_xai = explain_safe(features, phase_name)
                    inference_payload = {
                        "status": "SAFE",
                        "confidence": float(confidence),
                        "phase": phase_name,
                        "xai_explanation": safe_xai
                    }
                    await _broadcast(state.inference_clients, inference_payload)
                    last_status = current_status

            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        logger.info("Simulation loop cancelled.")
    except Exception as e:
        logger.error(f"Error in simulation loop: {e}")

async def _broadcast(clients: Set[WebSocket], payload: dict):
    # Create list to avoid RuntimeError if set changes during iteration
    for client in list(clients):
        try:
            await client.send_json(payload)
        except Exception:
            clients.remove(client)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
