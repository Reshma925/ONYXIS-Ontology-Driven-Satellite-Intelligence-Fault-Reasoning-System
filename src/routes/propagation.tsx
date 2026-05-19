import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, severityColor } from "@/lib/onyxis/simulation";
import { PageHeader, Panel } from "@/components/onyxis/Layout";

export const Route = createFileRoute("/propagation")({
  head: () => ({ meta: [{ title: "Propagation — ONYXIS" }] }),
  component: Propagation,
});

const CHAINS: { id: string; trigger: string; chain: string[]; rel: string[] }[] = [
  { id: "C1", trigger: "SolarFault", chain: ["SolarPanel_01", "Battery_01", "PCDU_01", "OBC_01"], rel: ["feedsPowerTo","feedsPowerTo","powers"] },
  { id: "C2", trigger: "BatteryFault", chain: ["Battery_01", "PCDU_01", "Comm_Stack", "Antenna_01"], rel: ["feedsPowerTo","powers","connectedTo"] },
  { id: "C3", trigger: "OverheatFault", chain: ["ThermalZone_01", "OBC_01", "AOCS_Stack"], rel: ["affects","controls"] },
  { id: "C4", trigger: "GyroFault", chain: ["Gyro_01", "AOCS_Stack", "ReactionWheel_01"], rel: ["dependsOn","controls"] },
];

function Propagation() {
  const { faults } = useOnyxis();
  const activeTriggers = new Set(faults.map(f => f.name));

  return (
    <div className="space-y-6">
      <PageHeader title="Semantic Fault Propagation" subtitle="Causal Graph"
        right={<div className="text-xs mono text-muted-foreground">{CHAINS.filter(c => activeTriggers.has(c.trigger)).length} ACTIVE CHAINS</div>} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {CHAINS.map(c => {
          const active = activeTriggers.has(c.trigger);
          const risk = active ? (c.chain.length >= 4 ? "CRITICAL" : "HIGH") : "LOW";
          const riskColor = active ? "var(--critical)" : "var(--muted-foreground)";
          return (
            <Panel key={c.id}
              title={`Chain ${c.id} • ${c.trigger}`}
              right={<span className="text-[10px] mono px-2 py-0.5 rounded border" style={{ color: riskColor, borderColor: riskColor }}>RISK {risk}</span>}>
              <div className="flex flex-col gap-2">
                {c.chain.map((node, i) => (
                  <div key={node} className="flex items-center gap-3">
                    <div className="flex-1 px-3 py-2 rounded-lg border mono text-xs"
                      style={{
                        borderColor: active ? severityColor("CRITICAL") : "var(--panel-border)",
                        background: active ? "color-mix(in oklab, var(--critical) 8%, transparent)" : "oklch(0.18 0.04 250 / 0.5)",
                        boxShadow: active ? `0 0 16px color-mix(in oklab, var(--critical) ${30 - i * 5}%, transparent)` : "none",
                      }}>
                      <div className="flex items-center justify-between">
                        <span className="font-bold">{node}</span>
                        <span className="text-[9px] uppercase tracking-widest" style={{ color: active ? "var(--critical)" : "var(--muted-foreground)" }}>
                          {active ? "AFFECTED" : "stable"}
                        </span>
                      </div>
                    </div>
                  </div>
                )).reduce((acc: React.ReactNode[], el, i, arr) => {
                  acc.push(el);
                  if (i < arr.length - 1) acc.push(
                    <div key={`arr-${i}`} className="flex items-center gap-2 pl-3">
                      <span className={`text-info ${active ? "animate-pulse-glow" : "opacity-40"}`}>↓</span>
                      <span className="text-[9px] mono uppercase tracking-widest text-muted-foreground">{c.rel[i]}</span>
                    </div>
                  );
                  return acc;
                }, [])}
              </div>
            </Panel>
          );
        })}
      </div>

      <Panel title="Recent Propagation Events">
        <ul className="space-y-1 text-xs mono">
          {faults.filter(f => f.propagationRisk === "HIGH" || f.propagationRisk === "CRITICAL").length === 0 && (
            <li className="text-muted-foreground">No active propagation events.</li>
          )}
          {faults.filter(f => f.propagationRisk === "HIGH" || f.propagationRisk === "CRITICAL").map(f => (
            <li key={f.id} className="flex items-center gap-3 px-3 py-2 rounded border-l-2"
              style={{ borderLeftColor: "var(--critical)", background: "oklch(0.18 0.04 250 / 0.5)" }}>
              <span className="text-critical">⚠</span>
              <span>{f.name}</span>
              <span className="text-muted-foreground">propagated from</span>
              <span className="text-info">{f.component}</span>
              <span className="ml-auto text-[10px] text-muted-foreground">risk={f.propagationRisk}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}