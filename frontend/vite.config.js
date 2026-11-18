import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5174,
    host: '127.0.0.1',
    proxy: {
      '/health': 'http://127.0.0.1:8001',
      '/predict': 'http://127.0.0.1:8001',
      '/explain': 'http://127.0.0.1:8001',
      '/models': 'http://127.0.0.1:8001',
      '/severity': 'http://127.0.0.1:8001',
      '/batch': 'http://127.0.0.1:8001',
      '/similarity': 'http://127.0.0.1:8001',
      '/rag': 'http://127.0.0.1:8001',
      '/dashboard': 'http://127.0.0.1:8001',
      '/drift': 'http://127.0.0.1:8001',
      '/rca': 'http://127.0.0.1:8001',
      '/samples': 'http://127.0.0.1:8001',
      '/categories': 'http://127.0.0.1:8001',
      '/reports': 'http://127.0.0.1:8001',
      '/active-learning': 'http://127.0.0.1:8001',
      '/outputs': 'http://127.0.0.1:8001',
      '/stream': 'http://127.0.0.1:8001',
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
