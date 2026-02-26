import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 10772,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:10773',
        changeOrigin: true,
      },
      '/sse': {
        target: 'http://localhost:10773',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
