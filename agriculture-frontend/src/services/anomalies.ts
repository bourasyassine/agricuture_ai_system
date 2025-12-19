import api from "./api";

export type Anomaly = {
  id: number;
  plot: number;
  metric: "temperature" | "humidity" | "soil_moisture";
  value: number;
  severity: "low" | "medium" | "high";
  message: string;
  recommendation: string;
  created_at: string;
};

type AnomalyPayload = Partial<Anomaly>;

type PaginatedResponse = {
  results?: AnomalyPayload[];
  count?: number;
  next?: string | null;
  previous?: string | null;
};

const isMetric = (value: unknown): value is Anomaly["metric"] =>
  value === "temperature" || value === "humidity" || value === "soil_moisture";

const isSeverity = (value: unknown): value is Anomaly["severity"] =>
  value === "low" || value === "medium" || value === "high";

const normalizePayload = (data: unknown): AnomalyPayload[] => {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && typeof data === "object" && Array.isArray((data as PaginatedResponse).results)) {
    return (data as PaginatedResponse).results ?? [];
  }

  return [];
};

export async function fetchAnomalies(): Promise<Anomaly[]> {
  const response = await api.get<AnomalyPayload[] | PaginatedResponse>("/anomalies/");
  const items = normalizePayload(response.data);

  return items.map((item, index) => ({
    id: typeof item.id === "number" ? item.id : index,
    plot: typeof item.plot === "number" ? item.plot : -1,
    metric: isMetric(item.metric) ? item.metric : "temperature",
    value: typeof item.value === "number" && Number.isFinite(item.value) ? item.value : NaN,
    severity: isSeverity(item.severity) ? item.severity : "low",
    message: typeof item.message === "string" ? item.message : "",
    recommendation: typeof item.recommendation === "string" ? item.recommendation : "",
    created_at: typeof item.created_at === "string" ? item.created_at : "",
  }));
}
