import { useCallback, useEffect, useState } from 'react'
import cohortsApi from '@/services/api/cohortsApi'
import coursesApi from '@/services/api/coursesApi'
import './CohortsPanel.css'

/**
 * Gestion des classes par le formateur : créer une classe, générer le lien à
 * diffuser, voir les membres, ouvrir un chapitre à toute la promo.
 *
 * Le lien est affiché en clair et copiable : c'est précisément pourquoi le
 * jeton est stocké non haché côté serveur — un formateur le recopie souvent.
 */
export default function CohortsPanel() {
  const [cohorts, setCohorts] = useState([])
  const [invites, setInvites] = useState([])
  const [chapters, setChapters] = useState([])
  const [selected, setSelected] = useState(null)
  const [members, setMembers] = useState([])
  const [newName, setNewName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const [cohortList, inviteList] = await Promise.all([
        cohortsApi.listCohorts(),
        cohortsApi.listInvites(),
      ])
      setCohorts(cohortList)
      setInvites(inviteList)
      setSelected((current) => current ?? cohortList[0]?.id ?? null)
    } catch {
      setError('Impossible de charger les classes.')
    }
  }, [])

  useEffect(() => {
    refresh()
    coursesApi
      .getChapters()
      .then((data) => setChapters(data.results ?? data))
      .catch(() => setChapters([]))
  }, [refresh])

  useEffect(() => {
    if (!selected) {
      setMembers([])
      return
    }
    cohortsApi.getMembers(selected).then(setMembers).catch(() => setMembers([]))
  }, [selected])

  const run = async (action, onDone) => {
    setBusy(true)
    setError(null)
    try {
      await action()
      if (onDone) await onDone()
    } catch (err) {
      const detail = err.response?.data
      const first = detail && Object.values(detail)[0]
      setError(Array.isArray(first) ? first[0] : first || 'Opération impossible.')
    } finally {
      setBusy(false)
    }
  }

  const handleCreateCohort = (e) => {
    e.preventDefault()
    if (!newName.trim()) return
    run(
      () => cohortsApi.createCohort({ name: newName.trim() }),
      async () => {
        setNewName('')
        await refresh()
      }
    )
  }

  const handleCreateInvite = () =>
    run(() => cohortsApi.createInvite({ cohort: selected }), refresh)

  const handleRevoke = (inviteId) =>
    run(() => cohortsApi.revokeInvite(inviteId), refresh)

  const handleUnlock = (chapterId) =>
    run(() => cohortsApi.unlockChapterForCohort(selected, chapterId))

  const handleRemove = (userId) =>
    run(
      () => cohortsApi.removeMember(selected, userId),
      () => cohortsApi.getMembers(selected).then(setMembers)
    )

  const copyLink = async (url, inviteId) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopied(inviteId)
      setTimeout(() => setCopied(null), 2000)
    } catch {
      setError('Copie impossible — sélectionnez le lien manuellement.')
    }
  }

  const cohortInvites = invites.filter((i) => i.cohort === selected)
  const selectedCohort = cohorts.find((c) => c.id === selected)

  return (
    <div className="cohorts-panel">
      {error && (
        <div className="auth-alert auth-alert--error" role="alert">{error}</div>
      )}

      <section className="cohorts-panel__section">
        <h3 className="cohorts-panel__title">Mes classes</h3>

        {cohorts.length === 0 ? (
          <p className="cohorts-panel__empty">
            Aucune classe pour l’instant. Créez-en une pour inviter vos apprenants.
          </p>
        ) : (
          <div className="cohorts-panel__chips">
            {cohorts.map((cohort) => (
              <button
                key={cohort.id}
                type="button"
                onClick={() => setSelected(cohort.id)}
                className={`cohort-chip ${
                  selected === cohort.id ? 'cohort-chip--active' : ''
                }`}
                aria-pressed={selected === cohort.id}
              >
                {cohort.name}
                <span className="cohort-chip__count">{cohort.member_count}</span>
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleCreateCohort} className="cohorts-panel__create">
          <label htmlFor="new-cohort" className="sr-only">Nom de la classe</label>
          <input
            id="new-cohort"
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Nom de la nouvelle classe"
            className="auth-form__input"
          />
          <button type="submit" disabled={busy} className="cohorts-panel__button">
            Créer
          </button>
        </form>
      </section>

      {selectedCohort && (
        <>
          <section className="cohorts-panel__section">
            <h3 className="cohorts-panel__title">
              Liens d’invitation — {selectedCohort.name}
            </h3>
            <p className="cohorts-panel__hint">
              Diffusez ce lien par le canal de votre choix. Il expire
              automatiquement et reste révocable à tout moment.
            </p>

            {cohortInvites.length === 0 ? (
              <p className="cohorts-panel__empty">Aucun lien actif.</p>
            ) : (
              <ul className="invite-list">
                {cohortInvites.map((invite) => (
                  <li key={invite.id} className="invite">
                    <code className="invite__url">{invite.url}</code>
                    <div className="invite__meta">
                      <span
                        className={`invite__state ${
                          invite.is_usable ? '' : 'invite__state--dead'
                        }`}
                      >
                        {invite.is_usable
                          ? `actif — ${invite.uses_count} utilisation(s)`
                          : invite.invalid_reason}
                      </span>
                      <button
                        type="button"
                        onClick={() => copyLink(invite.url, invite.id)}
                        className="invite__action"
                      >
                        {copied === invite.id ? 'Copié !' : 'Copier'}
                      </button>
                      {invite.is_usable && (
                        <button
                          type="button"
                          onClick={() => handleRevoke(invite.id)}
                          className="invite__action invite__action--danger"
                          disabled={busy}
                        >
                          Révoquer
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}

            <button
              type="button"
              onClick={handleCreateInvite}
              disabled={busy}
              className="cohorts-panel__button"
            >
              Générer un nouveau lien
            </button>
          </section>

          <section className="cohorts-panel__section">
            <h3 className="cohorts-panel__title">Ouvrir un chapitre à la classe</h3>
            <div className="cohorts-panel__chips">
              {chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  type="button"
                  onClick={() => handleUnlock(chapter.id)}
                  disabled={busy}
                  className="cohort-chip"
                >
                  🔓 {chapter.title}
                </button>
              ))}
            </div>
          </section>

          <section className="cohorts-panel__section">
            <h3 className="cohorts-panel__title">
              Membres ({members.length})
            </h3>
            {members.length === 0 ? (
              <p className="cohorts-panel__empty">
                Personne n’a encore rejoint cette classe.
              </p>
            ) : (
              <ul className="member-list">
                {members.map((member) => (
                  <li key={member.id} className="member">
                    <span className="member__name">
                      {member.full_name || member.email}
                    </span>
                    <span className="member__points">{member.total_points} pts</span>
                    <button
                      type="button"
                      onClick={() => handleRemove(member.id)}
                      disabled={busy}
                      className="invite__action invite__action--danger"
                    >
                      Retirer
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  )
}
