import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, severityColor, fmtUTC } from "@/lib/onyxis/simulation";
import { getFaultSummary, getRuleLabel } from "@/lib/onyxis/faultSummaries";
import { PageHeader, Panel } from "@/components/onyxis/Layout";

// Use centralized summaries and rule label helpers
const formatFaultSummary = (nameOrRule: string, maybeName?: string) => {
  if (maybeName !== undefined) return getFaultSummary(nameOrRule, maybeName);
  return getFaultSummary(undefined, nameOrRule);
};
const formatRuleLabel = (rule: string, faultName: string) => getRuleLabel(rule, faultName);

export const Route = createFileRoute("/faults")({
  head: () => ({ meta: [{ title: "Active Faults — ONYXIS" }] }),
  component: Faults,
});

function Faults() {
  const { faults } = useOnyxis();
  const sevCounts = {
    CRITICAL: faults.filter(f => f.severity === "CRITICAL").length,
    WARNING: faults.filter(f => f.severity === "WARNING").length,
    SEMANTIC: faults.filter(f => f.severity === "SEMANTIC").length,
    INFO: faults.filter(f => f.severity === "INFO").length,
  };
  return (
    <div className="space-y-6">
      <PageHeader title="Active Faults — Semantic Diagnostics" subtitle="Pellet Inferred"
        right={<div className="flex gap-2">
          {(["CRITICAL","WARNING","SEMANTIC","INFO"] as const).map(s => (
            <span key={s} className="text-[10px] mono px-2 py-1 rounded glass-panel" style={{ color: severityColor(s) }}>
              {s} {sevCounts[s]}
            </span>
          ))}
        </div>} />
      {faults.length === 0 ? (
        <Panel><div className="py-16 text-center"><div className="text-success text-3xl mb-2">◉</div><div className="text-success mono">ALL SYSTEMS NOMINAL</div><div className="text-xs text-muted-foreground mt-1">Pellet reasoner reports no inferred faults across the ontology.</div></div></Panel>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {faults.map(f => (
            <div key={f.id} className="glass-panel p-4 relative overflow-hidden"
              style={{ borderColor: `color-mix(in oklab, ${severityColor(f.severity)} 50%, transparent)`,
                       boxShadow: `0 0 24px color-mix(in oklab, ${severityColor(f.severity)} 25%, transparent)` }}>
              <div className="absolute top-0 left-0 w-1 h-full" style={{ background: severityColor(f.severity), boxShadow: `0 0 12px ${severityColor(f.severity)}` }} />
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] mono px-2 py-0.5 rounded font-bold" style={{ background: severityColor(f.severity), color: "#0b0f1a" }}>{f.severity}</span>
                    <span className="text-[10px] mono px-2 py-0.5 rounded border" style={{ borderColor: severityColor(f.severity), color: severityColor(f.severity) }}>RISK: {f.propagationRisk}</span>
                  </div>
                  <h4 className="text-base font-bold">{f.name}</h4>
                  <div className="text-xs text-muted-foreground mono">on {f.component}</div>
                </div>
                <span className="text-[10px] mono text-muted-foreground">{fmtUTC(f.timestamp)}</span>
              </div>
              <div className="space-y-2 text-xs">
                <Row k="SWRL Rule" v={formatRuleLabel(f.swrlRule, f.name)} mono />
                <Row k="Failure Summary" v={formatFaultSummary(f.swrlRule, f.name)} mono accent />
                <Row k="Telemetry Evidence" v={f.evidence} mono />
                <Row k="hasFault Relation" v={f.hasFault} mono accent />
                <div className="pt-2 border-t border-[color:var(--panel-border)]">
                  <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Ontology Explanation</div>
                  <div className="text-xs leading-relaxed text-foreground/90">{f.explanation}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Row({ k, v, mono, accent }: { k: string; v: string; mono?: boolean; accent?: boolean }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-muted-foreground text-[10px] uppercase tracking-wider">{k}</span>
      <span className={`${mono ? "mono" : ""} text-right ${accent ? "text-semantic" : "text-foreground"} truncate`}>{v}</span>
    </div>
  );
}