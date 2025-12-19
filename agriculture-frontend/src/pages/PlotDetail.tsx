import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from "chart.js";
import { Line } from "react-chartjs-2";
import DashboardLayout from "../layouts/DashboardLayout";
import { fetchPlotReadings, type SensorReading } from "../services/readings";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const chartOptions: ChartOptions<"line"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: "bottom" },
    tooltip: { mode: "index", intersect: false },
  },
  scales: {
    x: {
      ticks: { color: "#cbd5e1" },
      grid: { color: "rgba(148,163,184,0.2)" },
    },
    y: {
      ticks: { color: "#cbd5e1" },
      grid: { color: "rgba(148,163,184,0.2)" },
    },
  },
};

const toNumericValue = (value: unknown): number | null =>
  typeof value === "number" && Number.isFinite(value) ? value : null;

const toPercentageValue = (value: unknown): number | null => {
  const numeric = toNumericValue(value);
  if (numeric === null) {
    return null;
  }
  if (numeric >= 0 && numeric <= 1) {
    return numeric * 100;
  }
  return numeric;
};

const formatTimeLabel = (value: string): string => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value || "-";
  }

  return parsed.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
};

const buildMetricChart = (
  labels: string[],
  values: Array<number | null>,
  label: string,
  borderColor: string,
  backgroundColor: string
): ChartData<"line", (number | null)[], string> | null => {
  if (labels.length === 0) {
    return null;
  }
  const hasValues = values.some((value) => value !== null);
  if (!hasValues) {
    return null;
  }

  return {
    labels,
    datasets: [
      {
        label,
        data: values,
        borderColor,
        backgroundColor,
        tension: 0.25,
        pointRadius: 3,
      },
    ],
  };
};

export default function PlotDetail() {
  const { id } = useParams<{ id: string }>();
  const plotId = Number(id);
  const isValidPlotId = Number.isFinite(plotId) && plotId > 0;

  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    if (!isValidPlotId) {
      setError("Invalid plot id.");
      setReadings([]);
      setLoading(false);
      return () => {
        active = false;
      };
    }

    const loadReadings = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchPlotReadings(plotId);
        if (!active) return;
        setReadings(Array.isArray(data) ? data : []);
      } catch {
        if (!active) return;
        setError("Failed to load sensor readings.");
        setReadings([]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadReadings();

    return () => {
      active = false;
    };
  }, [isValidPlotId, plotId]);

  const handleRefresh = async () => {
    if (!isValidPlotId || loading || refreshing) return;
    setRefreshing(true);
    setError(null);
    try {
      const data = await fetchPlotReadings(plotId);
      setReadings(Array.isArray(data) ? data : []);
    } catch {
      setError("Failed to load sensor readings.");
      setReadings([]);
    } finally {
      setRefreshing(false);
    }
  };

  const sortedReadings = useMemo(() => {
    return readings
      .filter((item) => typeof item.timestamp === "string" && item.timestamp.trim().length > 0)
      .filter((item) => !Number.isNaN(new Date(item.timestamp).getTime()))
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [readings]);

  const series = useMemo(() => {
    if (sortedReadings.length === 0) {
      return null;
    }

    const labels = sortedReadings.map((reading) => formatTimeLabel(reading.timestamp));
    const temperatures = sortedReadings.map((reading) => toNumericValue(reading.temperature));
    const humidityValues = sortedReadings.map((reading) => toPercentageValue(reading.humidity));
    const soilMoistureValues = sortedReadings.map((reading) =>
      toPercentageValue(reading.soil_moisture)
    );

    return { labels, temperatures, humidityValues, soilMoistureValues };
  }, [sortedReadings]);

  const temperatureChart = useMemo(
    () =>
      buildMetricChart(
        series?.labels ?? [],
        series?.temperatures ?? [],
        "Temperature (C)",
        "#f97316",
        "rgba(249, 115, 22, 0.18)"
      ),
    [series]
  );

  const humidityChart = useMemo(
    () =>
      buildMetricChart(
        series?.labels ?? [],
        series?.humidityValues ?? [],
        "Humidity (%)",
        "#06b6d4",
        "rgba(6, 182, 212, 0.18)"
      ),
    [series]
  );

  const soilMoistureChart = useMemo(
    () =>
      buildMetricChart(
        series?.labels ?? [],
        series?.soilMoistureValues ?? [],
        "Soil moisture (%)",
        "#22c55e",
        "rgba(34, 197, 94, 0.18)"
      ),
    [series]
  );

  const dashboards = [
    { key: "temperature", title: "Temperature dashboard", chart: temperatureChart },
    { key: "humidity", title: "Humidity dashboard", chart: humidityChart },
    { key: "soil", title: "Soil moisture dashboard", chart: soilMoistureChart },
  ];

  const heading = isValidPlotId ? `Plot #${plotId}` : "Plot not found";

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Link to="/plots" className="text-sm text-slate-300 hover:text-white">
          Back to plots
        </Link>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-300">Plot details</p>
            <h1 className="text-3xl font-semibold text-white">{heading}</h1>
          </div>
          <button
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={handleRefresh}
            disabled={!isValidPlotId || loading || refreshing}
          >
            {refreshing ? "Refreshing..." : "Refresh data"}
          </button>
        </div>

        {loading && <div className="glass-card rounded-2xl p-4 text-slate-200">Loading...</div>}

        {!loading && error && <div className="glass-card rounded-2xl p-4 text-red-300">{error}</div>}

        {!loading && !error && (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            {dashboards.map((dashboard) => (
              <div key={dashboard.key} className="glass-card rounded-2xl p-6 space-y-4">
                <div className="text-sm text-slate-200">{dashboard.title}</div>
                <div className="relative h-[320px]">
                  {dashboard.chart ? (
                    <Line data={dashboard.chart} options={chartOptions} />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-300">
                      No data available yet.
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
