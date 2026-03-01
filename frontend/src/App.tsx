import { useEffect, useRef } from 'react';
import { TelemetryMatrix } from './components/TelemetryMatrix';
import { InferenceEngine } from './components/InferenceEngine';
import { XaiInterpreter } from './components/XaiInterpreter';
import { useSimulationStore } from './store/useSimulationStore';
import { Cpu, Settings, Power } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000/ws';

function App() {
  const { 
    addTelemetry, 
    setInference, 
    setConnectionStatus, 
    setSystemStatus,
    systemStatus,
    resetSimulation
  } = useSimulationStore();

  const sensorWsRef = useRef<WebSocket | null>(null);
  const inferenceWsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/system/status`)
      .then(res => res.json())
      .then(data => {
        setSystemStatus(data.simulation_active, data.scenario);
      }).catch(console.error);

    sensorWsRef.current = new WebSocket(`${WS_BASE}/sensor-stream`);
    inferenceWsRef.current = new WebSocket(`${WS_BASE}/inference-stream`);

    sensorWsRef.current.onopen = () => setConnectionStatus(true);
    sensorWsRef.current.onclose = () => setConnectionStatus(false);

    sensorWsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      addTelemetry(data);
    };

    inferenceWsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setInference(data);
    };

    return () => {
      sensorWsRef.current?.close();
      inferenceWsRef.current?.close();
    };
  }, []);

  const handleStart = async (scenario: string) => {
    resetSimulation();
    await fetch(`${API_BASE}/simulation/start?scenario_type=${scenario}`, { method: 'POST' });
    setSystemStatus(true, scenario);
  };

  const handleStop = async () => {
    await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' });
    setSystemStatus(false, 'none');
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand-group">
          <div className="brand-icon">
             <Cpu size={20} />
          </div>
          <div>
            <h1 className="brand-title">
              SMARTX FIRE
            </h1>
            <p className="brand-subtitle">
              Adaptive Event Simulation System v2.0
            </p>
          </div>
        </div>

        <div className="status-group">
           <div className="status-item">
              <span className="status-label">Engine Status</span>
              <span className="status-value">
                 <div className={`status-dot ${systemStatus.simulation_active ? 'active' : 'offline'}`} />
                 Running
              </span>
           </div>
           <div className="status-item">
              <span className="status-label">Connection</span>
              <span className="status-value" style={{ color: systemStatus.simulation_active ? 'var(--color-signal-nominal)' : 'var(--color-signal-warning)' }}>
                {systemStatus.simulation_active ? 'ACTIVE' : 'STANDBY'}
              </span>
           </div>
        </div>
      </header>

      <main className="main-content">
        
        <div className="controls-section">
          <div className="controls-label">
            <Settings size={14} />
            Scenarios
          </div>
          
          <div className="scenario-grid">
            <button onClick={() => handleStart('kitchen_cooking')} className={`btn-outline ${systemStatus.scenario === 'kitchen_cooking' ? 'active' : ''}`}>
              <span className="btn-subtext">01</span>
              <span>Kitchen Ops (Cooking)</span>
            </button>
            <button onClick={() => handleStart('dust_storm')} className={`btn-outline ${systemStatus.scenario === 'dust_storm' ? 'active' : ''}`}>
              <span className="btn-subtext">02</span>
              <span>Dust Anomaly</span>
            </button>
            <button onClick={() => handleStart('electrical_fire')} className={`btn-outline ${systemStatus.scenario === 'electrical_fire' ? 'active-critical' : ''}`}>
              <span className="btn-subtext" style={{ color: 'var(--color-signal-critical)' }}>03 / CRITICAL</span>
              <span>Electrical Fire</span>
            </button>
          </div>

          <div className="action-group">
            <button onClick={handleStop} className="btn-danger" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Power size={14} />
              Halt
            </button>
          </div>
        </div>

        <div className="panel telemetry">
            <TelemetryMatrix />
        </div>

        <div className="right-sidebar">
            <div className="panel inference">
                <InferenceEngine />
            </div>
            
            <div className="panel xai">
                <XaiInterpreter />
            </div>
        </div>

      </main>

      <footer className="footer">
         <div>USER: ADMIN | LATENCY: 12ms</div>
         <div>(C) 2026 GE SECURITY SYSTEMS</div>
      </footer>
    </div>
  );
}

export default App;
