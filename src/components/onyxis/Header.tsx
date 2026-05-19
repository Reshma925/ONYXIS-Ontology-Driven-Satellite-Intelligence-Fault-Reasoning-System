import { useOnyxis, statusColor, fmtUTC } from "@/lib/onyxis/simulation";

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex flex-col items-end leading-tight">
      <span className="text-[9px] uppercase tracking-widest text-muted-foreground">{label}</span>
      <span className="text-xs mono font-semibold" style={{ color: color ?? "var(--foreground)" }}>{value}</span>
    </div>
  );
}

function Dot({ ok, color }: { ok: boolean; color?: string }) {
  return (
    <span
      className="inline-block w-1.5 h-1.5 rounded-full"
      style={{
        background: color ?? (ok ? "var(--success)" : "var(--muted-foreground)"),
        boxShadow: `0 0 8px ${color ?? (ok ? "var(--success)" : "var(--muted-foreground)")}`,
      }}
    />
  );
}

export function Header() {
  const { satellite, now, faults, reasoningLatency, ontologySync, swrl, pellet, semantic, loading, error } = useOnyxis();
  const color = statusColor(satellite);
  const telemetryStatus = error ? "ERROR" : loading ? "CONNECTING" : "STREAMING";
  const telemetryColor = error ? "var(--critical)" : loading ? "var(--warning)" : "var(--success)";

  return (
    <header className="h-16 px-6 flex items-center justify-between border-b border-[color:var(--panel-border)] bg-[oklch(0.2_0.04_250/0.6)] backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <div>
          <div className="text-base font-bold tracking-[0.25em] text-foreground">ONYXIS</div>
          <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Semantic Mission Control</div>
        </div>
      </div>

      <div className="flex items-center gap-3 px-4 py-2 rounded-xl glass-panel"
        style={{ borderColor: `color-mix(in oklab, ${color} 50%, transparent)`, boxShadow: `0 0 24px color-mix(in oklab, ${color} 35%, transparent)` }}>
        <div className="relative">
          <div className="w-2.5 h-2.5 rounded-full animate-pulse-glow" style={{ background: color, boxShadow: `0 0 14px ${color}` }} />
        </div>
        <div className="flex flex-col items-center leading-tight">
          <span className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Satellite Status</span>
          <span className="text-sm font-bold tracking-widest" style={{ color }}>{satellite}</span>
        </div>
        <span className="text-[10px] mono text-muted-foreground border-l border-[color:var(--panel-border)] pl-3">SAT-ONX-1</span>
      </div>

      <div className="flex items-center gap-5">
        <Metric label="UTC Time" value={fmtUTC(now)} />
        <div className="flex items-center gap-2"><Dot ok={!loading && !error} color={telemetryColor} /><Metric label="Telemetry" value={telemetryStatus} color={telemetryColor} /></div>
        <div className="flex items-center gap-2">
          <Dot ok={ontologySync === "SYNCED"} color={ontologySync === "SYNCED" ? "var(--success)" : "var(--warning)"} />
          <Metric label="Ontology" value={ontologySync} color={ontologySync === "SYNCED" ? "var(--success)" : "var(--warning)"} />
        </div>
        <div className="flex items-center gap-2">
          <Dot ok={swrl && ontologySync === "SYNCED"} color={ontologySync === "SYNCED" && swrl ? "var(--success)" : ontologySync === "SYNCING" ? "var(--warning)" : "var(--muted-foreground)"} />
          <Metric
            label="SWRL"
            value={swrl ? ontologySync : "OFF"}
            color={swrl ? (ontologySync === "SYNCED" ? "var(--success)" : "var(--warning)") : "var(--muted-foreground)"}
          />
        </div>
        <div className="flex items-center gap-2">
          <Dot ok={pellet && ontologySync === "SYNCED"} color={ontologySync === "SYNCED" && pellet ? "var(--success)" : ontologySync === "SYNCING" ? "var(--warning)" : "var(--muted-foreground)"} />
          <Metric
            label="Pellet"
            value={pellet ? ontologySync : "OFF"}
            color={pellet ? (ontologySync === "SYNCED" ? "var(--success)" : "var(--warning)") : "var(--muted-foreground)"}
          />
        </div>
        <Metric label="Active Faults" value={String(faults.length)} color={faults.length ? "var(--critical)" : "var(--success)"} />
        <Metric label="Reasoning" value={`${reasoningLatency.toFixed(0)}ms`} color="var(--info)" />
      </div>
    </header>
  );
}