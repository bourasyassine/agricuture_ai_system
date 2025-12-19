import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "agri-900": "#0f172a",
        "agri-800": "#111827",
        "agri-700": "#1f2937",
        "agri-600": "#2563eb",
        "agri-500": "#22c55e",
        "agri-100": "#e8f5ef",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
} satisfies Config;
