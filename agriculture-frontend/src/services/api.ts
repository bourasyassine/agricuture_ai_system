import axios from "axios";
import { getAccessToken } from "./auth";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api",
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    const headers = config.headers ?? {};
    if (typeof (headers as any).set === "function") {
      (headers as any).set("Authorization", `Bearer ${token}`);
    } else {
      (headers as any).Authorization = `Bearer ${token}`;
    }
    config.headers = headers;
  }

  return config;
});

export default api;
