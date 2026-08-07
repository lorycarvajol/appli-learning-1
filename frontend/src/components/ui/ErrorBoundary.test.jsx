import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ErrorBoundary from './ErrorBoundary'

/**
 * Sans frontière, une seule exception pendant le rendu démonte l'arbre et
 * laisse un **écran blanc** : ni explication, ni sortie, indistinguable d'une
 * panne réseau.
 */

function Casse() {
  throw new Error('bang')
}

beforeEach(() => {
  // React journalise l'erreur attrapée : c'est normal et attendu, mais ça
  // noie la sortie des tests. On la tait pour ce fichier seulement.
  vi.spyOn(console, 'error').mockImplementation(() => {})
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('ErrorBoundary', () => {
  it('laisse passer un rendu qui se porte bien', () => {
    render(
      <MemoryRouter>
        <ErrorBoundary><p>contenu normal</p></ErrorBoundary>
      </MemoryRouter>
    )

    expect(screen.getByText('contenu normal')).toBeInTheDocument()
  })

  it('affiche un message et une sortie au lieu d’un écran blanc', () => {
    render(
      <MemoryRouter>
        <ErrorBoundary><Casse /></ErrorBoundary>
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { level: 1, name: /n’a pas pu s’afficher/ }))
      .toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Recharger la page' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Retour au tableau de bord' }))
      .toBeInTheDocument()
  })

  it('rassure sur le travail enregistré', () => {
    // Un apprenant en plein exercice a besoin de savoir ça avant tout le reste.
    render(
      <MemoryRouter>
        <ErrorBoundary><Casse /></ErrorBoundary>
      </MemoryRouter>
    )

    expect(screen.getByText(/travail\s+enregistré n’est pas affecté/)).toBeInTheDocument()
  })

  it('se réarme quand on change de page', async () => {
    // ⚠️ Le point qui rend le lien de sortie utile. Une frontière d'erreur ne
    // se réinitialise pas d'elle-même : sans la clé sur le chemin, cliquer
    // « Retour au tableau de bord » changerait l'URL et laisserait le même
    // message à l'écran — une sortie qui ne sort de rien.
    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/casse']}>
        <ErrorBoundary>
          <Routes>
            <Route path="/casse" element={<><Casse /></>} />
            <Route path="/dashboard" element={<p>tableau de bord</p>} />
          </Routes>
        </ErrorBoundary>
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { level: 1, name: /n’a pas pu s’afficher/ }))
      .toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: 'Retour au tableau de bord' }))

    expect(screen.getByText('tableau de bord')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { level: 1, name: /n’a pas pu s’afficher/ }))
      .not.toBeInTheDocument()
  })

  it('journalise la pile de composants, seule information de diagnostic', () => {
    render(
      <MemoryRouter>
        <ErrorBoundary><Casse /></ErrorBoundary>
      </MemoryRouter>
    )

    expect(console.error).toHaveBeenCalledWith(
      'Erreur de rendu attrapée :',
      expect.any(Error),
      expect.anything()
    )
  })
})

/**
 * La frontière est montée **deux fois** : dans `Layout` (autour du contenu de
 * page, ce qui préserve la navigation) et dans `App` (autour de `<Routes>`,
 * pour les pages publiques). Ce test vérifie que l'imbrication se comporte
 * comme prévu — React s'arrête toujours à la frontière la plus proche.
 */
describe('Frontières imbriquées', () => {
  it('la plus proche attrape, la plus haute ne bouge pas', () => {
    render(
      <MemoryRouter>
        <ErrorBoundary>
          <p>chrome conservé</p>
          <ErrorBoundary><Casse /></ErrorBoundary>
        </ErrorBoundary>
      </MemoryRouter>
    )

    // Le chrome extérieur survit : c'est tout l'intérêt de la frontière
    // intérieure de `Layout`, qui garde l'en-tête et le pied.
    expect(screen.getByText('chrome conservé')).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 1, name: /n’a pas pu s’afficher/ }))
      .toHaveLength(1)
  })
})
