import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/problems': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/pitch': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/tokens': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/pdf': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/solvers': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})