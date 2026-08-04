import { test, expect } from '@playwright/test'
import { registerNewUser } from './helpers'

/**
 * Parcours de navigation de contenu. Dépend du chapitre « Introduction au
 * HTML » : lancer `python manage.py load_section_1_html --force` avant
 * (cf. e2e/README.md). Ne pas amorcer avec `load_demo_content`, qui remplace
 * ce chapitre par une version maigre.
 *
 * Un apprenant fraîchement inscrit est **autonome** : le premier chapitre est
 * ouvert d'emblée (rythme libre), donc ses leçons sont consultables sans
 * qu'un formateur ait à débloquer quoi que ce soit.
 */
test.describe('Navigation dans les cours', () => {
  test('un apprenant ouvre un chapitre puis une leçon', async ({ page }) => {
    await registerNewUser(page)

    await page.goto('/chapters')
    await expect(page.getByRole('heading', { name: 'Chapitres', level: 1 })).toBeVisible()

    // Le chapitre de démonstration, accessible car premier du parcours.
    await page.getByRole('link', { name: /Introduction au HTML/i }).click()
    await expect(page).toHaveURL(/\/chapters\/introduction-html/)
    await expect(
      page.getByRole('heading', { name: 'Introduction au HTML', level: 1 })
    ).toBeVisible()

    // Ouverture d'une leçon de théorie du chapitre.
    await page.getByRole('link', { name: /Qu’est-ce que le HTML|Qu'est-ce que le HTML/i }).click()
    await expect(page).toHaveURL(/\/lessons\//)
    await expect(page.getByText(/HTML/i).first()).toBeVisible()
  })
})
