import { useEffect, useMemo, useState, type FormEvent } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import PlotCard from "../components/PlotCard";
import { createPlot, fetchPlotStatus } from "../services/plots";
import type { PlotStatus } from "../services/plots";

export default function Dashboard() {
  const [plots, setPlots] = useState<PlotStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [plotName, setPlotName] = useState("");
  const [plotSurface, setPlotSurface] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchPlotStatus();
        setPlots(data);
      } catch {
        setError("Failed to load plot status.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const handleRefresh = async () => {
    if (loading || isRefreshing) return;
    setIsRefreshing(true);
    setError(null);
    try {
      const data = await fetchPlotStatus();
      setPlots(data);
    } catch {
      setError("Failed to refresh plot status.");
    } finally {
      setIsRefreshing(false);
    }
  };

  const openModal = () => {
    setPlotName("");
    setPlotSurface("");
    setFormError(null);
    setError(null);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    if (isSubmitting) return;
    setIsModalOpen(false);
    setFormError(null);
  };

  const handleCreatePlot = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedName = plotName.trim();
    if (!trimmedName || isSubmitting) return;

    setIsSubmitting(true);
    setFormError(null);
    setError(null);

    const sizeInput = plotSurface.trim();
    const parsedSize = sizeInput === "" ? null : Number(sizeInput);
    const sizeHectares =
      parsedSize !== null && Number.isFinite(parsedSize) ? parsedSize : 1;

    try {
      await createPlot({ name: trimmedName, size_hectares: sizeHectares });
      const data = await fetchPlotStatus();
      setPlots(data);
      setIsModalOpen(false);
      setPlotName("");
      setPlotSurface("");
    } catch {
      setFormError("Failed to add plot.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const stats = useMemo(() => {
    const total = plots.length;
    const ok = plots.filter((p) => p.status === "OK").length;
    const warning = plots.filter((p) => p.status === "WARNING").length;
    const critical = plots.filter((p) => p.status === "CRITICAL").length;
    return { total, ok, warning, critical };
  }, [plots]);

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-8">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-300">Live overview</p>
            <h1 className="text-3xl font-semibold text-white">Farm Dashboard</h1>
          </div>

          <div className="flex gap-3">
            <button
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleRefresh}
              disabled={loading || isRefreshing}
            >
              {isRefreshing ? "Refreshing..." : "Refresh data"}
            </button>
            <button
              className="rounded-xl bg-agri-500 px-4 py-2 text-sm font-semibold text-agri-900 transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={openModal}
              disabled={isSubmitting || isModalOpen}
            >
              Add plot
            </button>
          </div>
        </header>

        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
            <div
              className="glass-card w-full max-w-lg rounded-2xl p-6 text-white"
              role="dialog"
              aria-modal="true"
              aria-labelledby="add-plot-title"
            >
              <div className="mb-4">
                <p className="text-sm text-slate-300">Create a new plot</p>
                <h2 id="add-plot-title" className="text-2xl font-semibold">
                  Add plot
                </h2>
              </div>

              <form onSubmit={handleCreatePlot} className="space-y-4">
                <div>
                  <label htmlFor="plot-name" className="text-sm text-slate-200">
                    Plot name
                  </label>
                  <input
                    id="plot-name"
                    type="text"
                    className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-agri-500"
                    placeholder="e.g. North field"
                    value={plotName}
                    onChange={(event) => setPlotName(event.target.value)}
                    required
                  />
                </div>

                <div>
                  <label htmlFor="plot-surface" className="text-sm text-slate-200">
                    Surface (ha)
                  </label>
                  <input
                    id="plot-surface"
                    type="number"
                    inputMode="decimal"
                    min="0"
                    step="0.01"
                    className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-agri-500"
                    placeholder="Optional"
                    value={plotSurface}
                    onChange={(event) => setPlotSurface(event.target.value)}
                  />
                </div>

                {formError && (
                  <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                    {formError}
                  </div>
                )}

                <div className="flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
                    onClick={closeModal}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-xl bg-agri-500 px-4 py-2 text-sm font-semibold text-agri-900 transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={isSubmitting || plotName.trim().length === 0}
                  >
                    {isSubmitting ? "Creating..." : "Create"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {error && <div className="glass-card rounded-2xl p-4 text-red-300">{error}</div>}

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Total plots", value: stats.total, tone: "from-agri-500 to-green-400" },
            { label: "Healthy", value: stats.ok, tone: "from-emerald-500 to-green-400" },
            { label: "Warning", value: stats.warning, tone: "from-amber-500 to-yellow-400" },
            { label: "Critical", value: stats.critical, tone: "from-red-500 to-rose-500" },
          ].map((stat) => (
            <div
              key={stat.label}
              className={`rounded-2xl bg-gradient-to-br p-5 text-white shadow-xl shadow-black/30 ${stat.tone}`}
            >
              <p className="text-sm text-white/80">{stat.label}</p>
              <p className="text-3xl font-semibold">{stat.value}</p>
            </div>
          ))}
        </section>

        <section className="glass-card rounded-2xl p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-300">Plot status</p>
              <h2 className="text-xl font-semibold text-white">Live sensors</h2>
            </div>
            <span className="rounded-full bg-white/10 px-4 py-1 text-sm text-slate-200">
              {stats.total} active plots
            </span>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, idx) => (
                <div
                  key={idx}
                  className="h-32 animate-pulse rounded-2xl bg-white/5 ring-1 ring-white/5"
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
              {plots.map((plot) => (
                <PlotCard key={plot.id} plot={plot} />
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
