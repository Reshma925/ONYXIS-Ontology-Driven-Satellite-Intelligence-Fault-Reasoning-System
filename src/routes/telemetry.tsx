import { createFileRoute } from "@tanstack/react-router";
import { useOnyxis, fmtUTC } from "@/lib/onyxis/simulation";
import { PageHeader, Panel } from "@/components/onyxis/Layout";

export const Route = createFileRoute("/telemetry")({
  head: () => ({ meta: [{ title: "Live Telemetry — ONYXIS" }] }),
  component: LiveTelemetry,
});

function LiveTelemetry() {
  const { telemetry, speed } = useOnyxis();
  const VISIBLE_LIMIT = 200;
  const visible = telemetry.slice(0, VISIBLE_LIMIT);
  return (
    <div className="space-y-6">
      <PageHeader title="Live Telemetry Stream" subtitle="Raw Spacecraft Feed"
        right={<div className="text-xs mono text-muted-foreground">RATE: <span className="text-success">{speed}x</span> • CHANNELS: <span className="text-info">8</span></div>} />
      <Panel title="Real-time Telemetry Feed" right={<span className="flex items-center gap-2 text-[10px] mono text-success"><span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-glow" /> STREAMING</span>}>
        <div className="relative font-mono text-xs h-[70vh] overflow-y-auto rounded-lg bg-[oklch(0.12_0.03_250/0.6)] border border-[color:var(--panel-border)] p-4 scan-line">
          {telemetry.length === 0 && <div className="text-muted-foreground">Awaiting telemetry frames…</div>}
          {visible.map((t, i) => (
            <div key={t.id} className="flex gap-3 py-0.5 hover:bg-[oklch(0.78_0.16_240/0.05)] px-2 rounded transition-colors"
              style={{ opacity: i === 0 ? 1 : Math.max(0.4, 1 - i * 0.012) }}>
              <span className="text-muted-foreground">[{fmtUTC(t.timestamp)}]</span>
              <span className="text-info">{t.channel.padEnd(20, " ")}</span>
              <span className="text-foreground">=</span>
              <span className="text-success font-bold">{t.value}</span>
              <span className="text-muted-foreground">{t.unit}</span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}