import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { fetchOntologyState, postOntologyControl } from "./ontologyApi";

export type Severity = "INFO" | "WARNING" | "CRITICAL" | "SEMANTIC";
export type SubsystemStatus = "NOMINAL" | "DEGRADED" | "WARNING" | "CRITICAL" | "OFFLINE";
export type SatelliteStatus =
  | "NOMINAL" | "DEGRADED" | "WARNING" | "CRITICAL"
  | "SAFE MODE" | "EMERGENCY" | "OFFLINE" | "INITIALIZING"
  | "MAINTENANCE" | "UNKNOWN";

export type Scenario =
  | "Normal Operation" | "Battery Drain" | "Thermal Overload"
  | "Signal Loss" | "Cascading Failure";

export interface Fault {
  id: string;
  name: string;
  severity: Severity;
  component: string;
  swrlRule: string;
  evidence: string;
  propagationRisk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  timestamp: number;
  explanation: string;
  hasFault: string;
  subsystem: SubsystemKey;
}

export interface LogEntry {
  id: string;
  timestamp: number;
  category: "Ontology" | "SWRL" | "Pellet" | "Fault" | "Propagation" | "System" | "User" | "Telemetry";
  severity: Severity;
  message: string;
}

export interface TelemetryTick {
  id: string;
  timestamp: number;
  channel: string;
  value: string;
  unit: string;
}

export type SubsystemKey = "power" | "thermal" | "comm" | "aocs" | "obc" | "structure";

export interface SubsystemState {
  key: SubsystemKey;
  name: string;
  icon: string;
  status: SubsystemStatus;
  metrics: Record<string, { value: number; unit: string; nominal?: [number, number]; label: string }>;
  faultIds: string[];
}

export interface SeriesPoint { t: number; [k: string]: number; }

const API_POLL_BASE = 1200;

