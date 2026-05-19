import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, severityColor, fmtUTC, type LogEntry } from "@/lib/onyxis/simulation";
import { PageHeader, Panel } from "@/components/onyxis/Layout";
import { useState } from "react";

export const Route = createFileRoute("/logs")({
  head: () => ({ meta: [{ title: "Event Logs — ONYXIS" }] }),
  component: Logs,
});

const CATS: LogEntry["category"][] = ["Ontology","SWRL","Pellet","Fault","Propagation","System","User","Telemetry"];

function Logs() {
  const { logs } = useOnyxis();
  const [filter, setFilter] = useState<LogEntry["category"] | "ALL">("ALL");
  const filtered = filter === "ALL" ? logs : logs.filter(l => l.category === filter);
  return (
    <div className="space-y-6">
      <PageHeader title="Mission Event Logs" subtitle="Operational Trace"
        right={<div className="text-xs mono text-muted-foreground">{filtered.length} ENTRIES</div>} />
      <div className="flex flex-wrap gap-2">
        {(["ALL", ...CATS] as const).map(c => (
          <button key={c} onClick={() => setFilter(c)}
            className={`text-[10px] mono uppercase tracking-widest px-3 py-1.5 rounded-md border transition-all ${filter === c ? "bg-[oklch(0.78_0.16_240/0.15)] border-[color:var(--info)] text-info" : "border-[color:var(--panel-border)] text-muted-foreground hover:text-foreground"}`}>
            {c}
          </button>
        ))}
      </div>
      <Panel>
        <div className="font-mono text-xs h-[65vh] overflow-y-auto rounded-lg bg-[oklch(0.12_0.03_250/0.6)] border border-[color:var(--panel-border)] divide-y divide-[color:var(--panel-border)]">
          {filtered.length === 0 && <div className="p-6 text-muted-foreground">No log entries.</div>}
          {filtered.map(l => (
            <div key={l.id} className="flex items-center gap-3 px-3 py-2 hover:bg-[oklch(0.78_0.16_240/0.05)]">
              <span className="text-muted-foreground shrink-0">{fmtUTC(l.timestamp)}</span>
              <span className="px-2 py-0.5 rounded text-[9px] font-bold tracking-wider shrink-0"
                style={{ background: `color-mix(in oklab, ${severityColor(l.severity)} 20%, transparent)`, color: severityColor(l.severity), border: `1px solid color-mix(in oklab, ${severityColor(l.severity)} 50%, transparent)` }}>
                {l.severity}
              </span>
              <span className="px-2 py-0.5 rounded text-[9px] uppercase tracking-wider shrink-0 bg-[oklch(0.3_0.05_250/0.5)] text-info">{l.category}</span>
              <span className="text-foreground/90 truncate">{l.message}</span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}