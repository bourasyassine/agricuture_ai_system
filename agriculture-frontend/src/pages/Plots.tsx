// src/pages/Plots.tsx
import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import PlotCard from "../components/PlotCard";
import { fetchPlotStatus } from "../services/plots";
import type { PlotStatus } from "../services/plots";

export default function Plots() {
  const [plots, setPlots] = useState<PlotStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const data = await fetchPlotStatus();
        if (mounted) setPlots(data);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const counts = useMemo(() => {
    const c: Record<PlotStatus["status"], number> = {
      OK: 0,
      WARNING: 0,
      CRITICAL: 0,
    };
    for (const p of plots) {
      c[p.status] = (c[p.status] ?? 0) + 1;
    }
    return c;
  }, [plots]);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-slate-300">Plots</p>
            <h1 className="text-3xl font-semibold text-white">All plots</h1>
          </div>

          <div className="flex gap-3 text-sm text-slate-200">
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              Healthy: {counts.OK}
            </span>
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              Warning: {counts.WARNING}
            </span>
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              Critical: {counts.CRITICAL}
            </span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, idx) => (
              <div key={idx} className="h-32 animate-pulse rounded-2xl bg-white/5 ring-1 ring-white/5" />
            ))}
          </div>
        ) : plots.length === 0 ? (
          <div className="glass-card rounded-2xl p-6 text-slate-300">
            No plots yet.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {plots.map((p) => (
              <PlotCard key={p.id} plot={p} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
