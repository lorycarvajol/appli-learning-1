import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminSpace from './AdminSpace'
import administrationApi from '@/services/api/administrationApi'
import cohortsApi from '@/services/api/cohortsApi'

vi.mock('@/services/api/administrationApi', () => ({ default: {} }))
vi.mock('@/services/api/cohortsApi', () => ({ default: {} }))

/**
 * L'espace admin concentre les actions les plus lourdes de la plateforme,
 * dont une irréversible. Ces tests portent sur ce qui protège l'utilisateur
 * de lui-même et sur ce qui rend le pouvoir vérifiable — pas sur la mise en
 * page.
 */

const OVERVIEW = {
  users: { learners: 12, trainers: 2, admins: 1, inactive: 0, unassigned_learners: 3 },
  cohorts: { total: 2, active: 2, without_trainer: 1 },
  content: { chapters: 5, lessons: 20 },
  activity: {
    lessons_completed: 40,
    last_7_days: 9,
    stalled_learners: 2,
    never_started_learners: 1,
    stalled_after_days: 14,
    trend: [
      { date: '2026-06-22', count: 0 },
      { date: '2026-07-21', count: 9 },
    ],
  },
  per_cohort: [
    {
      id: 'c1', name: 'Promo A', trainer_name: null, trainer_id: null,
      is_active: true, member_count: 4, completion_rate: 25,
    },
  ],
}

const TRAINERS = [
  { id: 't1', email: 'jean@example.com', full_name: 'Jean Formateur', cohorts: [], learner_count: 0 },
]

const AUDIT_ENTRIES = [
  {
    id: 'a1',
    actor_label: 'admin@example.com',
    action: 'ANONYMIZE',
    action_label: 'Anonymisation (RGPD)',
    target_label: 'eleve@example.com',
    changes: { before: 'eleve@example.com', after: 'anonyme-abc@anonymized.invalid' },
    created_at: '2026-07-21T10:00:00Z',
  },
]

beforeEach(() => {
  administrationApi.getOverview = vi.fn().mockResolvedValue(OVERVIEW)
  administrationApi.getTrainers = vi.fn().mockResolvedValue(TRAINERS)
  administrationApi.getAuditActions = vi.fn().mockResolvedValue([
    { value: 'ANONYMIZE', label: 'Anonymisation (RGPD)' },
  ])
  administrationApi.getAuditLog = vi.fn().mockResolvedValue(AUDIT_ENTRIES)
  administrationApi.getUsers = vi.fn().mockResolvedValue([
    { id: 'u1', email: 'eleve@example.com', full_name: 'Eve', role: 'LEARNER',
      is_active: true, is_anonymized: false, total_points: 10, cohort_name: null },
  ])
  administrationApi.anonymize = vi.fn().mockResolvedValue({})
  administrationApi.setCohortTrainer = vi.fn().mockResolvedValue({})
  administrationApi.createCohort = vi.fn().mockResolvedValue({})
  cohortsApi.listCohorts = vi.fn().mockResolvedValue([])
  cohortsApi.listInvites = vi.fn().mockResolvedValue([])
  cohortsApi.createInvite = vi.fn().mockResolvedValue({})
  cohortsApi.revokeInvite = vi.fn().mockResolvedValue({})
})

describe('AdminSpace', () => {
  it('signale le décrochage, pas seulement les volumes', async () => {
    render(<AdminSpace />)

    // Un total d'activités qui monte peut masquer une promo à l'arrêt :
    // ces deux chiffres désignent des personnes.
    expect(await screen.findByText('Décrochés (14 j)')).toBeInTheDocument()
    expect(screen.getByText('Jamais démarré')).toBeInTheDocument()
  })

  it('porte le nombre d’apprenants sans classe sur son onglet', async () => {
    // Ces apprenants ne sont visibles d'aucun formateur et s'accumulent en
    // silence : le compte doit se voir sans ouvrir l'onglet.
    render(<AdminSpace />)
    expect(await screen.findByRole('button', { name: /Sans classe\s*3/ })).toBeInTheDocument()
  })

  it('n’anonymise pas sans confirmation explicite', async () => {
    // L'action est irréversible : un clic seul ne doit jamais suffire.
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Comptes' }))
    await user.click(await screen.findByRole('button', { name: 'Anonymiser' }))

    expect(window.confirm).toHaveBeenCalled()
    expect(administrationApi.anonymize).not.toHaveBeenCalled()
  })

  it('anonymise une fois la confirmation donnée', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Comptes' }))
    await user.click(await screen.findByRole('button', { name: 'Anonymiser' }))

    await waitFor(() => expect(administrationApi.anonymize).toHaveBeenCalledWith('u1'))
  })

  it('affiche l’identité figée dans le journal, pas l’identité courante', async () => {
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Journal' }))

    // Tout l'intérêt de la trace : après anonymisation, le compte n'a plus
    // cet email, mais le journal le conserve.
    expect(await screen.findByText('eleve@example.com')).toBeInTheDocument()
    expect(screen.getByText(/anonyme-abc@anonymized\.invalid/)).toBeInTheDocument()
  })

  it('recharge le journal après une action, pour rendre la trace immédiate', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Comptes' }))
    administrationApi.getAuditLog.mockClear()
    await user.click(await screen.findByRole('button', { name: 'Anonymiser' }))

    await waitFor(() => expect(administrationApi.getAuditLog).toHaveBeenCalled())
  })

  it('permet de rattraper une classe orpheline', async () => {
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Classes' }))
    await user.selectOptions(
      await screen.findByLabelText('Formateur de Promo A'),
      't1'
    )

    await waitFor(() =>
      expect(administrationApi.setCohortTrainer).toHaveBeenCalledWith('c1', 't1')
    )
  })

  it('génère une invitation de rôle formateur', async () => {
    // La création d'une invitation formateur n'existait que côté API : elle a
    // désormais un bouton dans l'espace admin, et vise bien le rôle TRAINER.
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Formateurs' }))
    await user.click(
      await screen.findByRole('button', { name: /Générer un lien d’invitation formateur/ })
    )

    await waitFor(() =>
      expect(cohortsApi.createInvite).toHaveBeenCalledWith({ role: 'TRAINER' })
    )
  })

  it('n’affiche jamais le lien d’une invitation révoquée', async () => {
    // « supprime les liens d'invitation révoquée » : seul un lien actif est
    // montré ; le lien mort disparaît (sa trace reste au journal).
    cohortsApi.listInvites.mockResolvedValue([
      { id: 'i1', role: 'TRAINER', cohort: null, is_usable: true,
        uses_count: 0, url: 'http://x/rejoindre/ACTIF' },
      { id: 'i2', role: 'TRAINER', cohort: null, is_usable: false,
        invalid_reason: 'révoquée', uses_count: 0, url: 'http://x/rejoindre/REVOQUE' },
    ])
    const user = userEvent.setup()
    render(<AdminSpace />)

    await user.click(await screen.findByRole('button', { name: 'Formateurs' }))

    expect(await screen.findByText(/rejoindre\/ACTIF/)).toBeInTheDocument()
    expect(screen.queryByText(/rejoindre\/REVOQUE/)).not.toBeInTheDocument()
  })
})
