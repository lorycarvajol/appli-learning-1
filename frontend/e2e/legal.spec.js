import { test, expect } from '@playwright/test'

test.describe('Pages légales (publiques)', () => {
  const pages = [
    { path: '/confidentialite', heading: /politique de confidentialité/i },
    { path: '/mentions-legales', heading: /mentions légales/i },
    { path: '/cgu', heading: /conditions générales d’utilisation/i },
  ]

  for (const { path, heading } of pages) {
    test(`${path} est accessible sans session`, async ({ page }) => {
      await page.goto(path)
      await expect(page.getByRole('heading', { level: 1, name: heading })).toBeVisible()
    })
  }

  test('les liens de consentement de l’inscription mènent aux pages légales', async ({ page }) => {
    await page.goto('/register')

    const privacy = page.getByRole('link', { name: /politique de confidentialité/i })
    const terms = page.getByRole('link', { name: /conditions d’utilisation/i })

    await expect(privacy).toHaveAttribute('href', '/confidentialite')
    await expect(terms).toHaveAttribute('href', '/cgu')
  })
})
