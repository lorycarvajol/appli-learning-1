import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter } from 'react-router-dom'
import LeaderboardPage from './LeaderboardPage'
import gamificationReducer from './gamificationSlice'
import gamificationApi from '@/services/api/gamificationApi'

/**
 * Ce que verrouille ce fichier, dans l'ordre d'importance :
 *
 * 1. La page **n'invente pas d'identité** : elle affiche le nom réduit que le
 *    serveur lui donne, et rien d'autre. C'est la seule page où un apprenant
 *    voit les autres.
 * 2. Sa propre ligne est repérable (`is_me`), et son rang reste affiché même
 *    quand il tombe hors du tableau — c'est toute l'utilité de la page pour
 *    celui qui n'est pas dans les vingt premiers.
 * 3. Retiré du classement ≠ pas encore classé : les deux donnent `me: null`
 *    côté serveur, mais pas le même message.
 */

vi.mock('@/services/api/gamificationApi', () => ({
  default: { getLeaderboard: vi.fn() },
}))

const BOARD = {
  scope: 'global',
  available: true,
  participating: true,
  total_participants: 42,
  entries: [
    { rank: 1, display_name: 'Camille D.', avatar_key: 'nova-violet', points: 900, level: 10, badges_count: 7, is_me: false },
    { rank: 1, display_name: 'Sacha B.', avatar_key: '', points: 900, level: 10, badges_count: 6, is_me: false },
    { rank: 3, display_name: 'Lory C.', avatar_key: '', points: 120, level: 2, badges_count: 2, is_me: true },
  ],
  me: { rank: 3, display_name: 'Lory C.', points: 120, level: 2, badges_count: 2, is_me: true },
}

function renderPage({ board = BOARD, showInLeaderboard = true } = {}) {
  gamificationApi.getLeaderboard.mockResolvedValue(board)

  const store = configureStore({
    reducer: {
      gamification: gamificationReducer,
      auth: (state = {
        user: { id: 'u1', profile: { show_in_leaderboard: showInLeaderboard } },
      }) => state,
    },
  })

  return render(
    <Provider store={store}>
      <MemoryRouter>
        <LeaderboardPage />
      </MemoryRouter>
    </Provider>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('LeaderboardPage', () => {
  it('affiche les noms tels que le serveur les donne, sans email', async () => {
    const { container } = renderPage()

    expect(await screen.findByText('Camille D.')).toBeInTheDocument()
    // Le masquage est fait côté serveur ; la page ne doit ni le défaire ni le
    // refaire. Un « @ » à l'écran signifierait qu'un email a traversé.
    expect(container.textContent).not.toMatch('@')
  })

  it('marque la ligne de l’utilisateur courant', async () => {
    renderPage()

    const maLigne = (await screen.findByText('Lory C.')).closest('li')
    expect(maLigne).toHaveAttribute('aria-current', 'true')
    expect(maLigne).toHaveTextContent('Vous')
  })

  it('affiche le rang personnel même hors du tableau', async () => {
    renderPage({
      board: {
        ...BOARD,
        entries: BOARD.entries.filter((entry) => !entry.is_me),
        me: { ...BOARD.me, rank: 57 },
      },
    })

    const position = await screen.findByRole('region', { name: 'Votre position' })
    expect(position).toHaveTextContent('#57')
  })

  it('distingue « retiré du classement » de « pas encore classé »', async () => {
    const horsClassement = { ...BOARD, participating: false, me: null }

    const { unmount } = renderPage({ board: horsClassement, showInLeaderboard: false })
    expect(
      await screen.findByRole('region', { name: 'Votre position' })
    ).toHaveTextContent(/retiré du classement/i)
    unmount()

    renderPage({ board: horsClassement, showInLeaderboard: true })
    expect(
      await screen.findByRole('region', { name: 'Votre position' })
    ).toHaveTextContent(/Terminez une leçon/i)
  })

  it('explique l’absence de classe au lieu d’afficher un tableau vide', async () => {
    renderPage({
      board: {
        scope: 'cohort',
        available: false,
        reason: "Vous n'êtes rattaché à aucune classe.",
        entries: [],
        total_participants: 0,
        me: null,
      },
    })

    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: 'Ma classe' }))

    expect(
      await screen.findByText(/rattaché à aucune classe/i)
    ).toBeInTheDocument()
  })

  it('demande la portée choisie au serveur', async () => {
    renderPage()
    await screen.findByText('Camille D.')

    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Ma classe' }))

    await waitFor(() => {
      expect(gamificationApi.getLeaderboard).toHaveBeenCalledWith(
        expect.objectContaining({ scope: 'cohort' })
      )
    })
  })
})
