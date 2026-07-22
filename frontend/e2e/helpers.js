import { expect } from '@playwright/test'

/**
 * Outils partagés par les tests E2E.
 *
 * Chaque test crée son propre compte via un email unique : aucun test ne
 * dépend de l'état laissé par un autre, et la suite reste ré-exécutable sans
 * purge de base entre deux passages.
 */

export function uniqueEmail(prefix = 'e2e') {
  // Assez unique pour ne jamais entrer en collision, même en parallèle.
  const rand = Math.random().toString(36).slice(2, 8)
  return `${prefix}-${Date.now()}-${rand}@example.com`
}

export const DEFAULT_PASSWORD = 'e2e-pwd-not-a-real-secret'

/**
 * Inscrit un nouveau compte apprenant et attend l'arrivée sur le tableau de
 * bord. Renvoie l'email utilisé, pour les tests qui reconnectent ensuite.
 */
export async function registerNewUser(page, { password = DEFAULT_PASSWORD } = {}) {
  const email = uniqueEmail()

  await page.goto('/register')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Prénom').fill('Eve')
  await page.getByLabel('Nom', { exact: true }).fill('Test')
  await page.getByLabel('Mot de passe', { exact: true }).fill(password)
  await page.getByLabel('Confirmer le mot de passe').fill(password)
  await page.getByLabel(/politique de confidentialité/i).check()

  await page.getByRole('button', { name: /s’inscrire|s'inscrire/i }).click()
  await expect(page).toHaveURL(/\/dashboard/)

  return { email, password }
}

/** Connexion par le formulaire. */
export async function login(page, email, password = DEFAULT_PASSWORD) {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Mot de passe', { exact: true }).fill(password)
  await page.getByRole('button', { name: /se connecter/i }).click()
}

/** Ouvre le menu utilisateur (en-tête) et clique une entrée par son nom. */
export async function openUserMenu(page, itemName) {
  await page.locator('.header__user-button').click()
  await page.getByRole('menuitem', { name: itemName }).click()
}
