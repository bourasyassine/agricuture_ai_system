import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

type TokenPair = {
  access: string;
  refresh: string;
};

export async function login(username: string, password: string) {
  const { data } = await axios.post<TokenPair>(`${API_URL}/token/`, {
    username,
    password,
  });

  persistTokens(data);
}

function persistTokens({ access, refresh }: TokenPair) {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
}

export function getAccessToken(): string | null {
  return localStorage.getItem("access");
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem("access");
}

export function logout(): void {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}
