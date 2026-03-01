import { useSimulationStore } from '../store/useSimulationStore';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';
import { Database, Network } from 'lucide-react';
import './XaiInterpreter.css';

export const XaiInterpreter = () => {
  const inference = useSimulationStore((state) => state.inference);
  const isConnected = useSimulationStore((state) => state.isConnected);

  const xai = inference.xai_explanation;

  if (!isConnected || !xai) {
    return (
      <div className="xai-standby-panel">
        <Database size={32} className="xai-standby-icon" />
        <p className="xai-standby-text">
          XAI SYSTEM STANDBY
        </p>
      </div>
    );
  }

  const data = Object.entries(xai.top_features).map(([key, value]) => ({
    feature: key.replace('_rolling', '').toUpperCase(),
    value: Math.abs(value as number),
    rawValue: value as number,
    isPositive: (value as number) > 0
  })).sort((a, b) => b.value - a.value).slice(0, 5);

  return (
    <div className="xai-container">
      <div className="xai-header">
        <div className="xai-title-group">
          <Network color="var(--color-text-muted)" size={16} />
          <h3 className="xai-title">Feature Weights</h3>
        </div>
        <span className="xai-version">SHAP Explainer</span>
      </div>

      <div className="xai-chart-area">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 30, right: 20, top: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="var(--color-border-light)" horizontal={true} vertical={false} />
            <XAxis type="number" hide />
            <YAxis 
              dataKey="feature" 
              type="category" 
              stroke="var(--color-text-secondary)" 
              fontFamily="var(--font-mono)"
              fontSize={10} 
              axisLine={false}
              tickLine={false}
              width={100}
            />
            <Tooltip 
              cursor={{ fill: 'var(--color-panel-header)' }}
              content={({ active, payload }: any) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="xai-custom-tooltip">
                      Weight: {payload[0].payload.rawValue.toFixed(4)}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={12}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.isPositive ? 'var(--color-signal-critical)' : 'var(--color-signal-info)'} 
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="xai-interpretation-box">
        <div className="xai-interp-header">
           <span className="xai-interp-title">Interpretive Output</span>
        </div>
        <div className="xai-interp-text">
          {xai.human_readable ? (
            xai.human_readable.split('\n').map((line: string, i: number) => (
              <div key={i} style={{ marginBottom: line.startsWith('•') ? '4px' : '8px' }}>
                {line.startsWith('•') ? (
                   <span style={{ color: 'var(--color-text-secondary)' }}>{line}</span>
                ) : line.startsWith('[') ? (
                   <strong style={{ color: 'var(--color-text-primary)' }}>{line}</strong>
                ) : (
                   line
                )}
              </div>
            ))
          ) : (
            <div>&gt; ANALYZING...</div>
          )}
        </div>
      </div>
    </div>
  );
};
