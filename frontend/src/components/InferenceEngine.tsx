import { ShieldAlert, ShieldCheck, ZapOff, Activity, ServerCog } from 'lucide-react';
import { useSimulationStore } from '../store/useSimulationStore';
import './InferenceEngine.css';

export const InferenceEngine = () => {
  const inference = useSimulationStore((state) => state.inference);
  const isConnected = useSimulationStore((state) => state.isConnected);

  if (!isConnected) {
    return (
      <div className="inference-container">
        <div className="inference-header">
           <div className="inference-title-group">
              <ServerCog size={16} color="var(--color-text-muted)" />
              <h2 className="inference-title">Risk Classifier</h2>
           </div>
        </div>
        <div className="status-card standby">
           <div className="status-main-row">
             <ZapOff size={32} className="status-icon standby" />
             <div>
                <h3 className="status-text standby">OFFLINE</h3>
                <span className="confidence-label">Awaiting telemetry datalink</span>
             </div>
           </div>
        </div>
      </div>
    );
  }

  const isFire = inference.status === 'FIRE';
  const confidencePercent = (inference.confidence * 100).toFixed(2);

  return (
    <div className="inference-container">
      <div className="inference-header">
         <div className="inference-title-group">
            <ServerCog size={16} color="var(--color-text-muted)" />
            <h2 className="inference-title">Risk Classifier</h2>
         </div>
      </div>

      <div className={`status-card ${isFire ? 'fire' : 'safe'}`}>
        <div className="status-main-row">
          {isFire ? (
            <ShieldAlert size={32} className="status-icon fire" />
          ) : (
             <ShieldCheck size={32} className="status-icon safe" />
          )}
          <h3 className={`status-text ${isFire ? 'fire' : 'safe'}`}>
            {isFire ? 'CRITICAL EVENT' : 'NOMINAL'}
          </h3>
        </div>
        
        <div className="confidence-block">
           <span className="confidence-label">CLASSIFICATION CONFIDENCE</span>
           <div className="confidence-bar-bg">
              <div className={`confidence-bar-fill ${isFire ? 'fire' : 'safe'}`} style={{ width: `${confidencePercent}%` }} />
           </div>
           <span className="confidence-value">{confidencePercent}%</span>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-box">
          <span className="metric-label">Eval Time</span>
          <span className="metric-value">12.4ms</span>
        </div>
        <div className="metric-box">
          <span className="metric-label">Algorithm</span>
          <span className="metric-value">FR-XGB-V10</span>
        </div>
      </div>
    </div>
  );
};
