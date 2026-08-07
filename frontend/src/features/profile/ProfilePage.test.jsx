import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import ProfilePage from './ProfilePage'
import authReducer from '@/features/auth/authSlice'
import { authApi } from '@/services/api/authApi'

vi.mock('@/services/api/authApi', () => ({
  authApi: { updateProfile: vi.fn(), changePassword: vi.fn() },
}))
vi.mock('@/services/api/gamificationApi', () => ({
  default: { getSummary: vi.fn().mockResolvedValue({ streak: { current_streak: 4 } }) },
}))

const USER = {
  id: 'u1',
  email: 'eve@example.com',
  first_name: 'Eve',
  last_name: 'Martin',
  role: 'LEARNER',
  profile: {
    bio: '', github_username: '', avatar_key: '', theme: 'AUTO',
    total_points: 120, level: 2,
  },
}

function renderPage(user = USER) {
  const store = configureStore({
    reducer: {
      auth: authReducer,
      gamification: (state = { summary: null }) => state,
    },
    preloadedState: {
      auth: { user, isAuthenticated: true, initialized: true, loading: false, error: null },
    },
  })
  return { store, ...render(<Provider store={store}><ProfilePage /></Provider>) }
}

beforeEach(() => {
  // Contrat uniforme : les services renvoient les données déjà déballées,
  // pas la réponse axios (cf. services/api/contract.test.js).
  authApi.updateProfile.mockResolvedValue(USER)
  authApi.changePassword.mockResolvedValue({})
})

