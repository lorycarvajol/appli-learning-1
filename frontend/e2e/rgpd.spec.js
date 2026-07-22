import { test, expect } from '@playwright/test'
import { registerNewUser, login, openUserMenu } from './helpers'

/**
 * Parcours RGPD côté apprenant : portabilité (export) et effacement
 * self-service. Chaque test crée son propre compte jetable — la suppression
 * ne touche donc jamais un compte partagé.
 */
test.describe('RGPD — mes données', () => {
  test('le profil expose l’export et la suppression de compte', async ({ page }) => {
    await registerNewUser(page)
    await openUserMenu(page, 'Mon profil')
    await expect(page).toHaveURL(/\/profil/)

    await expect(page.getByRole('heading', { name: 'Mes données' })).toBeVisible()
    await expect(
      page.getByRole('button', { name: /Exporter mes données/i })
    ).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'Supprimer mon compte' })
    ).toBeVisible()
  })

  test('l’export télécharge un fichier JSON', async ({ page }) => {
    await registerNewUser(page)
    await page.goto('/profil')

    const downloadPromise = page.waitForEvent('download')
    await page.getByRole('button', { name: /Exporter mes données/i }).click()
    const download = await downloadPromise

    expect(download.suggestedFilename()).toBe('mes-donnees-codeacademy.json')
  })

  test('la suppression de compte déconnecte et empêche la reconnexion', async ({ page }) => {
    const { email, password } = await registerNewUser(page)
    await page.goto('/profil')

    // Révèle le formulaire de confirmation, puis confirme par mot de passe.
    await page.getByRole('button', { name: 'Supprimer mon compte' }).click()
    await page.getByLabel(/Confirmez avec votre mot de passe/i).fill(password)
    await page.getByRole('button', { name: /Supprimer définitivement/i }).click()

    await expect(page).toHaveURL(/\/login/)

    // Le compte est désormais anonymisé et désactivé : impossible d'y revenir.
    await login(page, email, password)
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('alert')).toBeVisible()
  })
})
