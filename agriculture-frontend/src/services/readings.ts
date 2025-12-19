import api from "./api";

export type SensorReading = {
  id: number;
  timestamp: string;
  temperature: number | null;
  humidity: number | null;
  soil_moisture: number | null;
};

type SensorReadingPayload = {
  id?: number;
  timestamp?: string;
  temperature?: number | null;
  air_temperature?: number | null;
  humidity?: number | null;
  soil_moisture?: number | null;
};

type PaginatedResponse = {
  results?: SensorReadingPayload[];
  count?: number;
  next?: string | null;
  previous?: string | null;
};

const normalizePayload = (data: SensorReadingPayload[] | PaginatedResponse | unknown): SensorReadingPayload[] => {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && typeof data === "object" && Array.isArray((data as PaginatedResponse).results)) {
    return (data as PaginatedResponse).results ?? [];
  }

  return [];
};

export async function fetchPlotReadings(plotId: number): Promise<SensorReading[]> {
  const response = await api.get<SensorReadingPayload[] | PaginatedResponse>("/sensor-readings/", {
    params: { plot: plotId },
  });

  const items = normalizePayload(response.data);

  return items.map((item, index) => {
    const temperatureValue =
      typeof item.temperature === "number"
        ? item.temperature
        : typeof item.air_temperature === "number"
        ? item.air_temperature
        : null;
    const humidityValue = typeof item.humidity === "number" ? item.humidity : null;
    const soilMoistureValue = typeof item.soil_moisture === "number" ? item.soil_moisture : null;

    return {
      id: typeof item.id === "number" ? item.id : index,
      timestamp: typeof item.timestamp === "string" ? item.timestamp : "",
      temperature: temperatureValue,
      humidity: humidityValue,
      soil_moisture: soilMoistureValue,
    };
  });
}
