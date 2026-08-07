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
  build: {
    /**
     * Vite intègre en base64 tout asset de moins de 4 ko. C'est un bon défaut
     * — une requête épargnée pour une icône — mais il se retourne contre le
     * catalogue d'avatars : `Avatar` est tiré par le `Header`, donc structurel
     * et jamais différé, et douze des quarante-deux visages passaient sous le
     * seuil. Chaque visiteur téléchargeait donc douze visages qu'il ne verrait
     * jamais (+58 ko bruts, +13 ko gzip sur le morceau d'entrée), alors qu'un
     * compte n'en affiche qu'un.
     *
     * Rendre `false` **désactive** l'intégration pour ces fichiers : ils sont
     * émis à part, chargés à la demande et mis en cache. `undefined` laisse le
     * seuil habituel s'appliquer partout ailleurs.
     *
     * ⚠️ Le suffixe `?no-inline`, qui dirait la même chose au point d'usage,
     * n'existe qu'à partir de Vite 6.
     */
    assetsInlineLimit: (filePath) =>
      filePath.includes('/assets/avatars/') ? false : undefined,
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
