import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Only used if VITE_API_BASE is set to a relative path such as "/api".
      // By default the app calls the backend absolutely (see .env), which
      // exercises the same cross-origin CORS path production uses.
      // No rewrite: the FastAPI routers are themselves mounted under /api,
      // so stripping the prefix here would 404 every request.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
