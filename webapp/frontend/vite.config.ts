import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 10772,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:10773",
        changeOrigin: true,
      },
      "/sse": {
        target: "http://localhost:10773",
        changeOrigin: true,
      },
      "/docs": {
        target: "http://localhost:10773",
        changeOrigin: true,
      },
      "/openapi.json": {
        target: "http://localhost:10773",
        changeOrigin: true,
      },
      "/redoc": {
        target: "http://localhost:10773",
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
