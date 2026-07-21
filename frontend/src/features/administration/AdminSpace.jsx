import { useCallback, useEffect, useState } from 'react'
import administrationApi from '@/services/api/administrationApi'
import cohortsApi from '@/services/api/cohortsApi'
import { ROLE_LABELS, ROLES } from '@/constants/roles'
import './AdminSpace.css'

const TABS = [
  { key: 'overview', label: 'Pilotage' },
  { key: 'trainers', label: 'Formateurs' },
  { key: 'cohorts', label: 'Classes' },
  { key: 'unassigned', label: 'Sans classe' },
  { key: 'accounts', label: 'Comptes' },
  { key: 'audit', label: 'Journal' },
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
  const [auditEntries, setAuditEntries] = useState([])
  const [auditActions, setAuditActions] = useState([])
  const [auditFilter, setAuditFilter] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)

  const loadUsers = useCallback(
    (params) => administrationApi.getUsers(params).then(setUsers).catch(() => setUsers([])),
    []
  )

  const loadCohorts = useCallback(
    () => cohortsApi.listCohorts().then(setCohorts).catch(() => setCohorts([])),
    []
  )

  const loadAudit = useCallback(
    (action) =>
      administrationApi
        .getAuditLog(action ? { action } : {})
        .then(setAuditEntries)
        .catch(() => setAuditEntries([])),
    []
  )

  useEffect(() => {
    administrationApi.getOverview().then(setOverview).catch(() => setOverview(null))
    administrationApi.getTrainers().then(setTrainers).catch(() => setTrainers([]))
    administrationApi.getAuditActions().then(setAuditActions).catch(() => setAuditActions([]))
    loadCohorts()
  }, [loadCohorts])

  useEffect(() => {
    if (tab === 'unassigned') loadUsers({ unassigned: 'true' })
    if (tab === 'accounts') loadUsers(search ? { search } : {})
    if (tab === 'audit') loadAudit(auditFilter)
  }, [tab, search, auditFilter, loadUsers, loadAudit])

  const run = async (action, message) => {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await action()
      setNotice(message)
      const freshOverview = await administrationApi.getOverview()
      setOverview(freshOverview)
      // Toute action d'administration produit une entrée de journal : le
      // rafraîchir systématiquement rend la traçabilité visible au moment même
      // où l'on agit, plutôt qu'à la prochaine visite de l'onglet.
      await Promise.all([
        loadCohorts(),
        loadAudit(auditFilter),
        tab === 'unassigned' ? loadUsers({ unassigned: 'true' }) : null,
        tab === 'accounts' ? loadUsers(search ? { search } : {}) : null,
      ])
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.trainer_id?.[0] ||
          'Action impossible.'
      )
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

        {tab === 'cohorts' && (
          <Cohorts
            cohorts={overview?.per_cohort || []}
            trainers={trainers}
            busy={busy}
            onCreate={(payload) =>
              run(() => administrationApi.createCohort(payload), 'Classe créée.')
            }
            onSetTrainer={(cohortId, trainerId) =>
              run(
                () => administrationApi.setCohortTrainer(cohortId, trainerId),
                'Formateur affecté.'
              )
            }
          />
        )}

        {tab === 'audit' && (
          <AuditJournal
            entries={auditEntries}
            actions={auditActions}
            filter={auditFilter}
            onFilter={setAuditFilter}
          />
        )}

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
        {/* Ces deux chiffres désignent des personnes, pas des volumes : un
            total d'activités qui monte peut masquer une moitié de promo à
            l'arrêt. */}
        <AdminStat
          value={activity.stalled_learners}
          label={`Décrochés (${activity.stalled_after_days} j)`}
          alert={activity.stalled_learners > 0}
        />
        <AdminStat
          value={activity.never_started_learners}
          label="Jamais démarré"
          alert={activity.never_started_learners > 0}
        />
      </div>

      <ActivityTrend activity={activity} />

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

function ActivityTrend({ activity }) {
  const trend = activity?.trend || []
  if (trend.length === 0) return null

  // Échelle rapportée au jour le plus chargé : une courbe à échelle fixe
  // paraîtrait plate dès que le volume baisse.
  const peak = Math.max(...trend.map((day) => day.count), 1)
  const total = trend.reduce((sum, day) => sum + day.count, 0)

  return (
    <section className="admin-card">
      <h2 className="admin-card__title">Activité sur 30 jours</h2>
      <p className="admin-card__hint">
        {total} activité(s) enregistrée(s), maximum {peak} sur une journée.
      </p>

      <div className="admin-trend" role="img"
        aria-label={`Activité quotidienne sur 30 jours, ${total} au total`}
      >
        {trend.map((day) => (
          <div
            key={day.date}
            className="admin-trend__bar"
            style={{ height: `${Math.round((day.count / peak) * 100)}%` }}
            title={`${day.date} — ${day.count}`}
          />
        ))}
      </div>

      <div className="admin-trend__axis">
        <span>{trend[0].date}</span>
        <span>{trend[trend.length - 1].date}</span>
      </div>
    </section>
  )
}

