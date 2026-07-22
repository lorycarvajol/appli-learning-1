import { test, expect } from '@playwright/test'
import {
  registerNewUser,
  login,
  openUserMenu,
  expectAuthenticatedDashboard,
  DEFAULT_PASSWORD,
} from './helpers'

test.describe('Authentification', () => {
  test('le consentement RGPD est obligatoire à l’inscription', async ({ page }) => {
    await page.goto('/register')

    await page.getByLabel('Email').fill('peu-importe@example.com')
    await page.getByLabel('Prénom').fill('Eve')
    await page.getByLabel('Nom', { exact: true }).fill('Test')
    await page.getByLabel('Mot de passe', { exact: true }).fill(DEFAULT_PASSWORD)
    await page.getByLabel('Confirmer le mot de passe').fill(DEFAULT_PASSWORD)

    // Tant que la case n'est pas cochée, l'inscription est bloquée : la case
    // n'est pas décorative.
    const submit = page.getByRole('button', { name: /s’inscrire|s'inscrire/i })
    await expect(submit).toBeDisabled()

    await page.getByLabel(/politique de confidentialité/i).check()
    await expect(submit).toBeEnabled()
  })

  test('inscription puis arrivée sur le tableau de bord', async ({ page }) => {
    await registerNewUser(page)
    await expectAuthenticatedDashboard(page)
  })

  test('connexion à un compte existant mène à un tableau de bord fonctionnel', async ({ page }) => {
    // Reproduit le scénario réel du bug : une connexion « à froid », sans
    // inscription préalable dans la même session. `alice` est créée par
    // `python manage.py create_demo_users` (cf. e2e/README.md).
    await login(page, 'alice@test.com', 'learner123')
    await expectAuthenticatedDashboard(page)
  })

  test('déconnexion puis reconnexion', async ({ page }) => {
    const { email, password } = await registerNewUser(page)

    await openUserMenu(page, 'Déconnexion')
    await expect(page).toHaveURL(/\/login/)

    await login(page, email, password)
    await expectAuthenticatedDashboard(page)
  })

  test('un mauvais mot de passe ne connecte pas', async ({ page }) => {
    const { email } = await registerNewUser(page)
    await openUserMenu(page, 'Déconnexion')

    await login(page, email, 'mauvais-mot-de-passe')

    // L'accès est refusé, et un message d'erreur s'affiche. Ce message est la
    // régression que corrige l'exception d'auth dans l'intercepteur axios :
    // avant, un 401 de login déclenchait un rechargement de `/login` qui
    // effaçait l'erreur.
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('alert')).toBeVisible()
  })
})