describe('ProfilePage', () => {
  it('affiche la progression sans permettre de la modifier', async () => {
    renderPage()

    // Les points sont un solde dérivé du grand livre : ils s'affichent, mais
    // aucun champ de saisie ne doit les exposer.
    //
    // On vise les rôles de saisie de valeur plutôt que « tout libellé
    // contenant "points" » : la case « apparaître dans le classement »
    // mentionne légitimement les points dans sa légende, et la version large
    // la comptait comme une violation. C'est bien un champ éditant le solde
    // qu'il s'agit d'interdire, pas le mot.
    expect(await screen.findByText('120')).toBeInTheDocument()
    expect(screen.queryByRole('textbox', { name: /points/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('spinbutton', { name: /points/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('slider', { name: /points/i })).not.toBeInTheDocument()
  })

  it('présente la personne : pseudo, rôle, classe et bio', async () => {
    renderPage({
      ...USER,
      profile: {
        ...USER.profile,
        github_username: 'evemartin',
        bio: 'Je découvre le web, une balise à la fois.',
        cohort_name: 'Promo 2026',
      },
    })

    const titre = await screen.findByRole('heading', { name: 'Eve Martin', level: 1 })
    // La bio et le pseudo apparaissent **aussi** dans le formulaire plus bas :
    // on interroge le bandeau, pas la page, sinon l'assertion ne prouve rien.
    const bandeau = within(titre.closest('header'))

    // Le pseudo mène au compte GitHub : l'afficher sans y conduire n'aurait
    // servi à rien.
    const pseudo = bandeau.getByRole('link', { name: 'Profil GitHub de evemartin' })
    expect(pseudo).toHaveAttribute('href', 'https://github.com/evemartin')
    expect(pseudo).toHaveTextContent('@evemartin')

    expect(bandeau.getByText('Apprenant')).toBeInTheDocument()
    expect(bandeau.getByText('Promo 2026')).toBeInTheDocument()
    expect(bandeau.getByText('Je découvre le web, une balise à la fois.')).toBeInTheDocument()
  })

  it('invite à écrire une bio quand il n’y en a pas', async () => {
    renderPage()

    // Un bandeau vide n'invite à rien. On dit quoi faire, pas « aucune bio ».
    expect(await screen.findByText('Ajoutez une phrase pour vous présenter.'))
      .toBeInTheDocument()
    // Rien à afficher ⇒ rien d'affiché : pas de « @ » orphelin ni de puce vide.
    expect(screen.queryByRole('link', { name: /Profil GitHub/ })).not.toBeInTheDocument()
  })

  it('ne répète pas les chiffres de la progression dans le bandeau', async () => {
    renderPage()

    // Points, niveau, série et trophées vivent dans la carte « Ma progression »
    // juste en dessous. Les remonter dans le bandeau ferait un doublon, et
    // écraserait la bio — la seule chose que l'apprenant écrit lui-même.
    const bandeau = (await screen.findByRole('heading', { name: 'Eve Martin', level: 1 }))
      .closest('header')
    expect(bandeau).not.toHaveTextContent('120')
    expect(bandeau).not.toHaveTextContent('Niveau')
  })

  it('ne déplie le catalogue qu’à la demande', async () => {
    const user = userEvent.setup()
    renderPage()

    // Quarante-deux visages ouverts d'emblée repoussaient hors de vue tout le
    // reste du profil, alors qu'on ne change d'avatar qu'une fois.
    const bascule = await screen.findByRole('button', { name: 'Changer d’avatar' })
    expect(bascule).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('radio', { name: 'Avatar nova' })).not.toBeInTheDocument()

    await user.click(bascule)
    expect(screen.getByRole('radio', { name: 'Avatar nova' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Fermer les avatars' }))
      .toHaveAttribute('aria-expanded', 'true')
  })

  it('enregistre l’avatar choisi dans la galerie', async () => {
    const user = userEvent.setup()
    renderPage()

    // Le choix se fait en deux temps depuis que le catalogue compte sept
    // familles : le visage d'abord — la palette par défaut s'applique — puis
    // la couleur de fond. Ce test vérifie que les deux se recombinent en une
    // seule clé `<visage>-<palette>`, la seule forme que le serveur accepte.
    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    await user.click(screen.getByRole('radio', { name: 'Avatar nova' }))
    await user.click(screen.getByRole('radio', { name: 'Fond turquoise' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ avatar_key: 'nova-teal' }),
        })
      )
    })
  })

  it('présente la couleur et la bordure AVANT les visages', async () => {
    const user = userEvent.setup()
    renderPage({ ...USER, profile: { ...USER.profile, avatar_key: 'nova-violet' } })

    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))

    // ⚠️ Ces deux réglages étaient relégués après les sept familles, à plus de
    // 1 000 px du haut : l'exploitant a cru la couleur de fond disparue. Ils
    // doivent précéder les visages, qui se prévisualisent alors dans la
    // combinaison choisie.
    const titres = screen.getAllByRole('heading', { level: 3 }).map((h) => h.textContent)
    expect(titres.slice(0, 2)).toEqual(['Couleur du fond', 'Bordure'])
  })

  it('enregistre la bordure choisie', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    await user.click(screen.getByRole('radio', { name: 'Bordure Double liseré' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ avatar_border: 'double' }),
        })
      )
    })
  })

  it('propose la bordure même sans visage choisi', async () => {
    const user = userEvent.setup()
    renderPage()

    // La bordure habille la vignette, pas le dessin : elle vaut aussi pour
    // les initiales. La couleur du fond, elle, vient du nom dans ce cas — d'où
    // son absence.
    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    expect(screen.getByRole('radio', { name: 'Bordure Halo' })).toBeInTheDocument()
    expect(screen.queryByRole('radio', { name: 'Fond turquoise' })).not.toBeInTheDocument()
  })

  it('n’offre pas de couleur de fond tant qu’aucun visage n’est choisi', async () => {
    const user = userEvent.setup()
    renderPage()

    // Sans visage, le fond vient du nom (repli à initiales, déterministe) :
    // des palettes sans effet se liraient comme une panne.
    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    expect(screen.getByRole('radio', { name: 'Mes initiales' })).toBeInTheDocument()
    expect(screen.queryByRole('radio', { name: 'Fond turquoise' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('radio', { name: 'Avatar bottts3' }))
    expect(screen.getByRole('radio', { name: 'Fond turquoise' })).toBeInTheDocument()
  })

  it('affiche l’auteur et la licence de chaque famille de visages', async () => {
    const user = userEvent.setup()
    renderPage()

    // Quatre des sept familles sont en CC BY 4.0 : l'attribution est une
    // obligation, pas une décoration. La retirer du sélecteur doit rougir.
    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    expect(screen.getByText('Zoish · CC0 1.0')).toBeInTheDocument()
    // Lisa Wischofsky signe deux familles (Adventurer et sa variante neutre) :
    // la ligne apparaît donc deux fois, une par famille.
    expect(screen.getAllByText('Lisa Wischofsky · CC BY 4.0')).toHaveLength(2)
    expect(screen.getByText('Ashley Seo · CC BY 4.0')).toBeInTheDocument()
    expect(screen.getByText('Johan Melin · CC BY 4.0')).toBeInTheDocument()
  })

  it('permet de revenir aux initiales', async () => {
    const user = userEvent.setup()
    renderPage({ ...USER, profile: { ...USER.profile, avatar_key: 'prism-amber' } })

    await user.click(await screen.findByRole('button', { name: 'Changer d’avatar' }))
    await user.click(screen.getByRole('radio', { name: 'Mes initiales' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ avatar_key: '' }),
        })
      )
    })
  })

  it('permet de se retirer du classement', async () => {
    const user = userEvent.setup()
    renderPage()

    // Coché par défaut : un profil qui ne mentionne pas le réglage vaut
    // « visible », sinon l'enregistrement d'un tout autre champ retirerait du
    // classement quelqu'un qui n'a rien demandé.
    const caseAcocher = await screen.findByRole('checkbox', {
      name: /Apparaître dans le classement/i,
    })
    expect(caseAcocher).toBeChecked()

    await user.click(caseAcocher)
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ show_in_leaderboard: false }),
        })
      )
    })
  })

  it('n’envoie jamais les points ni le rôle au serveur', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => expect(authApi.updateProfile).toHaveBeenCalled())
    const payload = authApi.updateProfile.mock.calls[0][0]
    expect(payload.role).toBeUndefined()
    expect(payload.profile.total_points).toBeUndefined()
    expect(payload.profile.level).toBeUndefined()
  })

  it('refuse un changement de mot de passe mal confirmé sans appeler l’API', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(await screen.findByLabelText('Mot de passe actuel'), 'ancien-mdp')
    await user.type(screen.getByLabelText('Nouveau mot de passe'), 'nouveau-mdp-solide')
    await user.type(screen.getByLabelText('Confirmer'), 'faute-de-frappe')
    await user.click(screen.getByRole('button', { name: 'Changer le mot de passe' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/ne correspondent pas/)
    expect(authApi.changePassword).not.toHaveBeenCalled()
  })

  it('affiche un message d’erreur lisible plutôt que l’objet brut de DRF', async () => {
    // DRF répond {profile: {avatar_key: ["…"]}} : rendu tel quel, l'utilisateur
    // lirait « [object Object] ».
    authApi.updateProfile.mockRejectedValue({
      response: { data: { profile: { avatar_key: ['Cet avatar ne fait pas partie du catalogue.'] } } },
    })
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Enregistrer' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Cet avatar ne fait pas partie du catalogue.'
    )
  })
})
