import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, statusColor, type SubsystemKey } from "@/lib/onyxis/simulation";
import { PageHeader } from "@/components/onyxis/Layout";
import { useEffect, useRef } from "react";

export const Route = createFileRoute("/twin")({
  head: () => ({ meta: [{ title: "Digital Twin — ONYXIS" }] }),
  component: Twin,
});

const NODES: { id: string; label: SubsystemKey | "solar" | "antenna"; x: number; y: number; sub?: SubsystemKey; title: string; sym: string }[] = [
  { id: "solar", label: "solar", x: 50, y: 80, sub: "power", title: "SolarPanel_01", sym: "☀" },
  { id: "battery", label: "power", x: 50, y: 200, sub: "power", title: "Battery_01", sym: "⚡" },
  { id: "pcdu", label: "power", x: 50, y: 320, sub: "power", title: "PCDU_01", sym: "⚡" },
  { id: "obc", label: "obc", x: 50, y: 440, sub: "obc", title: "OBC_01", sym: "🧠" },
  { id: "comm", label: "comm", x: -180, y: 560, sub: "comm", title: "Comm Stack", sym: "📡" },
  { id: "antenna", label: "antenna", x: -180, y: 660, sub: "comm", title: "Antenna_01", sym: "📡" },
  { id: "aocs", label: "aocs", x: 280, y: 560, sub: "aocs", title: "AOCS Stack", sym: "🛰" },
  { id: "thermal", label: "thermal", x: 280, y: 320, sub: "thermal", title: "ThermalZone_01", sym: "🌡" },
  { id: "structure", label: "structure", x: -180, y: 320, sub: "structure", title: "Frame_01", sym: "🏗" },
];

const EDGES: { from: string; to: string; rel: string }[] = [
  { from: "solar", to: "battery", rel: "feedsPowerTo" },
  { from: "battery", to: "pcdu", rel: "feedsPowerTo" },
  { from: "pcdu", to: "obc", rel: "powers" },
  { from: "obc", to: "comm", rel: "controls" },
  { from: "obc", to: "aocs", rel: "controls" },
  { from: "comm", to: "antenna", rel: "connectedTo" },
  { from: "thermal", to: "obc", rel: "monitors" },
  { from: "thermal", to: "battery", rel: "monitors" },
  { from: "structure", to: "battery", rel: "supports" },
  { from: "structure", to: "pcdu", rel: "supports" },
];

function Twin() {
  const { subsystems, faults } = useOnyxis();
  const containerRef = useRef<HTMLDivElement>(null);

  // Generate floating particles once
  useEffect(() => {}, []);

  const center = { x: 400, y: 400 };
  const pos = (n: typeof NODES[number]) => ({ x: center.x + n.x, y: 50 + n.y });

  const subStatus = (sub?: SubsystemKey) => sub ? subsystems[sub].status : "NOMINAL";
  const isFaulted = (sub?: SubsystemKey) => sub ? subsystems[sub].faultIds.length > 0 : false;

  return (
    <div className="space-y-6">
      <PageHeader title="Digital Twin — Ontology Map" subtitle="Semantic Architecture"
        right={<div className="text-xs mono text-muted-foreground">{NODES.length} INDIVIDUALS • {EDGES.length} RELATIONS</div>} />

      <div className="glass-panel relative overflow-hidden h-[78vh]" ref={containerRef}>
        {/* Stars */}
        <div className="absolute inset-0 overflow-hidden">
          {Array.from({ length: 80 }).map((_, i) => {
            const x = (i * 137.5) % 100;
            const y = (i * 73.3) % 100;
            const s = (i % 3) + 1;
            return <div key={i} className="absolute rounded-full bg-white animate-pulse-glow"
              style={{ left: `${x}%`, top: `${y}%`, width: s, height: s, opacity: 0.3 + (i % 5) / 10, animationDelay: `${i * 0.1}s` }} />;
          })}
        </div>
        {/* Orbital ring */}
        <div className="absolute left-1/2 top-1/2 w-[820px] h-[820px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[color:var(--info)]/15"
          style={{ animation: "orbit 80s linear infinite" }}>
          <div className="absolute -top-1 left-1/2 w-2 h-2 rounded-full bg-[color:var(--info)] glow-primary" />
        </div>
        <div className="absolute left-1/2 top-1/2 w-[600px] h-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[color:var(--semantic)]/15"
          style={{ animation: "orbit 60s linear infinite reverse" }} />

        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 800" preserveAspectRatio="xMidYMid meet">
          <defs>
            <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="var(--info)" opacity="0.6" />
            </marker>
          </defs>
          {EDGES.map((e, i) => {
            const f = NODES.find(n => n.id === e.from)!; const t = NODES.find(n => n.id === e.to)!;
            const fp = pos(f); const tp = pos(t);
            const fault = isFaulted(f.sub) && isFaulted(t.sub);
            const color = fault ? "var(--critical)" : "var(--info)";
            return (
              <g key={i}>
                <line x1={fp.x} y1={fp.y} x2={tp.x} y2={tp.y}
                  stroke={color} strokeWidth={fault ? 2 : 1} strokeOpacity={fault ? 0.9 : 0.35}
                  className={fault ? "animate-flow" : ""} markerEnd="url(#arr)" />
                <text x={(fp.x + tp.x) / 2} y={(fp.y + tp.y) / 2 - 4} fill="var(--muted-foreground)"
                  fontSize="9" textAnchor="middle" className="mono select-none">{e.rel}</text>
              </g>
            );
          })}
        </svg>

        {NODES.map(n => {
          const p = pos(n);
          const status = subStatus(n.sub);
          const color = statusColor(status);
          const fault = isFaulted(n.sub);
          return (
            <div key={n.id} className={`absolute ${fault ? "animate-shake" : "animate-float"}`}
              style={{ left: `calc(${(p.x / 800) * 100}% - 38px)`, top: `calc(${(p.y / 800) * 100}% - 38px)` }}>
              <div className="w-[76px] h-[76px] rounded-2xl glass-panel grid place-items-center transition-all"
                style={{ borderColor: `color-mix(in oklab, ${color} 60%, transparent)`,
                         boxShadow: `0 0 ${fault ? 32 : 18}px color-mix(in oklab, ${color} ${fault ? 70 : 40}%, transparent)` }}>
                <span className="text-2xl">{n.sym}</span>
              </div>
              <div className="text-center mt-1">
                <div className="text-[10px] mono font-bold">{n.title}</div>
                <div className="text-[9px] mono" style={{ color }}>{status}</div>
              </div>
            </div>
          );
        })}

        <div className="absolute bottom-4 left-4 glass-panel px-3 py-2 text-[10px] mono space-y-1">
          <div className="text-muted-foreground uppercase tracking-widest mb-1">Legend</div>
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-success" /> Nominal</div>
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-warning" /> Warning</div>
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-critical" /> Critical</div>
        </div>
        <div className="absolute bottom-4 right-4 glass-panel px-3 py-2 text-[10px] mono">
          <div className="text-muted-foreground uppercase tracking-widest">Active Faults</div>
          <div className="text-base font-bold" style={{ color: faults.length ? "var(--critical)" : "var(--success)" }}>{faults.length}</div>
        </div>
      </div>
    </div>
  );
}