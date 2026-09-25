import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/problems': 'http://localhost:8000',
      '/pitch': 'http://localhost:8000',
      '/proposals': 'http://localhost:8000',
      '/solvers': 'http://localhost:8000',
      '/pdf': 'http://localhost:8000',
      '/tokens': 'http://localhost:8000',
    }
  }
})