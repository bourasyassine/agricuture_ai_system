import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import { fetchAnomalies, type Anomaly } from "../services/anomalies";

const severityTone: Record<Anomaly["severity"], string> = {
  high: "bg-red-500/10 text-red-200 ring-red-500/30",
  medium: "bg-orange-500/10 text-orange-200 ring-orange-500/30",
  low: "bg-emerald-500/10 text-emerald-200 ring-emerald-500/30",
};

const metricLabel: Record<Anomaly["metric"], string> = {
  temperature: "Temperature",
  humidity: "Humidity",
  soil_moisture: "Soil moisture",
};

const formatDate = (value: string): string => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "-";
  }
  return parsed.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

const formatValue = (value: number): string => {
  if (!Number.isFinite(value)) {
    return "-";
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
};

export default function Alerts() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchAnomalies();
        if (!active) return;
        setAnomalies(Array.isArray(data) ? data : []);
      } catch {
        if (!active) return;
        setError("Failed to load alerts.");
        setAnomalies([]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      active = false;
    };
  }, []);

  const severityCounts = useMemo(
    () =>
      anomalies.reduce(
        (acc, item) => {
          acc[item.severity] = (acc[item.severity] ?? 0) + 1;
          return acc;
        },
        { high: 0, medium: 0, low: 0 } as Record<Anomaly["severity"], number>
      ),
    [anomalies]
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-slate-300">AI monitoring</p>
            <h1 className="text-3xl font-semibold text-white">Alerts</h1>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-200">
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              High: {severityCounts.high}
            </span>
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              Medium: {severityCounts.medium}
            </span>
            <span className="rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              Low: {severityCounts.low}
            </span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {Array.from({ length: 4 }).map((_, idx) => (
              <div key={idx} className="h-40 animate-pulse rounded-2xl bg-white/5 ring-1 ring-white/5" />
            ))}
          </div>
        ) : error ? (
          <div className="glass-card rounded-2xl p-6 text-red-200 ring-1 ring-red-500/30">
            {error}
          </div>
        ) : anomalies.length === 0 ? (
          <div className="glass-card rounded-2xl p-6 text-slate-200">
            No anomalies detected.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {anomalies.map((anomaly) => {
              const hasValidPlot = Number.isFinite(anomaly.plot) && anomaly.plot > 0;
              const plotLabel = hasValidPlot ? `Plot #${anomaly.plot}` : "Plot unavailable";
              const recommendation =
                anomaly.recommendation && anomaly.recommendation.trim().length > 0
                  ? anomaly.recommendation
                  : "No recommendation provided.";
              const message =
                anomaly.message && anomaly.message.trim().length > 0
                  ? anomaly.message
                  : "No message provided.";

              return (
                <div
                  key={anomaly.id}
                  className="glass-card flex flex-col gap-4 rounded-2xl p-5 ring-1 ring-white/5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-3">
                        <p className="text-lg font-semibold text-white">{plotLabel}</p>
                        <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-200 ring-1 ring-white/10">
                          {metricLabel[anomaly.metric]}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">{message}</p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ring-1 ${severityTone[anomaly.severity]}`}
                    >
                      {anomaly.severity}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-4 text-sm text-slate-200 sm:grid-cols-3">
                    <div>
                      <p className="text-xs text-slate-400">Value</p>
                      <p className="text-base font-semibold text-white">
                        {formatValue(anomaly.value)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Detected</p>
                      <p className="text-sm text-slate-200">{formatDate(anomaly.created_at)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Plot</p>
                      {hasValidPlot ? (
                        <Link
                          to={`/plots/${anomaly.plot}`}
                          className="text-sm font-semibold text-agri-500 transition hover:text-agri-100"
                        >
                          View plot
                        </Link>
                      ) : (
                        <span className="text-sm text-slate-400">Unavailable</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-slate-400">Recommendation</p>
                    <p className="text-sm text-slate-200">{recommendation}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
