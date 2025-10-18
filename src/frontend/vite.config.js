import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: "0.0.0.0",
      proxy: {
        "/predict": env.VITE_BACKEND_URL ?? "http://localhost:8000",
        "/metrics": env.VITE_BACKEND_URL ?? "http://localhost:8000",
        "/health": env.VITE_BACKEND_URL ?? "http://localhost:8000",
        "/saliency": env.VITE_BACKEND_URL ?? "http://localhost:8000",
      },
    },
  };
});
