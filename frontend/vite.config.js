import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    strictPort: true,
    proxy: {
      // Proxy pour les fichiers media (images, vidéos, etc.)
      '/media': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      // Proxy pour les fichiers statiques si nécessaire
      '/static': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
    css: false,
    // Les fichiers de test vivent à côté du code qu'ils couvrent.
    include: ['src/**/*.{test,spec}.{js,jsx}'],
  },
})