function Cohorts({ cohorts, trainers, busy, onCreate, onSetTrainer }) {
  const [name, setName] = useState('')
  const [trainerId, setTrainerId] = useState('')

  const submit = (event) => {
    event.preventDefault()
    if (!name.trim()) return
    onCreate({ name: name.trim(), trainer_id: trainerId || null })
    setName('')
    setTrainerId('')
  }

  return (
    <>
      <section className="admin-card">
        <h2 className="admin-card__title">Créer une classe</h2>
        <p className="admin-card__hint">
          En tant qu’administrateur, vous désignez le formateur responsable —
          un formateur, lui, ne peut créer une classe que pour lui-même.
        </p>

        <form className="admin-form" onSubmit={submit}>
          <label className="sr-only" htmlFor="cohort-name">Nom de la classe</label>
          <input
            id="cohort-name"
            className="auth-form__input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nom de la classe…"
          />

          <label className="sr-only" htmlFor="cohort-trainer">Formateur responsable</label>
          <select
            id="cohort-trainer"
            className="admin-select"
            value={trainerId}
            onChange={(e) => setTrainerId(e.target.value)}
          >
            <option value="">Sans formateur</option>
            {trainers.map((trainer) => (
              <option key={trainer.id} value={trainer.id}>
                {trainer.full_name || trainer.email}
              </option>
            ))}
          </select>

          <button type="submit" className="admin-action" disabled={busy || !name.trim()}>
            Créer
          </button>
        </form>
      </section>

      <section className="admin-card">
        <h2 className="admin-card__title">Affectation des formateurs</h2>
        {cohorts.length === 0 ? (
          <p className="admin-empty">Aucune classe pour l’instant.</p>
        ) : (
          <ul className="admin-list">
            {cohorts.map((cohort) => (
              <li key={cohort.id} className="admin-list__item">
                <div className="admin-list__main">
                  <strong>{cohort.name}</strong>
                  <span className="admin-list__meta">
                    {cohort.member_count} apprenant(s)
                    {!cohort.is_active && ' · archivée'}
                  </span>
                </div>

                <label className="sr-only" htmlFor={`trainer-${cohort.id}`}>
                  Formateur de {cohort.name}
                </label>
                <select
                  id={`trainer-${cohort.id}`}
                  className="admin-select"
                  value={cohort.trainer_id || ''}
                  disabled={busy}
                  onChange={(e) => onSetTrainer(cohort.id, e.target.value || null)}
                >
                  <option value="">Sans formateur</option>
                  {trainers.map((trainer) => (
                    <option key={trainer.id} value={trainer.id}>
                      {trainer.full_name || trainer.email}
                    </option>
                  ))}
                </select>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  )
}

function AuditJournal({ entries, actions, filter, onFilter }) {
  return (
    <section className="admin-card">
      <h2 className="admin-card__title">Journal d’audit</h2>
      <p className="admin-card__hint">
        Trace de chaque action d’administration. Les identités affichées sont
        celles <strong>figées au moment de l’acte</strong> : c’est ce qui rend
        une anonymisation vérifiable après coup. Le journal est en lecture
        seule, y compris pour un administrateur.
      </p>

      <label className="sr-only" htmlFor="audit-filter">Filtrer par type d’action</label>
      <select
        id="audit-filter"
        className="admin-select admin-card__search"
        value={filter}
        onChange={(e) => onFilter(e.target.value)}
      >
        <option value="">Toutes les actions</option>
        {actions.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>

      {entries.length === 0 ? (
        <p className="admin-empty">Aucune action enregistrée.</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Auteur</th>
              <th>Action</th>
              <th>Cible</th>
              <th>Détail</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id}>
                <td>{new Date(entry.created_at).toLocaleString('fr-FR')}</td>
                <td>{entry.actor_label}</td>
                <td>{entry.action_label}</td>
                <td>{entry.target_label || '—'}</td>
                <td className="admin-audit__changes">{describeChanges(entry.changes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

/** Rend le couple avant/après lisible sans exposer la structure JSON brute. */
function describeChanges(changes) {
  if (!changes || Object.keys(changes).length === 0) return '—'

  const format = (value) => {
    if (value === null || value === undefined || value === '') return '∅'
    if (typeof value === 'object') {
      return Object.entries(value)
        .map(([key, item]) => `${key} : ${item}`)
        .join(', ')
    }
    return String(value)
  }

  if ('before' in changes && 'after' in changes) {
    return `${format(changes.before)} → ${format(changes.after)}`
  }
  return format(changes.after ?? changes)
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
