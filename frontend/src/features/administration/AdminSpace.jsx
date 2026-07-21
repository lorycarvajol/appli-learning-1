import { useCallback, useEffect, useState } from 'react'
import administrationApi from '@/services/api/administrationApi'
import cohortsApi from '@/services/api/cohortsApi'
import { ROLE_LABELS, ROLES } from '@/constants/roles'
import './AdminSpace.css'

const TABS = [
  { key: 'overview', label: 'Pilotage' },
  { key: 'trainers', label: 'Formateurs' },
  { key: 'unassigned', label: 'Sans classe' },
  { key: 'accounts', label: 'Comptes' },
]

const DJANGO_ADMIN_URL = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
).replace(/\/api\/?$/, '/admin/')

export default function AdminSpace() {
  const [tab, setTab] = useState('overview')
  const [overview, setOverview] = useState(null)
  const [trainers, setTrainers] = useState([])
  const [users, setUsers] = useState([])
  const [cohorts, setCohorts] = useState([])
  const [search, setSearch] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)

  const loadUsers = useCallback(
    (params) => administrationApi.getUsers(params).then(setUsers).catch(() => setUsers([])),
    []
  )

  useEffect(() => {
    administrationApi.getOverview().then(setOverview).catch(() => setOverview(null))
    administrationApi.getTrainers().then(setTrainers).catch(() => setTrainers([]))
    cohortsApi.listCohorts().then(setCohorts).catch(() => setCohorts([]))
  }, [])

  useEffect(() => {
    if (tab === 'unassigned') loadUsers({ unassigned: 'true' })
    if (tab === 'accounts') loadUsers(search ? { search } : {})
  }, [tab, search, loadUsers])

  const run = async (action, message) => {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await action()
      setNotice(message)
      const [freshOverview] = await Promise.all([administrationApi.getOverview()])
      setOverview(freshOverview)
      if (tab === 'unassigned') await loadUsers({ unassigned: 'true' })
      if (tab === 'accounts') await loadUsers(search ? { search } : {})
    } catch (err) {
      setError(err.response?.data?.detail || 'Action impossible.')
    } finally {
      setBusy(false)
    }
  }

  const handleAnonymize = (user) => {
    const label = user.full_name || user.email
    if (
      !window.confirm(
        `Anonymiser définitivement le compte de ${label} ?\n\n` +
          "L'identité sera effacée (email, nom, mot de passe) et le compte " +
          'désactivé. La progression est conservée mais ne désignera plus ' +
          'personne. Cette action est IRRÉVERSIBLE.'
      )
    ) {
      return
    }
    run(() => administrationApi.anonymize(user.id), 'Compte anonymisé.')
  }

  return (
    <div className="admin-space">
      <header className="admin-space__hero">
        <div className="admin-space__hero-content">
          <h1 className="admin-space__title">Administration</h1>
          <p className="admin-space__subtitle">
            Pilotage de la plateforme, formateurs et cycle de vie des comptes.
          </p>
          {/* Le CRUD de contenu reste dans l'admin Django : il le fait mieux */}
          <a
            className="admin-space__django-link"
            href={DJANGO_ADMIN_URL}
            target="_blank"
            rel="noreferrer"
          >
            Ouvrir l’admin Django (chapitres, leçons, badges…) ↗
          </a>
        </div>
      </header>

      <div className="admin-space__container">
        <nav className="admin-space__tabs" aria-label="Sections d’administration">
          {TABS.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setTab(item.key)}
              className={`admin-tab ${tab === item.key ? 'admin-tab--active' : ''}`}
              aria-pressed={tab === item.key}
            >
              {item.label}
              {item.key === 'unassigned' && overview?.users?.unassigned_learners > 0 && (
                <span className="admin-tab__badge">
                  {overview.users.unassigned_learners}
                </span>
              )}
            </button>
          ))}
        </nav>

        {error && <div className="auth-alert auth-alert--error" role="alert">{error}</div>}
        {notice && <div className="auth-alert auth-alert--success" role="status">{notice}</div>}

        {tab === 'overview' && <Overview overview={overview} />}

        {tab === 'trainers' && <Trainers trainers={trainers} />}

        {tab === 'unassigned' && (
          <Unassigned
            users={users}
            cohorts={cohorts}
            busy={busy}
            onAssign={(userId, cohortId) =>
              run(
                () => administrationApi.assignCohort(userId, cohortId),
                'Apprenant rattaché.'
              )
            }
          />
        )}

        {tab === 'accounts' && (
          <Accounts
            users={users}
            search={search}
            onSearch={setSearch}
            busy={busy}
            onSetRole={(userId, role) =>
              run(() => administrationApi.setRole(userId, role), 'Rôle modifié.')
            }
            onSetActive={(userId, isActive) =>
              run(
                () => administrationApi.setActive(userId, isActive),
                isActive ? 'Compte réactivé.' : 'Compte désactivé.'
              )
            }
            onAnonymize={handleAnonymize}
          />
        )}
      </div>
    </div>
  )
}

