import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link, useNavigate, useParams } from 'react-router-dom'
import cohortsApi from '@/services/api/cohortsApi'
import { fetchCurrentUser } from '@/features/auth/authSlice'
import PasswordInput from '@/components/ui/PasswordInput'

/**
 * Page d'arrivée sur un lien d'invitation.
 *
 * Trois situations à couvrir — c'est là que ces parcours déçoivent d'habitude :
 *   1. visiteur inconnu   → formulaire de création de compte
 *   2. déjà connecté      → simple confirmation
 *   3. compte existant    → renvoi vers la connexion, rattachement au retour
 *
 * Le lien est résolu avant tout formulaire, pour ne pas faire remplir un
 * formulaire qui échouera.
 */
export default function JoinCohort() {
  const { token } = useParams()
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { user } = useSelector((state) => state.auth)
  const hasSession = Boolean(localStorage.getItem('accessToken'))

  const [checking, setChecking] = useState(true)
  const [invite, setInvite] = useState(null)
  const [form, setForm] = useState({
    email: '', password: '', password_confirm: '', first_name: '', last_name: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [joined, setJoined] = useState(false)

  useEffect(() => {
    let cancelled = false
    cohortsApi
      .getInvite(token)
      .then((data) => {
        if (!cancelled) setInvite(data.valid ? data : null)
      })
      .catch(() => {
        if (!cancelled) setInvite(null)
      })
      .finally(() => {
        if (!cancelled) setChecking(false)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))

  const readError = (err) => {
    const detail = err.response?.data
    if (!detail) return "Une erreur est survenue."
    const first = detail.email || detail.password || detail.token || detail.detail
    return Array.isArray(first) ? first[0] : first || "Une erreur est survenue."
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const data = await cohortsApi.registerWithInvite(token, form)
      localStorage.setItem('accessToken', data.tokens.access)
      localStorage.setItem('refreshToken', data.tokens.refresh)
      await dispatch(fetchCurrentUser())
      navigate('/dashboard')
    } catch (err) {
      setError(readError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleAttach = async () => {
    setLoading(true)
    setError(null)
    try {
      await cohortsApi.attachToInvite(token)
      await dispatch(fetchCurrentUser())
      setJoined(true)
      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err) {
      setError(readError(err))
    } finally {
      setLoading(false)
    }
  }

  const renderBody = () => {
    if (checking) {
      return <p className="auth-form__hint">Vérification de l’invitation...</p>
    }

    if (!invite) {
      return (
        <>
          <div className="auth-alert auth-alert--error" role="alert">
            Cette invitation est invalide, expirée ou révoquée.
          </div>
          <p className="auth-form__hint">
            Demandez un nouveau lien à votre formateur.
          </p>
          <Link to="/login" className="auth-form__submit">
            Retour à la connexion
          </Link>
        </>
      )
    }

    if (joined) {
      return (
        <div className="auth-alert auth-alert--success" role="status">
          Vous avez rejoint {invite.cohort_name}. Redirection...
        </div>
      )
    }

    // Cas 2 : déjà connecté — une confirmation suffit.
    if (hasSession && user) {
      return (
        <>
          {error && (
            <div className="auth-alert auth-alert--error" role="alert">{error}</div>
          )}
          <p className="auth-form__hint">
            Vous êtes connecté en tant que <strong>{user.email}</strong>.
          </p>
          <button
            type="button"
            className="auth-form__submit"
            onClick={handleAttach}
            disabled={loading}
          >
            {loading ? 'Rattachement...' : `Rejoindre ${invite.cohort_name}`}
          </button>
        </>
      )
    }

    // Cas 1 : visiteur inconnu — création de compte.
    return (
      <>
        {error && (
          <div className="auth-alert auth-alert--error" role="alert">{error}</div>
        )}

        <form onSubmit={handleRegister} className="auth-form" noValidate>
          <div className="auth-form__row">
            <div className="auth-form__group">
              <label htmlFor="join-first-name" className="auth-form__label">Prénom</label>
              <input
                id="join-first-name" name="first_name" type="text"
                value={form.first_name} onChange={handleChange}
                className="auth-form__input" autoComplete="given-name"
              />
            </div>
            <div className="auth-form__group">
              <label htmlFor="join-last-name" className="auth-form__label">Nom</label>
              <input
                id="join-last-name" name="last_name" type="text"
                value={form.last_name} onChange={handleChange}
                className="auth-form__input" autoComplete="family-name"
              />
            </div>
          </div>

          <div className="auth-form__group">
            <label htmlFor="join-email" className="auth-form__label">Email</label>
            <input
              id="join-email" name="email" type="email"
              value={form.email} onChange={handleChange}
              className="auth-form__input" placeholder="votre@email.com"
              required autoComplete="email"
            />
          </div>

          <div className="auth-form__group">
            <label htmlFor="join-password" className="auth-form__label">Mot de passe</label>
            <PasswordInput
              id="join-password" name="password"
              value={form.password} onChange={handleChange}
              placeholder="••••••••" required minLength={8}
              autoComplete="new-password"
            />
          </div>

          <div className="auth-form__group">
            <label htmlFor="join-password-confirm" className="auth-form__label">
              Confirmer le mot de passe
            </label>
            <PasswordInput
              id="join-password-confirm" name="password_confirm"
              value={form.password_confirm} onChange={handleChange}
              placeholder="••••••••" required autoComplete="new-password"
            />
          </div>

          <button type="submit" disabled={loading} className="auth-form__submit">
            {loading ? 'Création du compte...' : 'Rejoindre la classe'}
          </button>
        </form>

        <div className="auth-footer">
          {/* Cas 3 : le lien est conservé pour rattacher au retour de connexion */}
          <p className="auth-footer__text">Vous avez déjà un compte ?</p>
          <Link to={`/login?next=/rejoindre/${token}`} className="auth-footer__link">
            Se connecter
          </Link>
        </div>
      </>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <Link to="/login" className="auth-logo">
          <span className="auth-logo__mark" aria-hidden="true">&lt;/&gt;</span>
          <span>CodeAcademy</span>
        </Link>

        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-header__title">
              {invite?.cohort_name ? `Rejoindre ${invite.cohort_name}` : 'Invitation'}
            </h1>
            {invite?.trainer_name && (
              <p className="auth-header__subtitle">
                Classe animée par {invite.trainer_name}
              </p>
            )}
          </div>

          {renderBody()}
        </div>
      </div>
    </div>
  )
}