function initSubsystems(): Record<SubsystemKey, SubsystemState> {
  return {
    power: {
      key: "power",
      name: "Power System",
      icon: "⚡",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        batteryVoltage: { value: 0, unit: "V", nominal: [26, 29.5], label: "Battery Voltage" },
        batteryTemp: { value: 0, unit: "°C", nominal: [10, 35], label: "Battery Temp" },
        batteryCharge: { value: 0, unit: "%", nominal: [40, 100], label: "Charge Level" },
        dischargeRate: { value: 0, unit: "A", nominal: [0, 3.5], label: "Discharge Rate" },
        solarIrradiance: { value: 0, unit: "W/m²", nominal: [800, 1400], label: "Solar Irradiance" },
        solarOutput: { value: 0, unit: "W", nominal: [200, 400], label: "Solar Output" },
        powerConsumption: { value: 0, unit: "W", nominal: [150, 350], label: "Power Consumption" },
        pcduOutput: { value: 0, unit: "V", nominal: [27.5, 28.5], label: "PCDU Output" },
        busVoltage: { value: 0, unit: "V", nominal: [27.5, 28.5], label: "Bus Voltage" },
      },
    },
    thermal: {
      key: "thermal",
      name: "Thermal System",
      icon: "🌡",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        internalTemp: { value: 0, unit: "°C", nominal: [15, 30], label: "Internal Temp" },
        thermalLoad: { value: 0, unit: "W", nominal: [100, 280], label: "Thermal Load" },
        heaterOutput: { value: 0, unit: "W", nominal: [0, 120], label: "Heater Output" },
        sensorState: { value: 0, unit: "OK", label: "Sensor State" },
        coolingEfficiency: { value: 0, unit: "%", nominal: [80, 100], label: "Cooling Eff." },
        componentTemp: { value: 0, unit: "°C", nominal: [10, 55], label: "Component Temp" },
      },
    },
    comm: {
      key: "comm",
      name: "Communication",
      icon: "📡",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        signalStrength: { value: 0, unit: "dBm", nominal: [-80, -50], label: "Signal Strength" },
        txQuality: { value: 0, unit: "%", nominal: [85, 100], label: "TX Quality" },
        antennaAlignment: { value: 0, unit: "°", nominal: [0, 1.5], label: "Antenna Align" },
        ttcStatus: { value: 0, unit: "OK", label: "TTC Status" },
        rfPower: { value: 0, unit: "W", nominal: [12, 22], label: "RF Output" },
        encQuality: { value: 0, unit: "%", nominal: [95, 100], label: "Encoding Q." },
        decoderError: { value: 0, unit: "%", nominal: [0, 0.5], label: "Decoder Err" },
        uplinkStatus: { value: 0, unit: "OK", label: "Uplink" },
      },
    },
    aocs: {
      key: "aocs",
      name: "AOCS",
      icon: "🛰",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        gyroDrift: { value: 0, unit: "°/s", nominal: [0, 0.1], label: "Gyro Drift" },
        angularRate: { value: 0, unit: "°/s", nominal: [0, 2], label: "Angular Rate" },
        orientationDev: { value: 0, unit: "°", nominal: [0, 1.5], label: "Orientation Dev" },
        rwVibration: { value: 0, unit: "g", nominal: [0, 0.3], label: "Reaction Wheel Health" },
        starTrackerErr: { value: 0, unit: "arcsec", nominal: [0, 50], label: "Star Tracker Err" },
        gnssError: { value: 0, unit: "m", nominal: [0, 8], label: "GNSS Error" },
        magnetometer: { value: 0, unit: "OK", label: "Magnetometer" },
        thrusterState: { value: 0, unit: "OK", label: "Thrusters" },
      },
    },
    obc: {
      key: "obc",
      name: "OBC System",
      icon: "🧠",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        cpuLoad: { value: 0, unit: "%", nominal: [10, 75], label: "CPU Load" },
        memoryUsage: { value: 0, unit: "%", nominal: [20, 80], label: "Memory" },
        processingLoad: { value: 0, unit: "%", nominal: [10, 70], label: "Processing" },
        dataThroughput: { value: 0, unit: "Mbps", nominal: [2, 25], label: "Throughput" },
        taskQueue: { value: 0, unit: "", nominal: [0, 50], label: "Task Queue" },
        obcTemp: { value: 0, unit: "°C", nominal: [10, 55], label: "OBC Temp" },
      },
    },
    structure: {
      key: "structure",
      name: "Structure",
      icon: "🏗",
      status: "NOMINAL",
      faultIds: [],
      metrics: {
        structuralStress: { value: 0, unit: "MPa", nominal: [0, 60], label: "Stress" },
        vibration: { value: 0, unit: "g", nominal: [0, 0.25], label: "Vibration" },
        mountStability: { value: 0, unit: "%", nominal: [95, 100], label: "Mount Stab." },
        frameIntegrity: { value: 0, unit: "%", nominal: [98, 100], label: "Frame Int." },
        panelStability: { value: 0, unit: "%", nominal: [95, 100], label: "Panel Stab." },
      },
    },
  };
}

interface OnyxisState {
  bootedAt: number;
  now: number;
  satellite: SatelliteStatus;
  subsystems: Record<SubsystemKey, SubsystemState>;
  faults: Fault[];
  logs: LogEntry[];
  telemetry: TelemetryTick[];
  series: Record<string, SeriesPoint[]>;
  scenario: Scenario;
  setScenario: (s: Scenario) => void;
  pellet: boolean; setPellet: (b: boolean) => void;
  swrl: boolean; setSwrl: (b: boolean) => void;
  semantic: boolean; setSemantic: (b: boolean) => void;
  propagation: boolean; setPropagation: (b: boolean) => void;
  speed: number; setSpeed: (n: number) => void;
  reasoningLatency: number;
  ontologySync: "SYNCED" | "SYNCING" | "DESYNCED";
  loading: boolean;
  error: string | null;
  reset: () => void;
  resyncOntology: () => void;
  runReasoning: () => void;
  individuals: string[];
  inferredClasses: string[];
  swrlRules: { id: string; name: string; condition: string; active: boolean }[];
  backendAvailable: boolean;
}

const Ctx = createContext<OnyxisState | null>(null);

export function useOnyxis() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useOnyxis must be inside OnyxisProvider");
  return v;
}

const DEFAULT_STATE: Omit<OnyxisState, "setScenario" | "setPellet" | "setSwrl" | "setSemantic" | "setPropagation" | "setSpeed" | "reset" | "resyncOntology" | "runReasoning"> = {
  bootedAt: Date.now(),
  now: Date.now(),
  satellite: "UNKNOWN",
  subsystems: initSubsystems(),
  faults: [],
  logs: [],
  telemetry: [],
  series: {},
  scenario: "Normal Operation",
  pellet: true,
  swrl: true,
  semantic: true,
  propagation: true,
  speed: 1,
  reasoningLatency: 0,
  ontologySync: "DESYNCED",
  loading: true,
  error: null,
  individuals: [],
  inferredClasses: [],
  swrlRules: [],
  backendAvailable: false,
};

