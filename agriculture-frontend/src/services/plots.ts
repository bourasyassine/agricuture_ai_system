import api from "./api";

export type PlotStatus = {
  id: number;
  name: string;
  size_hectares: number;
  status: "OK" | "WARNING" | "CRITICAL";
};

export type Plot = {
  id: number;
  name: string;
  size_hectares: number;
  farm: number;
};

export async function fetchPlotStatus(): Promise<PlotStatus[]> {
  const response = await api.get("/plots/status/");
  return response.data;
}

type PlotCreatePayload = {
  name: string;
  size_hectares: number;
  farm?: number;
};

export async function createPlot(payload: PlotCreatePayload): Promise<Plot> {
  const response = await api.post<Plot>("/plots/", payload);
  return response.data;
}
