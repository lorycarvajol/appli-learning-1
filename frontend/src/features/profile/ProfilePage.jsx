import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { changePassword, updateProfile, logoutUser } from '@/features/auth/authSlice'
import { fetchGamificationSummary } from '@/features/gamification/gamificationSlice'
import { authApi } from '@/services/api/authApi'
import Avatar from '@/components/ui/Avatar'
import PasswordInput from '@/components/ui/PasswordInput'
import { ROLE_LABELS } from '@/constants/roles'
import {
  FAMILLES,
  PALETTES,
  PALETTE_LABELS,
  PALETTE_PAR_DEFAUT,
  initialsPalette,
  paletteColors,
  parseAvatarKey,
} from './avatars'
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
  const [pickerOuvert, setPickerOuvert] = useState(false)
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
        // Absent de la réponse (vieux client, compte tout juste créé) vaut
        // « visible » : c'est le défaut du modèle, et l'inverse retirerait
        // silencieusement du classement quelqu'un qui n'a rien demandé.
        show_in_leaderboard: user.profile?.show_in_leaderboard !== false,
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
        show_in_leaderboard: form.show_in_leaderboard,
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
      <ProfileHero user={user} preview={preview} />

      <div className="profile__container">
        {error && <div className="auth-alert auth-alert--error" role="alert">{error}</div>}
        {notice && <div className="auth-alert auth-alert--success" role="status">{notice}</div>}

        <ProgressSummary profile={user.profile} summary={summary} />

        <form className="profile__card" onSubmit={submit}>
          <h2 className="profile__card-title">Mon avatar</h2>
          <p className="profile__hint">
            Sans choix, vos initiales servent d’avatar.
          </p>

          {/*
            Le catalogue est déplié à la demande. Quarante-deux visages ouverts
            d'emblée occupaient tout l'écran et repoussaient le reste du profil
            — nom, mot de passe, classement — hors de vue, alors qu'on ne
            change d'avatar qu'une fois.
          */}
          <div className="profile__avatar-actuel">
            <Avatar user={preview} size={64} />
            <button
              type="button"
              className="profile__submit profile__submit--ghost profile__avatar-bascule"
              aria-expanded={pickerOuvert}
              aria-controls="choix-avatar"
              onClick={() => setPickerOuvert((ouvert) => !ouvert)}
            >
              {pickerOuvert ? 'Fermer les avatars' : 'Changer d’avatar'}
            </button>
          </div>

          {pickerOuvert && (
            <AvatarPicker
              id="choix-avatar"
              value={form.avatar_key}
              user={preview}
              onChange={(key) => setForm((c) => ({ ...c, avatar_key: key }))}
            />
          )}

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

          {/*
            Se comparer motive les uns et décourage les autres : le classement
            ne peut pas être imposé. Se retirer n'a aucun effet sur les points,
            les trophées ni la progression — seule la ligne publique disparaît.
          */}
          <div className="profile__check">
            <input
              id="show_in_leaderboard"
              type="checkbox"
              checked={form.show_in_leaderboard}
              onChange={(event) =>
                setForm((c) => ({ ...c, show_in_leaderboard: event.target.checked }))
              }
            />
            <label className="profile__check-label" htmlFor="show_in_leaderboard">
              Apparaître dans le classement
              <span className="profile__field-hint">
                Sous la forme « Prénom N. ». Décoché, vous n’y figurez plus et
                n’y voyez plus votre rang ; vos points et vos trophées sont
                conservés.
              </span>
            </label>
          </div>

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

/**
 * En-tête du profil : qui est cette personne sur la plateforme.
 *
 * Volontairement **sans chiffres** : points, niveau, série et trophées sont
 * dans la carte « Ma progression », juste en dessous. Les répéter en gros dans
 * le bandeau aurait donné l'en-tête de tableau de bord qu'on voit partout, et
 * relégué la seule chose que l'apprenant écrit lui-même — sa bio — au rang de
 * sous-titre. Ici la bio est le texte le plus grand après le nom : c'est le
 * seul endroit de l'application où un apprenant parle en son nom.
 *
 * L'accent coloré du bandeau est repris de **l'avatar choisi** : la palette
 * sélectionnée dans le catalogue teinte l'anneau et la lueur. Sans choix, on
 * retombe sur la couleur dérivée du nom — celle de l'avatar à initiales — donc
 * il y a toujours un accent, et il désigne toujours la même personne.
 */
