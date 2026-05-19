import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { useOnyxis, statusColor, severityColor, fmtUTC, type SubsystemKey } from "@/lib/onyxis/simulation";
import { getFaultSummary, getRuleLabel } from "@/lib/onyxis/faultSummaries";
import { PageHeader, Panel } from "@/components/onyxis/Layout";

const formatFaultSummary = (nameOrRule: string, maybeName?: string) => {
  if (maybeName !== undefined) return getFaultSummary(nameOrRule, maybeName);
  return getFaultSummary(undefined, nameOrRule);
};

const formatRuleLabel = (rule: string, faultName: string) => getRuleLabel(rule, faultName);

export const Route = createFileRoute("/")({
  head: () => ({ meta: [{ title: "Dashboard — ONYXIS" }] }),
  component: Index,
});

function GlobalMetric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="glass-panel px-4 py-3">
      <div className="text-[9px] uppercase tracking-[0.2em] text-muted-foreground">{label}</div>
      <div className="text-lg mono font-bold mt-1" style={{ color: color ?? "var(--foreground)" }}>{value}</div>
    </div>
  );
}

function SubsystemCard({ k }: { k: SubsystemKey }) {
  const { subsystems, faults } = useOnyxis();
  const sub = subsystems[k];
  const subFaults = faults.filter(f => f.subsystem === k);
  const color = statusColor(sub.status);
  const top = Object.entries(sub.metrics).slice(0, 4);
  return (
    <Link to="/faults" className="block group">
      <div
        className={`glass-panel p-4 transition-all duration-300 group-hover:-translate-y-0.5 ${sub.status === "CRITICAL" ? "animate-shake" : ""}`}
        style={{
          borderColor: `color-mix(in oklab, ${color} 40%, transparent)`,
          boxShadow: `0 0 32px color-mix(in oklab, ${color} ${sub.status === "NOMINAL" ? 8 : 25}%, transparent)`,
        }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">{sub.icon}</span>
            <div>
              <div className="text-sm font-semibold">{sub.name}</div>
              <div className="text-[10px] uppercase tracking-widest mono" style={{ color }}>{sub.status}</div>
            </div>
          </div>
          <div className="relative">
            <span className="w-2 h-2 rounded-full block animate-pulse-glow" style={{ background: color, boxShadow: `0 0 10px ${color}` }} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 mb-3">
          {top.map(([key, m]) => (
            <div key={key} className="px-2 py-1.5 rounded bg-[oklch(0.18_0.04_250/0.5)] border border-[color:var(--panel-border)]">
              <div className="text-[9px] uppercase tracking-wider text-muted-foreground truncate">{m.label}</div>
              <div className="text-xs mono font-semibold">{typeof m.value === "number" ? m.value.toFixed(2) : m.value}{m.unit && m.unit !== "OK" && <span className="text-muted-foreground ml-0.5">{m.unit}</span>}</div>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-muted-foreground uppercase tracking-wider">Active Faults</span>
          <span className="mono font-bold" style={{ color: subFaults.length ? "var(--critical)" : "var(--success)" }}>
            {subFaults.length === 0 ? "NONE" : `${subFaults.length} ACTIVE`}
          </span>
        </div>
        {subFaults[0] && (
          <div className="mt-2 text-[10px] mono px-2 py-1 rounded border-l-2"
            style={{ borderLeftColor: severityColor(subFaults[0].severity), background: "oklch(0.18 0.04 250 / 0.5)" }}>
            <span className="text-muted-foreground">{formatRuleLabel(subFaults[0].swrlRule, subFaults[0].name)}</span> → <span style={{ color: severityColor(subFaults[0].severity) }}>{formatFaultSummary(subFaults[0].swrlRule, subFaults[0].name)}</span>
          </div>
        )}
      </div>
    </Link>
  );
}

function Index() {
  const { satellite, faults, reasoningLatency, subsystems, ontologySync, scenario } = useOnyxis();
  const subKeys: SubsystemKey[] = ["power","thermal","comm","aocs","obc","structure"];
  const semanticAlerts = faults.slice(0, 5);
  const healthScore = Math.max(0, 100 - faults.reduce((a, f) => a + (f.severity === "CRITICAL" ? 18 : f.severity === "WARNING" ? 8 : 3), 0));
  return (
    <div className="space-y-6">
      <PageHeader title="Mission Operations Overview" subtitle="Dashboard"
        right={<div className="text-xs mono text-muted-foreground">SCENARIO: <span className="text-info font-semibold">{scenario}</span></div>} />

      <div className="glass-panel p-5 relative overflow-hidden">
        <div className="absolute inset-0 grid-bg opacity-30" />
        <div className="relative grid grid-cols-2 md:grid-cols-6 gap-3">
          <GlobalMetric label="Mission Status" value={satellite} color={statusColor(satellite)} />
          <GlobalMetric label="Health Score" value={`${healthScore}%`} color={healthScore > 70 ? "var(--success)" : healthScore > 40 ? "var(--warning)" : "var(--critical)"} />
          <GlobalMetric label="Active Faults" value={String(faults.length)} color={faults.length ? "var(--critical)" : "var(--success)"} />
          <GlobalMetric label="Reasoning Latency" value={`${reasoningLatency.toFixed(0)} ms`} color="var(--info)" />
          <GlobalMetric label="Ontology Sync" value={ontologySync} color="var(--success)" />
          <GlobalMetric label="Subsystems" value={`${Object.values(subsystems).filter(s => s.status === "NOMINAL").length}/6 OK`} color="var(--success)" />
        </div>
      </div>

      <div>
        <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-3">Subsystem Telemetry</div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {subKeys.map(k => <SubsystemCard key={k} k={k} />)}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Active Semantic Alerts" className="lg:col-span-2">
          {semanticAlerts.length === 0 ? (
            <div className="text-sm text-muted-foreground py-8 text-center">
              <span className="text-success mono">◉ ALL SYSTEMS NOMINAL</span><br />
              <span className="text-[11px]">No semantic faults inferred by Pellet.</span>
            </div>
          ) : (
            <ul className="space-y-2">
              {semanticAlerts.map(f => (
                <li key={f.id} className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[oklch(0.18_0.04_250/0.5)] border-l-2"
                  style={{ borderLeftColor: severityColor(f.severity) }}>
                  <span className="mono text-[10px] px-2 py-0.5 rounded" style={{ background: severityColor(f.severity), color: "#0b0f1a" }}>{f.severity}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold truncate">{formatFaultSummary(f.swrlRule, f.name)} <span className="text-muted-foreground font-normal">on {f.component}</span></div>
                    <div className="text-[10px] mono text-muted-foreground truncate">{formatRuleLabel(f.swrlRule, f.name)} • {f.evidence}</div>
                  </div>
                  <span className="text-[10px] mono text-muted-foreground">{fmtUTC(f.timestamp)}</span>
                </li>
              ))}
            </ul>
          )}
        </Panel>
        <Panel title="System Health Overview">
          <div className="space-y-3">
            {subKeys.map(k => {
              const s = subsystems[k];
              const c = statusColor(s.status);
              const pct = s.status === "NOMINAL" ? 100 : s.status === "DEGRADED" ? 75 : s.status === "WARNING" ? 50 : 25;
              return (
                <div key={k}>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>{s.icon} {s.name}</span>
                    <span className="mono" style={{ color: c }}>{s.status}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[oklch(0.3_0.05_250/0.5)] overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: c, boxShadow: `0 0 8px ${c}` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Panel>
      </div>
    </div>
  );
}
