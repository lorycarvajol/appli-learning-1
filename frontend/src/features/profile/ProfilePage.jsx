import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { changePassword, updateProfile, logoutUser } from '@/features/auth/authSlice'
import { fetchGamificationSummary } from '@/features/gamification/gamificationSlice'
import { authApi } from '@/services/api/authApi'
import Avatar from '@/components/ui/Avatar'
import PasswordInput from '@/components/ui/PasswordInput'
import { ROLE_LABELS } from '@/constants/roles'
import { AVATAR_KEYS } from './avatars'
import './ProfilePage.css'

const THEMES = [
  { value: 'AUTO', label: 'Selon le système' },
  { value: 'LIGHT', label: 'Clair' },
  { value: 'DARK', label: 'Sombre' },
]

const BIO_MAX = 500

export default function ProfilePage() {
  const dispatch = useDispatch()
  const { user } = useSelector((state) => state.auth)
  const summary = useSelector((state) => state.gamification.summary)

  const [form, setForm] = useState(null)
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState(null)
  const [error, setError] = useState(null)

  // Le formulaire est initialisé depuis le store une fois l'utilisateur connu.
  // Le réinitialiser à chaque rendu écraserait la saisie en cours.
  useEffect(() => {
    if (user && !form) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        bio: user.profile?.bio || '',
        github_username: user.profile?.github_username || '',
        avatar_key: user.profile?.avatar_key || '',
        theme: user.profile?.theme || 'AUTO',
      })
    }
  }, [user, form])

  useEffect(() => {
    dispatch(fetchGamificationSummary())
  }, [dispatch])

  if (!user || !form) {
    return <p className="profile__empty">Chargement du profil...</p>
  }

  const set = (field) => (event) =>
    setForm((current) => ({ ...current, [field]: event.target.value }))

  // L'aperçu doit refléter la sélection en cours, pas l'avatar enregistré :
  // choisir sans voir le résultat rendrait la galerie inutilisable.
  const preview = {
    ...user,
    first_name: form.first_name,
    last_name: form.last_name,
    profile: { ...user.profile, avatar_key: form.avatar_key },
  }

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setNotice(null)

    const result = await dispatch(updateProfile({
      first_name: form.first_name,
      last_name: form.last_name,
      profile: {
        bio: form.bio,
        github_username: form.github_username,
        avatar_key: form.avatar_key,
        theme: form.theme,
      },
    }))

    setSaving(false)
    if (updateProfile.rejected.match(result)) {
      setError(firstError(result.payload) || 'Enregistrement impossible.')
    } else {
      setNotice('Profil enregistré.')
    }
  }

  return (
    <div className="profile">
      <header className="profile__hero">
        <Avatar user={preview} size={84} className="profile__hero-avatar" />
        <div>
          <h1 className="profile__title">
            {user.first_name || user.last_name
              ? `${user.first_name} ${user.last_name}`.trim()
              : user.email}
          </h1>
          <p className="profile__subtitle">
            {user.email} · {ROLE_LABELS[user.role] || user.role}
            {user.profile?.cohort_name && ` · ${user.profile.cohort_name}`}
          </p>
        </div>
      </header>

      <div className="profile__container">
        {error && <div className="auth-alert auth-alert--error" role="alert">{error}</div>}
        {notice && <div className="auth-alert auth-alert--success" role="status">{notice}</div>}

        <ProgressSummary profile={user.profile} summary={summary} />

        <form className="profile__card" onSubmit={submit}>
          <h2 className="profile__card-title">Mon avatar</h2>
          <p className="profile__hint">
            Sans choix, vos initiales servent d’avatar.
          </p>

          <AvatarPicker
            value={form.avatar_key}
            user={preview}
            onChange={(key) => setForm((c) => ({ ...c, avatar_key: key }))}
          />

          <h2 className="profile__card-title">Mes informations</h2>

          <div className="profile__grid">
            <Field label="Prénom" id="first_name">
              <input id="first_name" className="auth-form__input"
                value={form.first_name} onChange={set('first_name')} />
            </Field>

            <Field label="Nom" id="last_name">
              <input id="last_name" className="auth-form__input"
                value={form.last_name} onChange={set('last_name')} />
            </Field>

            <Field label="Pseudo GitHub" id="github_username">
              <input id="github_username" className="auth-form__input"
                value={form.github_username} onChange={set('github_username')}
                placeholder="mon-pseudo" />
            </Field>

            <Field label="Thème de l’interface" id="theme"
              hint="Rattaché à votre compte : il vous suit d’un poste à l’autre.">
              <select id="theme" className="admin-select"
                value={form.theme} onChange={set('theme')}>
                {THEMES.map((theme) => (
                  <option key={theme.value} value={theme.value}>{theme.label}</option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Bio" id="bio"
            hint={`${form.bio.length} / ${BIO_MAX} caractères`}>
            <textarea id="bio" className="auth-form__input profile__textarea"
              rows={4} maxLength={BIO_MAX}
              value={form.bio} onChange={set('bio')}
              placeholder="Quelques mots sur vous, votre parcours, vos objectifs…" />
          </Field>

          <button type="submit" className="profile__submit" disabled={saving}>
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </form>

        <PasswordCard />

        <DataCard />
      </div>
    </div>
  )
}

function Field({ label, id, hint, children }) {
  return (
    <div className="profile__field">
      <label className="profile__label" htmlFor={id}>{label}</label>
      {children}
      {hint && <span className="profile__field-hint">{hint}</span>}
    </div>
  )
}

function AvatarPicker({ value, user, onChange }) {
  return (
    <div className="profile__avatars" role="radiogroup" aria-label="Choix de l’avatar">
      <button
        type="button"
        role="radio"
        aria-checked={!value}
        aria-label="Mes initiales"
        className={`profile__avatar-choice ${!value ? 'profile__avatar-choice--active' : ''}`}
        onClick={() => onChange('')}
      >
        <Avatar user={{ ...user, profile: { avatar_key: '' } }} size={48} />
      </button>

      {AVATAR_KEYS.map((key) => (
        <button
          key={key}
          type="button"
          role="radio"
          aria-checked={value === key}
          aria-label={`Avatar ${key.replace('-', ' ')}`}
          className={`profile__avatar-choice ${value === key ? 'profile__avatar-choice--active' : ''}`}
          onClick={() => onChange(key)}
        >
          <Avatar user={{ profile: { avatar_key: key } }} size={48} />
        </button>
      ))}
    </div>
  )
}

function ProgressSummary({ profile, summary }) {
  const streak = summary?.streak
  return (
    <section className="profile__card">
      <h2 className="profile__card-title">Ma progression</h2>
      <div className="profile__stats">
        <Stat value={profile?.total_points ?? 0} label="Points" />
        <Stat value={profile?.level ?? 1} label="Niveau" />
        <Stat value={streak?.current_streak ?? 0} label="Jours d’affilée" />
        <Stat value={summary?.badges_earned ?? 0} label="Trophées" />
      </div>
    </section>
  )
}

function Stat({ value, label }) {
  return (
    <div className="profile__stat">
      <span className="profile__stat-value">{value}</span>
      <span className="profile__stat-label">{label}</span>
    </div>
  )
}

function PasswordCard() {
  const dispatch = useDispatch()
  const [fields, setFields] = useState({ old: '', next: '', confirm: '' })
  const [state, setState] = useState({ busy: false, error: null, notice: null })

  const set = (field) => (event) =>
    setFields((current) => ({ ...current, [field]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()

    if (fields.next !== fields.confirm) {
      setState({ busy: false, error: 'Les deux mots de passe ne correspondent pas.', notice: null })
      return
    }

    setState({ busy: true, error: null, notice: null })
    const result = await dispatch(changePassword({
      oldPassword: fields.old,
      newPassword: fields.next,
      newPasswordConfirm: fields.confirm,
    }))

    if (changePassword.rejected.match(result)) {
      setState({ busy: false, error: firstError(result.payload) || 'Changement impossible.', notice: null })
    } else {
      setFields({ old: '', next: '', confirm: '' })
      setState({ busy: false, error: null, notice: 'Mot de passe modifié.' })
    }
  }

  return (
    <form className="profile__card" onSubmit={submit}>
      <h2 className="profile__card-title">Mot de passe</h2>
      <p className="profile__hint">
        L’ancien mot de passe est demandé : sans lui, un poste laissé ouvert
        suffirait à s’approprier le compte.
      </p>

      {state.error && <div className="auth-alert auth-alert--error" role="alert">{state.error}</div>}
      {state.notice && <div className="auth-alert auth-alert--success" role="status">{state.notice}</div>}

      <div className="profile__grid">
        <Field label="Mot de passe actuel" id="old_password">
          <PasswordInput id="old_password"
            value={fields.old} onChange={set('old')} autoComplete="current-password" />
        </Field>

        <Field label="Nouveau mot de passe" id="new_password">
          <PasswordInput id="new_password"
            value={fields.next} onChange={set('next')} autoComplete="new-password" />
        </Field>

        <Field label="Confirmer" id="confirm_password">
          <PasswordInput id="confirm_password"
            value={fields.confirm} onChange={set('confirm')} autoComplete="new-password" />
        </Field>
      </div>

      <button type="submit" className="profile__submit" disabled={state.busy}>
        {state.busy ? 'Modification…' : 'Changer le mot de passe'}
      </button>
    </form>
  )
}

/**
 * Section RGPD : exporter ses données (portabilité) et supprimer son compte
 * (droit à l'effacement en self-service).
 *
 * La suppression est irréversible : on exige donc le mot de passe *et* une
 * confirmation explicite avant d'appeler l'API, sur le même principe que
 * l'anonymisation côté administration.
 */
function DataCard() {
  const dispatch = useDispatch()
  const [exporting, setExporting] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [password, setPassword] = useState('')
  const [state, setState] = useState({ busy: false, error: null, notice: null })

  const exportData = async () => {
    setExporting(true)
    setState((s) => ({ ...s, error: null }))
    try {
      const data = await authApi.exportMyData()
      // Téléchargement côté client : on transforme le JSON en fichier local.
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'mes-donnees-codeacademy.json'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch {
      setState((s) => ({ ...s, error: 'Export impossible pour le moment.' }))
    } finally {
      setExporting(false)
    }
  }

  const deleteAccount = async (event) => {
    event.preventDefault()
    setState({ busy: true, error: null, notice: null })
    try {
      await authApi.deleteMyAccount(password)
      // Compte anonymisé et sessions révoquées côté serveur : on purge la
      // session locale et on renvoie vers la connexion. `window.location`
      // (comme l'intercepteur axios) plutôt que `useNavigate` : un rechargement
      // complet garantit qu'aucun état résiduel du compte supprimé ne subsiste.
      await dispatch(logoutUser())
      window.location.href = '/login'
    } catch (error) {
      const payload = error.response?.data
      setState({
        busy: false,
        error: firstError(payload) || 'Suppression impossible.',
        notice: null,
      })
    }
  }

  return (
    <section className="profile__card">
      <h2 className="profile__card-title">Mes données</h2>
      <p className="profile__hint">
        Conformément au RGPD, vous pouvez emporter vos données ou supprimer
        votre compte à tout moment.
      </p>

      {state.error && (
        <div className="auth-alert auth-alert--error" role="alert">{state.error}</div>
      )}

      <div className="profile__data-actions">
        <button
          type="button"
          className="profile__submit profile__submit--ghost"
          onClick={exportData}
          disabled={exporting}
        >
          {exporting ? 'Préparation…' : 'Exporter mes données (JSON)'}
        </button>
      </div>

      <div className="profile__danger">
        <h3 className="profile__danger-title">Supprimer mon compte</h3>
        <p className="profile__hint">
          Cette action est <strong>irréversible</strong>. Vos données
          personnelles (identité, profil) seront effacées. Votre progression est
          conservée de façon anonyme pour ne pas fausser les statistiques des
          classes.
        </p>

        {!confirming ? (
          <button
            type="button"
            className="profile__submit profile__submit--danger"
            onClick={() => setConfirming(true)}
          >
            Supprimer mon compte
          </button>
        ) : (
          <form onSubmit={deleteAccount} className="profile__danger-form">
            <Field label="Confirmez avec votre mot de passe" id="delete_password">
              <PasswordInput
                id="delete_password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </Field>
            <div className="profile__danger-buttons">
              <button
                type="button"
                className="profile__submit profile__submit--ghost"
                onClick={() => { setConfirming(false); setPassword('') }}
              >
                Annuler
              </button>
              <button
                type="submit"
                className="profile__submit profile__submit--danger"
                disabled={state.busy || !password}
              >
                {state.busy ? 'Suppression…' : 'Supprimer définitivement'}
              </button>
            </div>
          </form>
        )}
      </div>
    </section>
  )
}

/**
 * Extrait un message lisible d'une réponse d'erreur DRF.
 *
 * DRF renvoie `{champ: ["message"]}`, parfois imbriqué d'un niveau pour le
 * profil. Afficher l'objet brut donnerait « [object Object] » à l'utilisateur.
 */
function firstError(payload) {
  if (!payload) return null
  if (typeof payload === 'string') return payload

  for (const value of Object.values(payload)) {
    if (typeof value === 'string') return value
    if (Array.isArray(value) && value.length) return String(value[0])
    if (value && typeof value === 'object') {
      const nested = firstError(value)
      if (nested) return nested
    }
  }
  return null
}
