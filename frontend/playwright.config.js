import { defineConfig, devices } from '@playwright/test'

/**
 * Tests bout-en-bout (Playwright) — tranche mince, en local.
 *
 * Contrairement aux tests Vitest (isolés, jsdom), ceux-ci pilotent un vrai
 * navigateur contre la **stack complète en marche** : front `:5173` + back
 * `:8000` + postgres + redis. La stack n'est pas démarrée par Playwright — on
 * suppose `docker-compose up` déjà lancé (cf. `e2e/README.md`). C'est délibéré :
 * reconstruire l'orchestration ici doublerait le `docker-compose` du dépôt.
 *
 * Périmètre volontairement restreint aux parcours qui **ne dépendent pas du
 * bac à sable d'exécution** (auth, navigation, pages légales, RGPD). La
 * soumission d'exercice, qui exige le sandbox celery/docker.sock, est une
 * tranche ultérieure — à marquer à part, comme les tests backend `-m docker`.
 */
export default defineConfig({
  testDir: './e2e',
  // Les tests créent leurs propres comptes (emails uniques) : ils peuvent
  // tourner en parallèle sans se marcher dessus.
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    // Un échec doit laisser une trace exploitable sans relancer.
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
