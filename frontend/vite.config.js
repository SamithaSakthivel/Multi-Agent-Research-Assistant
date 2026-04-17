import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Changed localhost to 127.0.0.1
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://127.0.0.1:8000', // Changed localhost to 127.0.0.1
        ws: true,
        changeOrigin: true,
      },
    },
  },
})