function Overview({ overview }) {
  if (!overview) return <p className="admin-empty">Chargement du pilotage...</p>

  const { users, cohorts, content, activity } = overview

  return (
    <>
      <div className="admin-stats">
        <AdminStat value={users.learners} label="Apprenants" />
        <AdminStat value={users.trainers} label="Formateurs" />
        <AdminStat value={cohorts.active} label="Classes actives" />
        <AdminStat
          value={users.unassigned_learners}
          label="Sans classe"
          alert={users.unassigned_learners > 0}
        />
        <AdminStat
          value={cohorts.without_trainer}
          label="Classes orphelines"
          alert={cohorts.without_trainer > 0}
        />
        <AdminStat value={users.inactive} label="Comptes désactivés" />
        <AdminStat value={content.chapters} label="Chapitres publiés" />
        <AdminStat value={activity.last_7_days} label="Activités (7 j)" />
      </div>

      <section className="admin-card">
        <h2 className="admin-card__title">Avancement par classe</h2>
        {overview.per_cohort.length === 0 ? (
          <p className="admin-empty">Aucune classe pour l’instant.</p>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Classe</th>
                <th>Formateur</th>
                <th>Effectif</th>
                <th>Complétion</th>
              </tr>
            </thead>
            <tbody>
              {overview.per_cohort.map((cohort) => (
                <tr key={cohort.id}>
                  <td>{cohort.name}</td>
                  <td>
                    {cohort.trainer_name || (
                      <span className="admin-warn">sans formateur</span>
                    )}
                  </td>
                  <td>{cohort.member_count}</td>
                  <td>
                    <div className="admin-bar">
                      <div
                        className="admin-bar__fill"
                        style={{ width: `${cohort.completion_rate}%` }}
                      />
                    </div>
                    <span className="admin-bar__label">{cohort.completion_rate} %</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  )
}

function AdminStat({ value, label, alert }) {
  return (
    <div className={`admin-stat ${alert ? 'admin-stat--alert' : ''}`}>
      <span className="admin-stat__value">{value}</span>
      <span className="admin-stat__label">{label}</span>
    </div>
  )
}

function Trainers({ trainers }) {
  return (
    <section className="admin-card">
      <h2 className="admin-card__title">Formateurs</h2>
      <p className="admin-card__hint">
        Pour en recruter un, générez une invitation de rôle « formateur » depuis
        l’espace formateur — seul un administrateur peut en émettre.
      </p>

      {trainers.length === 0 ? (
        <p className="admin-empty">Aucun formateur.</p>
      ) : (
        <ul className="admin-list">
          {trainers.map((trainer) => (
            <li key={trainer.id} className="admin-list__item">
              <div className="admin-list__main">
                <strong>{trainer.full_name || trainer.email}</strong>
                <span className="admin-list__meta">{trainer.email}</span>
              </div>
              <div className="admin-list__cohorts">
                {trainer.cohorts.length === 0 ? (
                  <span className="admin-list__meta">aucune classe</span>
                ) : (
                  trainer.cohorts.map((cohort) => (
                    <span key={cohort.id} className="admin-pill">
                      {cohort.name} · {cohort.member_count}
                    </span>
                  ))
                )}
              </div>
              <span className="admin-list__count">
                {trainer.learner_count} apprenant(s)
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Unassigned({ users, cohorts, busy, onAssign }) {
  return (
    <section className="admin-card">
      <h2 className="admin-card__title">Apprenants sans classe</h2>
      <p className="admin-card__hint">
        Ils progressent en rythme libre et ne sont visibles d’aucun formateur.
        Les rattacher les rend suivis — sans jamais leur retirer un accès déjà
        obtenu.
      </p>

      {users.length === 0 ? (
        <p className="admin-empty">Tous les apprenants sont rattachés.</p>
      ) : (
        <ul className="admin-list">
          {users.map((user) => (
            <li key={user.id} className="admin-list__item">
              <div className="admin-list__main">
                <strong>{user.full_name || user.email}</strong>
                <span className="admin-list__meta">{user.email}</span>
              </div>
              <span className="admin-list__count">{user.total_points} pts</span>
              <label className="sr-only" htmlFor={`assign-${user.id}`}>
                Rattacher {user.email} à une classe
              </label>
              <select
                id={`assign-${user.id}`}
                className="admin-select"
                disabled={busy || cohorts.length === 0}
                defaultValue=""
                onChange={(e) => e.target.value && onAssign(user.id, e.target.value)}
              >
                <option value="">Rattacher à…</option>
                {cohorts.map((cohort) => (
                  <option key={cohort.id} value={cohort.id}>
                    {cohort.name}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Accounts({ users, search, onSearch, busy, onSetRole, onSetActive, onAnonymize }) {
  return (
    <section className="admin-card">
      <h2 className="admin-card__title">Comptes</h2>

      <label className="sr-only" htmlFor="admin-search">Rechercher un compte</label>
      <input
        id="admin-search"
        type="search"
        value={search}
        onChange={(e) => onSearch(e.target.value)}
        placeholder="Rechercher par email ou nom…"
        className="auth-form__input admin-card__search"
      />

      {users.length === 0 ? (
        <p className="admin-empty">Aucun compte trouvé.</p>
      ) : (
        <ul className="admin-list">
          {users.map((user) => (
            <li key={user.id} className="admin-list__item">
              <div className="admin-list__main">
                <strong>{user.full_name || user.email}</strong>
                <span className="admin-list__meta">
                  {user.email}
                  {user.cohort_name && ` · ${user.cohort_name}`}
                  {!user.is_active && ' · désactivé'}
                  {user.is_anonymized && ' · anonymisé'}
                </span>
              </div>

              <label className="sr-only" htmlFor={`role-${user.id}`}>
                Rôle de {user.email}
              </label>
              <select
                id={`role-${user.id}`}
                className="admin-select"
                value={user.role}
                disabled={busy || user.is_anonymized}
                onChange={(e) => onSetRole(user.id, e.target.value)}
              >
                {Object.values(ROLES).map((role) => (
                  <option key={role} value={role}>
                    {ROLE_LABELS[role]}
                  </option>
                ))}
              </select>

              <button
                type="button"
                className="admin-action"
                disabled={busy || user.is_anonymized}
                onClick={() => onSetActive(user.id, !user.is_active)}
              >
                {user.is_active ? 'Désactiver' : 'Réactiver'}
              </button>

              <button
                type="button"
                className="admin-action admin-action--danger"
                disabled={busy || user.is_anonymized}
                onClick={() => onAnonymize(user)}
              >
                Anonymiser
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
