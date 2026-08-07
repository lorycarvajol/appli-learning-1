import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

/**
 * jsdom n'implémente pas `window.matchMedia` — pas partiellement, pas du
 * tout. Tout composant qui interroge le thème du système lève donc
 * « matchMedia is not a function » **au montage**, avant même la première
 * assertion : c'est ce qui arrive dès qu'un test monte `ThemeProvider`, donc
 * `Layout`, donc `Header`.
 *
 * Le bouchon répond « thème clair » et accepte les écouteurs que
 * `ThemeProvider` pose pour suivre les changements en direct. Un test qui
 * voudrait le thème sombre remplace `window.matchMedia` pour lui seul.
 */
window.matchMedia = window.matchMedia || ((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addEventListener: () => {},
  removeEventListener: () => {},
  addListener: () => {},
  removeListener: () => {},
  dispatchEvent: () => false,
}))

afterEach(() => {
  cleanup()
  localStorage.clear()
  vi.clearAllMocks()
})
