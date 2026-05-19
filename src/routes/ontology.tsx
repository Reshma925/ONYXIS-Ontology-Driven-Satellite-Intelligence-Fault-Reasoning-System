import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis } from "@/lib/onyxis/simulation";
import { fetchOntologyInspect } from "@/lib/onyxis/ontologyApi";
import { PageHeader, Panel } from "@/components/onyxis/Layout";
import { useState, useMemo, useEffect } from "react";

export const Route = createFileRoute("/ontology")({
  head: () => ({ meta: [{ title: "Ontology Inspector — ONYXIS" }] }),
  component: Ontology,
});

function Ontology() {
  const { individuals, inferredClasses, swrlRules, faults, ontologySync, pellet, reasoningLatency, swrl, logs, telemetry, scenario } = useOnyxis();
  const [inspect, setInspect] = useState<null | {
    classes: string[];
    subclasses: string[];
    individuals: string[];
    datatypeProperties: string[];
    objectProperties: string[];
    swrlRules: Array<{ id: string; name: string; condition: string; active: boolean }>;
  }>(null);
  const [inspectError, setInspectError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const filteredInd = useMemo(() => individuals.filter(i => i.toLowerCase().includes(q.toLowerCase())), [individuals, q]);
  const visibleLogs = useMemo(
    () => logs.filter(entry => entry.category === "Ontology" || entry.category === "Pellet" || entry.category === "SWRL").slice(-6).reverse(),
    [logs]
  );
  const lastTelemetry = telemetry.length > 0 ? telemetry[telemetry.length - 1] : null;

  useEffect(() => {
    let active = true;
    fetchOntologyInspect()
      .then(data => {
        if (active) setInspect(data as any);
      })
      .catch(error => {
        if (active) setInspectError(error?.message ?? String(error));
      });
    return () => {
      active = false;
    };
  }, [ontologySync, individuals.length, swrlRules.length]);

  return (
    <div className="space-y-6">
      <PageHeader title="Ontology Inspector" subtitle="OWL Runtime"
        right={<div className="flex gap-3 text-xs mono">
          <span><span className="text-muted-foreground">SYNC</span> <span className="text-success">{ontologySync}</span></span>
            <span><span className="text-muted-foreground">PELLET</span> <span className={pellet ? (ontologySync === "SYNCED" ? "text-success" : "text-muted-foreground") : "text-muted-foreground"}>{pellet ? ontologySync : "OFF"}</span></span>
            <span><span className="text-muted-foreground">SWRL</span> <span className={swrl ? (ontologySync === "SYNCED" ? "text-success" : "text-muted-foreground") : "text-muted-foreground"}>{swrl ? ontologySync : "OFF"}</span></span>
          <span><span className="text-muted-foreground">LATENCY</span> <span className="text-info">{reasoningLatency.toFixed(0)}ms</span></span>
        </div>} />

      <input
        value={q} onChange={e => setQ(e.target.value)}
        placeholder="Search individuals, classes, properties…"
        className="w-full px-4 py-3 rounded-lg glass-panel text-sm mono placeholder:text-muted-foreground outline-none focus:ring-1 focus:ring-[color:var(--info)]"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title={`Active Individuals (${filteredInd.length})`}>
          <ul className="space-y-1 max-h-[60vh] overflow-y-auto">
            {filteredInd.map(i => (
              <li key={i} className="px-3 py-1.5 rounded text-xs mono hover:bg-[oklch(0.78_0.16_240/0.05)] flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-info" />
                <span>{i}</span>
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title={`Inferred Classes (${inferredClasses.length})`}>
          <ul className="space-y-1 max-h-[60vh] overflow-y-auto">
            {inferredClasses.map(c => (
              <li key={c} className="px-3 py-1.5 rounded text-xs mono hover:bg-[oklch(0.65_0.22_290/0.08)] flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-semantic" />
                <span>owl:{c}</span>
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title={`hasFault Relationships (${faults.length})`}>
          {faults.length === 0 ? (
            <div className="text-xs text-muted-foreground">No hasFault triples currently inferred.</div>
          ) : (
            <ul className="space-y-1 max-h-[60vh] overflow-y-auto">
              {faults.map(f => (
                <li key={f.id} className="px-3 py-2 rounded text-xs mono bg-[oklch(0.65_0.22_290/0.08)] border-l-2 border-semantic">
                  <span className="text-info">{f.component}</span> <span className="text-muted-foreground">hasFault</span> <span className="text-critical">{f.name}</span>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>

      <Panel title="Runtime Reasoning Snapshot">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">Scenario</div>
            <div className="font-semibold">{scenario}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">Ontology Sync</div>
            <div className="font-semibold">{ontologySync}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">Reasoning Latency</div>
            <div className="font-semibold">{reasoningLatency.toFixed(0)} ms</div>
          </div>
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">Pellet Reasoner</div>
            <div className="font-semibold">{pellet ? "ON" : "OFF"}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">SWRL Rules</div>
            <div className="font-semibold">{swrl ? "ENABLED" : "DISABLED"}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
            <div className="text-muted-foreground mb-1">Latest Telemetry</div>
            {lastTelemetry ? (
              <div className="font-semibold">{lastTelemetry.channel}: {lastTelemetry.value}{lastTelemetry.unit ? ` ${lastTelemetry.unit}` : ""}</div>
            ) : (
              <div className="text-xs text-muted-foreground">Waiting for telemetry…</div>
            )}
          </div>
        </div>
      </Panel>

      <Panel title={`Ontology Catalog ${inspect ? `(${inspect.classes.length} classes, ${inspect.objectProperties.length} object props)` : ""}`}>
        {inspectError ? (
          <div className="text-sm text-destructive">Failed to load inspect data: {inspectError}</div>
        ) : inspect ? (
          <div className="space-y-3 text-xs mono">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
                <div className="text-muted-foreground mb-1">Classes</div>
                <div className="font-semibold">{inspect.classes.length}</div>
              </div>
              <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
                <div className="text-muted-foreground mb-1">Individuals</div>
                <div className="font-semibold">{inspect.individuals.length}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
                <div className="text-muted-foreground mb-1">Object Properties</div>
                <div className="font-semibold">{inspect.objectProperties.length}</div>
              </div>
              <div className="rounded-lg border border-[color:var(--panel-border)] p-3">
                <div className="text-muted-foreground mb-1">Datatype Properties</div>
                <div className="font-semibold">{inspect.datatypeProperties.length}</div>
              </div>
            </div>
            <div className="rounded-lg border border-[color:var(--panel-border)] p-3 bg-[oklch(0.95_0.06_250/0.4)]">
              <div className="text-muted-foreground mb-1">Loaded SWRL Rules</div>
              <div className="font-semibold">{inspect.swrlRules.length}</div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">Loading inspect data…</div>
        )}
      </Panel>

      <Panel title="Recent Reasoning Activity">
        <div className="space-y-2 text-xs mono">
          {visibleLogs.length === 0 ? (
            <div className="text-muted-foreground">No recent ontology or reasoning logs available.</div>
          ) : (
            visibleLogs.map(entry => (
              <div key={entry.id} className="rounded-lg border border-[color:var(--panel-border)] p-3 bg-[oklch(0.98_0.05_240/0.4)]">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-semibold">{entry.category}</span>
                  <span className="text-muted-foreground text-[11px]">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-[10px] text-muted-foreground">{entry.severity}</div>
                <div>{entry.message}</div>
              </div>
            ))
          )}
        </div>
      </Panel>

      <Panel title={`Active SWRL Rules (${swrlRules.length})`}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {swrlRules.map(r => (
            <div key={r.id} className="p-3 rounded-lg border border-[color:var(--panel-border)] bg-[oklch(0.18_0.04_250/0.5)]">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-info mono">{r.id} — {r.name}</span>
                <span className={`text-[10px] mono px-2 py-0.5 rounded ${r.active ? "text-success border border-success/40" : "text-muted-foreground border border-muted-foreground/40"}`}>
                  {r.active ? "ACTIVE" : "DISABLED"}
                </span>
              </div>
              <div className="text-[11px] mono text-muted-foreground leading-relaxed">{r.condition}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}