function ProfileHero({ user, preview }) {
  const parsed = parseAvatarKey(user.profile?.avatar_key)
  const accent = paletteColors(
    parsed ? parsed.palette : initialsPalette(user.email || '')
  )

  const nom = `${user.first_name || ''} ${user.last_name || ''}`.trim()
  const pseudo = user.profile?.github_username?.trim()
  const bio = user.profile?.bio?.trim()
  const classe = user.profile?.cohort_name

  return (
    <header
      className="profile__hero"
      style={{ '--hero-accent': accent.from, '--hero-accent-2': accent.to }}
    >
      <div className="profile__hero-inner">
        <Avatar user={preview} size={96} className="profile__hero-avatar" />

        <div className="profile__identity">
          {/* Sur sa propre page, l'email en repli n'expose rien à personne. */}
          <h1 className="profile__title">{nom || user.email}</h1>

          <div className="profile__meta">
            {pseudo && (
              // Le seul identifiant « pseudonyme » que le profil enregistre est
              // le compte GitHub. En chasse fixe, comme on l'écrirait dans
              // l'éditeur — c'est le seul écart typographique du bandeau.
              <a
                className="profile__handle"
                href={`https://github.com/${pseudo}`}
                target="_blank"
                rel="noreferrer noopener"
                aria-label={`Profil GitHub de ${pseudo}`}
              >
                @{pseudo}
              </a>
            )}
            <span className="profile__chip">{ROLE_LABELS[user.role] || user.role}</span>
            {classe && <span className="profile__chip">{classe}</span>}
          </div>

          {bio
            ? <p className="profile__bio">{bio}</p>
            : (
              /* Un bandeau vide n'invite à rien : on dit quoi faire. */
              <p className="profile__bio profile__bio--vide">
                Ajoutez une phrase pour vous présenter.
              </p>
            )}
        </div>
      </div>
    </header>
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

/**
 * Choix de l'avatar, en deux temps : le visage, puis la couleur du fond.
 *
 * Le catalogue compte sept familles de six visages, déclinés en six palettes —
 * **252 combinaisons**. Les présenter à plat, comme le faisait la version à
 * trente-six, donnerait une planche illisible où chaque visage reviendrait six
 * fois. En séparant les deux choix, on retombe à quarante-huit boutons et la
 * palette redevient ce qu'elle est : un réglage, pas une variante.
 *
 * Les vignettes de visage portent la **palette en cours**, pour que l'aperçu
 * corresponde à ce qui sera enregistré.
 */
function AvatarPicker({ id, value, user, onChange }) {
  const parsed = parseAvatarKey(value)
  const paletteCourante = parsed ? parsed.palette : PALETTE_PAR_DEFAUT

  return (
    <div className="profile__avatar-picker" id={id}>
      <div
        className="profile__avatars"
        role="radiogroup"
        aria-label="Avatar par défaut"
      >
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
      </div>

      {FAMILLES.map((famille) => (
        <section className="profile__avatar-family" key={famille.id}>
          <h3 className="profile__avatar-family-title">{famille.titre}</h3>
          {/*
            L'attribution est portée là où l'œuvre est utilisée : quatre des
            sept familles sont en CC BY 4.0, qui l'impose. Les mentions légales
            reprennent la liste complète, avec les liens.
          */}
          <p className="profile__avatar-credit">
            {famille.credit.auteur} · {famille.credit.licence}
          </p>

          <div
            className="profile__avatars"
            role="radiogroup"
            aria-label={`Visages ${famille.titre}`}
          >
            {famille.visages.map((visage) => {
              const key = `${visage}-${paletteCourante}`
              return (
                <button
                  key={visage}
                  type="button"
                  role="radio"
                  aria-checked={value === key}
                  aria-label={`Avatar ${visage}`}
                  className={`profile__avatar-choice ${value === key ? 'profile__avatar-choice--active' : ''}`}
                  onClick={() => onChange(key)}
                >
                  <Avatar user={{ profile: { avatar_key: key } }} size={48} />
                </button>
              )
            })}
          </div>
        </section>
      ))}

      {/*
        Sans visage choisi, la couleur du fond vient du nom (repli à initiales,
        déterministe) : il n'y a rien à régler, et proposer des palettes sans
        effet ferait croire à une panne.
      */}
      {parsed && (
        <section className="profile__avatar-family">
          <h3 className="profile__avatar-family-title">Couleur du fond</h3>
          <div
            className="profile__palettes"
            role="radiogroup"
            aria-label="Couleur du fond de l’avatar"
          >
            {PALETTES.map((palette) => {
              const key = `${parsed.visage}-${palette}`
              return (
                <button
                  key={palette}
                  type="button"
                  role="radio"
                  aria-checked={value === key}
                  aria-label={`Fond ${PALETTE_LABELS[palette] || palette}`}
                  className={`profile__avatar-choice ${value === key ? 'profile__avatar-choice--active' : ''}`}
                  onClick={() => onChange(key)}
                >
                  <Avatar user={{ profile: { avatar_key: key } }} size={48} />
                </button>
              )
            })}
          </div>
        </section>
      )}
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
