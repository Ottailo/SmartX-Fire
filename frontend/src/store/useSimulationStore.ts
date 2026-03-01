import { create } from 'zustand';

export interface SensorData {
  heat: number;
  smoke: number;
  gas: number;
}

export interface TelemetryFrame {
  timestamp: number;
  sensors: SensorData;
  is_anomaly: boolean;
}

export interface XaiExplanation {
  top_features: Record<string, number>;
  human_readable: string;
}

export interface InferenceStatus {
  status: 'SAFE' | 'FIRE' | 'OFFLINE';
  confidence: number;
  xai_explanation: XaiExplanation | null;
}

interface SimulationState {
  isConnected: boolean;
  systemStatus: {
    simulation_active: boolean;
    scenario: string;
  };
  telemetryHistory: TelemetryFrame[];
  inference: InferenceStatus;
  
  // Actions
  addTelemetry: (frame: TelemetryFrame) => void;
  setInference: (status: InferenceStatus) => void;
  setConnectionStatus: (status: boolean) => void;
  setSystemStatus: (active: boolean, scenario: string) => void;
  resetSimulation: () => void;
}

const MAX_HISTORY = 60; // Keep 60 seconds of data

export const useSimulationStore = create<SimulationState>((set) => ({
  isConnected: false,
  systemStatus: {
    simulation_active: false,
    scenario: 'none'
  },
  telemetryHistory: [],
  inference: {
    status: 'OFFLINE',
    confidence: 0,
    xai_explanation: null
  },
  
  addTelemetry: (frame) => set((state) => {
    const newHistory = [...state.telemetryHistory, frame];
    if (newHistory.length > MAX_HISTORY) {
      newHistory.shift(); // Remove oldest
    }
    return { telemetryHistory: newHistory };
  }),
  
  setInference: (status) => set({ inference: status }),
  setConnectionStatus: (status) => set({ isConnected: status }),
  setSystemStatus: (active, scenario) => set({ systemStatus: { simulation_active: active, scenario } }),
  
  resetSimulation: () => set({
    telemetryHistory: [],
    inference: { status: 'OFFLINE', confidence: 0, xai_explanation: null }
  })
}));