export function OnyxisProvider({ children }: { children: React.ReactNode }) {
  const [bootedAt] = useState(DEFAULT_STATE.bootedAt);
  const [state, setState] = useState(DEFAULT_STATE);
  const [speed, setSpeed] = useState(1);
  const [loading, setLoading] = useState(DEFAULT_STATE.loading);
  const [error, setError] = useState<string | null>(DEFAULT_STATE.error);
  const [backendAvailable, setBackendAvailable] = useState(DEFAULT_STATE.backendAvailable);
  const mountedRef = useRef(true);

  const loadState = async () => {
    if (!mountedRef.current) return;
    setLoading(true);
    try {
      const response = await fetchOntologyState();
      if (!mountedRef.current) return;
      setState(prev => ({ ...prev, ...response }));
      setError(null);
      setBackendAvailable(true);
    } catch (err) {
      if (!mountedRef.current) return;
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      // When backend disconnects, CLEAR state entirely - don't show stale data
      setState(DEFAULT_STATE);
      setBackendAvailable(false);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  useEffect(() => {
    mountedRef.current = true;
    loadState();
    const intervalId = window.setInterval(loadState, Math.max(250, API_POLL_BASE / speed));
    return () => {
      mountedRef.current = false;
      window.clearInterval(intervalId);
    };
  }, [speed]);

  const sendControl = async (action: string, payload?: Record<string, unknown>) => {
    try {
      await postOntologyControl(action, payload);
      await loadState();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const setScenario = (scenario: Scenario) => {
    sendControl("scenario", { scenario });
  };

  const setPellet = (value: boolean) => {
    sendControl("toggle", { name: "pellet", value });
  };

  const setSwrl = (value: boolean) => {
    sendControl("toggle", { name: "swrl", value });
  };

  const setSemantic = (value: boolean) => {
    sendControl("toggle", { name: "semantic", value });
  };

  const setPropagation = (value: boolean) => {
    sendControl("toggle", { name: "propagation", value });
  };

  const reset = () => {
    sendControl("reset");
  };

  const resyncOntology = () => {
    sendControl("resync");
  };

  const runReasoning = () => {
    sendControl("reason");
  };

  const value: OnyxisState = {
    bootedAt,
    now: state.now,
    satellite: state.satellite,
    subsystems: state.subsystems,
    faults: state.faults,
    logs: state.logs,
    telemetry: state.telemetry,
    series: state.series,
    scenario: state.scenario as Scenario,
    setScenario,
    pellet: state.pellet,
    setPellet,
    swrl: state.swrl,
    setSwrl,
    semantic: state.semantic,
    setSemantic,
    propagation: state.propagation,
    setPropagation,
    speed,
    setSpeed,
    reasoningLatency: state.reasoningLatency,
    ontologySync: state.ontologySync,
    loading,
    error,
    reset,
    resyncOntology,
    runReasoning,
    individuals: state.individuals,
    inferredClasses: state.inferredClasses,
    swrlRules: state.swrlRules,
    backendAvailable,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function statusColor(status: SatelliteStatus | SubsystemStatus) {
  switch (status) {
    case "NOMINAL":
      return "text-emerald-500";
    case "DEGRADED":
      return "text-amber-500";
    case "WARNING":
      return "text-orange-500";
    case "CRITICAL":
      return "text-red-500";
    case "SAFE MODE":
    case "EMERGENCY":
    case "OFFLINE":
      return "text-red-600";
    case "INITIALIZING":
    case "MAINTENANCE":
      return "text-sky-500";
    default:
      return "text-slate-500";
  }
}

export function severityColor(severity: Severity) {
  switch (severity) {
    case "INFO":
      return "text-slate-500";
    case "WARNING":
      return "text-amber-500";
    case "CRITICAL":
      return "text-red-500";
    case "SEMANTIC":
      return "text-cyan-500";
    default:
      return "text-slate-500";
  }
}

export function fmtUTC(timestamp: number) {
  return new Date(timestamp).toISOString().replace("T", " ").replace("Z", " UTC");
}
