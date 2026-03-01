import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { useSimulationStore } from '../store/useSimulationStore';
import './TelemetryMatrix.css';
import { Activity } from 'lucide-react';

export const TelemetryMatrix = () => {
  const telemetryHistory = useSimulationStore((state) => state.telemetryHistory);

  return (
    <div className="telemetry-container">
       <div className="telemetry-header">
         <div className="telemetry-title-group">
            <h2 className="telemetry-title">
               <Activity size={16} color="var(--color-text-muted)" />
               Data Ingestion Pipeline
            </h2>
            <span className="telemetry-subtitle">Real-time Multi-axial Telemetry</span>
         </div>
         <div className="telemetry-legend">
            <div className="legend-item">
               <div className="legend-color" style={{ backgroundColor: 'var(--color-signal-info)' }}></div>
               Gas (ppm)
            </div>
            <div className="legend-item">
               <div className="legend-color" style={{ backgroundColor: 'var(--color-signal-warning)' }}></div>
               Heat (°C)
            </div>
            <div className="legend-item">
               <div className="legend-color" style={{ backgroundColor: '#00E5FF', boxShadow: '0 0 8px #00E5FF' }}></div>
               Smoke (%)
            </div>
         </div>
       </div>

       <div className="telemetry-main-panel">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={telemetryHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid vertical={false} />
              <XAxis 
                dataKey="timestamp" 
                tick={{ fontSize: 10 }}
                tickMargin={12}
                minTickGap={30}
                axisLine={{ stroke: 'var(--color-border-strong)' }}
                tickLine={{ stroke: 'var(--color-border-strong)' }}
              />
              <YAxis 
                yAxisId="left"
                tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
                domain={[0, 'auto']}
                width={60}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 10, fill: 'var(--color-signal-warning)' }}
                domain={[0, 'auto']}
                width={60}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip 
                cursor={{ stroke: 'var(--color-border-strong)', strokeWidth: 1, strokeDasharray: '4 4' }}
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="tooltip-container">
                        <div className="tooltip-header">
                           <span>Index</span>
                           <span style={{ color: 'var(--color-text-primary)' }}>T+{label}s</span>
                        </div>
                        {payload.map((entry, index) => (
                          <div key={index} className="tooltip-row">
                            <span className="tooltip-label">{entry.name}</span>
                            <span className="tooltip-value" style={{ color: entry.color }}>
                              {Number(entry.value).toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="sensors.gas" 
                name="Gas" 
                stroke="var(--color-signal-info)" 
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="sensors.heat" 
                name="Heat" 
                stroke="var(--color-signal-warning)" 
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="sensors.smoke" 
                name="Smoke" 
                stroke="#00E5FF" 
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
       </div>
    </div>
  );
};
