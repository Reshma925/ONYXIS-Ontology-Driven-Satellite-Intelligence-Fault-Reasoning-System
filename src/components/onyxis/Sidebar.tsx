import { Link, useRouterState } from "@tanstack/react-router";
import { useOnyxis } from "@/lib/onyxis/simulation";

const items = [
  { to: "/", label: "Dashboard", icon: "🛰" },
  { to: "/telemetry", label: "Live Telemetry", icon: "📡" },
  { to: "/twin", label: "Digital Twin", icon: "🌌" },
  { to: "/graphs", label: "Telemetry Graphs", icon: "📈" },
  { to: "/faults", label: "Active Faults", icon: "⚠" },
  { to: "/logs", label: "Event Logs", icon: "📜" },
  { to: "/ontology", label: "Ontology Inspector", icon: "🧠" },
] as const;

export function Sidebar() {
  const path = useRouterState({ select: r => r.location.pathname });
  const { faults } = useOnyxis();
  return (
    <aside className="w-64 shrink-0 border-r border-[color:var(--panel-border)] bg-[oklch(0.2_0.04_250/0.7)] backdrop-blur-xl flex flex-col">
      <div className="px-5 py-5 border-b border-[color:var(--panel-border)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg grid place-items-center bg-gradient-to-br from-[color:var(--info)] to-[color:var(--semantic)] glow-primary">
            <span className="text-base">◆</span>
          </div>
          <div>
            <div className="text-sm font-bold tracking-[0.2em] text-foreground">ONYXIS</div>
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Mission Control</div>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {items.map(it => {
          const active = path === it.to;
          const isFaults = it.to === "/faults" && faults.length > 0;
          return (
            <Link
              key={it.to}
              to={it.to}
              className={[
                "group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200",
                active
                  ? "bg-[oklch(0.78_0.16_240/0.12)] text-foreground border border-[oklch(0.78_0.16_240/0.4)] shadow-[inset_0_0_20px_oklch(0.78_0.16_240/0.1)]"
                  : "text-muted-foreground hover:text-foreground hover:bg-[oklch(0.3_0.05_250/0.4)] border border-transparent"
              ].join(" ")}
            >
              {active && <span className="absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-full bg-[color:var(--info)] glow-primary" />}
              <span className="text-base w-5 text-center">{it.icon}</span>
              <span className="flex-1">{it.label}</span>
              {isFaults && (
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[color:var(--critical)] text-white mono animate-pulse-glow">
                  {faults.length}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-[color:var(--panel-border)] text-[10px] text-muted-foreground mono space-y-1">
        <div className="flex justify-between"><span>BUILD</span><span>v3.2.0-onx</span></div>
        <div className="flex justify-between"><span>NODE</span><span>MCC-EU-01</span></div>
      </div>
    </aside>
  );
}