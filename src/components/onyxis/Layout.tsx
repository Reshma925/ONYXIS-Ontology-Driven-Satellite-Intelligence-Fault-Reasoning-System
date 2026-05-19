import { Outlet } from "@tanstack/react-router";
import { OnyxisProvider } from "@/lib/onyxis/simulation";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function Layout() {
  return (
    <OnyxisProvider>
      <div className="min-h-screen flex w-full text-foreground">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Header />
          <main className="flex-1 overflow-auto p-6 grid-bg">
            <Outlet />
          </main>
        </div>
      </div>
    </OnyxisProvider>
  );
}

export function PageHeader({ title, subtitle, right }: { title: string; subtitle?: string; right?: React.ReactNode }) {
  return (
    <div className="flex items-end justify-between mb-6">
      <div>
        <div className="text-[10px] uppercase tracking-[0.3em] text-[color:var(--info)] mb-1">// {subtitle ?? "Mission Operations"}</div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
      </div>
      {right}
    </div>
  );
}

export function Panel({ title, right, children, className = "" }:
  { title?: string; right?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={`glass-panel relative overflow-hidden ${className}`}>
      {title && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-[color:var(--panel-border)]">
          <h3 className="text-xs uppercase tracking-[0.2em] text-muted-foreground font-semibold">{title}</h3>
          {right}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}