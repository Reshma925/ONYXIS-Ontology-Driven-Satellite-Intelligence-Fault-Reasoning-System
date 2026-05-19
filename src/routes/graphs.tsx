import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, type SeriesPoint } from "@/lib/onyxis/simulation";
import { PageHeader, Panel } from "@/components/onyxis/Layout";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, AreaChart, Area } from "recharts";
import { useState } from "react";

export const Route = createFileRoute("/graphs")({
  head: () => ({ meta: [{ title: "Telemetry Graphs — ONYXIS" }] }),
  component: Graphs,
});

const GROUPS = {
  "Power": [
    { k: "batteryVoltage", label: "Battery Voltage", unit: "V", color: "var(--info)" },
    { k: "solarOutput", label: "Solar Output", unit: "W", color: "var(--success)" },
    { k: "powerConsumption", label: "Power Consumption", unit: "W", color: "var(--warning)" },
    { k: "busVoltage", label: "Bus Voltage", unit: "V", color: "var(--semantic)" },
  ],
  "Thermal": [
    { k: "internalTemp", label: "Internal Temperature", unit: "°C", color: "var(--warning)" },
    { k: "thermalLoad", label: "Thermal Load", unit: "W", color: "var(--critical)" },
  ],
  "Communication": [
    { k: "signalStrength", label: "Signal Strength", unit: "dBm", color: "var(--info)" },
    { k: "rfPower", label: "RF Output Power", unit: "W", color: "var(--semantic)" },
    { k: "txQuality", label: "Transmission Quality", unit: "%", color: "var(--success)" },
  ],
  "AOCS": [
    { k: "gyroDrift", label: "Gyro Drift", unit: "°/s", color: "var(--warning)" },
    { k: "orientationDev", label: "Orientation Deviation", unit: "°", color: "var(--info)" },
    { k: "rwVibration", label: "Reaction Wheel Health", unit: "g", color: "var(--semantic)" },
  ],
  "OBC": [
    { k: "cpuLoad", label: "CPU Usage", unit: "%", color: "var(--info)" },
    { k: "memoryUsage", label: "Memory Usage", unit: "%", color: "var(--semantic)" },
  ],
  "Structure": [
    { k: "vibration", label: "Vibration", unit: "g", color: "var(--warning)" },
    { k: "structuralStress", label: "Structural Stress", unit: "MPa", color: "var(--critical)" },
  ],
  "Semantic Engine": [
    { k: "reasoningLatency", label: "Reasoning Latency", unit: "s", color: "var(--info)" },
    { k: "activeFaults", label: "Active Fault Count", unit: "", color: "var(--critical)" },
  ],
} as const;

function MiniChart({ data, color, area }: { data: SeriesPoint[]; color: string; area?: boolean }) {
  const C = area ? AreaChart : LineChart;
  return (
    <ResponsiveContainer width="100%" height={140}>
      <C data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id={`g-${color}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.4} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="oklch(0.55 0.12 240 / 0.1)" strokeDasharray="2 4" />
        <XAxis dataKey="t" tickFormatter={t => new Date(t).getUTCSeconds().toString()} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} />
        <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} domain={["auto","auto"]} />
        <Tooltip
          contentStyle={{ background: "oklch(0.18 0.04 250)", border: "1px solid var(--panel-border)", fontSize: 11, borderRadius: 8 }}
          labelFormatter={t => new Date(t as number).toUTCString().split(" ")[4]}
        />
        {area
          ? <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} fill={`url(#g-${color})`} isAnimationActive={false} />
          : <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} isAnimationActive={false} />}
      </C>
    </ResponsiveContainer>
  );
}

function Graphs() {
  const { series } = useOnyxis();
  const groups = Object.keys(GROUPS) as (keyof typeof GROUPS)[];
  const [filter, setFilter] = useState<"All" | keyof typeof GROUPS>("All");
  const visible = filter === "All" ? groups : [filter];
  return (
    <div className="space-y-6">
      <PageHeader title="Telemetry Graphs" subtitle="Live Charts"
        right={<div className="flex flex-wrap gap-2">
          {(["All", ...groups] as const).map(g => (
            <button key={g} onClick={() => setFilter(g)}
              className={`text-[10px] mono uppercase tracking-widest px-3 py-1.5 rounded-md border ${filter === g ? "bg-[oklch(0.78_0.16_240/0.15)] border-[color:var(--info)] text-info" : "border-[color:var(--panel-border)] text-muted-foreground hover:text-foreground"}`}>
              {g}
            </button>
          ))}
        </div>} />
      {visible.map(g => (
        <div key={g}>
          <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-3">{g}</div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            { GROUPS[g].map(s => {
              // Convert reasoning latency from ms -> s for human-friendly display
              const raw = series[s.k] ?? [];
              const data = s.k === "reasoningLatency" ? raw.map(p => ({ ...p, v: (p.v as number) / 1000 })) : raw;
              const last = data[data.length - 1]?.v;
              return (
                <Panel key={s.k} title={s.label} right={<span className="text-xs mono font-bold" style={{ color: s.color }}>{last?.toFixed(2) ?? "--"} {s.unit}</span>}>
                  <MiniChart data={data} color={s.color} area />
                </Panel>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}