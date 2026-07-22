import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { authApi } from '@/services/api/authApi'
import PasswordInput from '@/components/ui/PasswordInput'

/**
 * Choix du nouveau mot de passe depuis le lien reçu par email.
 *
 * Le lien est validé **avant** d'afficher le formulaire : faire saisir deux
 * fois un mot de passe pour annoncer ensuite que le lien avait expiré est la
 * façon la plus sûre de perdre l'utilisateur.
 */
export default function ResetPassword() {
  const { uid, token } = useParams()
  const navigate = useNavigate()

  const [checking, setChecking] = useState(true)
  const [linkValid, setLinkValid] = useState(false)
  const [accountEmail, setAccountEmail] = useState('')

  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)

  useEffect(() => {
    let cancelled = false

    authApi
      .validateResetLink(uid, token)
      .then((data) => {
        if (cancelled) return
        setLinkValid(data.valid)
        setAccountEmail(data.email || '')
      })
      .catch(() => {
        if (!cancelled) setLinkValid(false)
      })
      .finally(() => {
        if (!cancelled) setChecking(false)
      })

    return () => {
      cancelled = true
    }
  }, [uid, token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await authApi.confirmPasswordReset(uid, token, password, passwordConfirm)
      setDone(true)
      // Toutes les sessions ont été révoquées côté serveur : on renvoie vers
      // la connexion plutôt que de tenter de connecter automatiquement.
      setTimeout(() => navigate('/login'), 2500)
    } catch (err) {
      const detail = err.response?.data
      setError(
        detail?.new_password?.[0] ||
          detail?.token?.[0] ||
          detail?.detail ||
          'Impossible de réinitialiser le mot de passe.'
      )
    } finally {
      setLoading(false)
    }
  }

  const renderBody = () => {
    if (checking) {
      return <p className="auth-form__hint">Vérification du lien...</p>
    }

    if (!linkValid) {
      return (
        <>
          <div className="auth-alert auth-alert--error" role="alert">
            Ce lien est invalide ou a expiré.
          </div>
          <p className="auth-form__hint">
            Les liens ne sont valables qu’une heure, et deviennent inutilisables
            dès que vous vous reconnectez ou qu’un nouveau lien est demandé.
          </p>
          <Link to="/forgot-password" className="auth-form__submit">
            Demander un nouveau lien
          </Link>
        </>
      )
    }

    if (done) {
      return (
        <div className="auth-alert auth-alert--success" role="status">
          Mot de passe modifié. Redirection vers la connexion...
        </div>
      )
    }

    return (
      <>
        {accountEmail && (
          <p className="auth-form__hint">
            Nouveau mot de passe pour <strong>{accountEmail}</strong>
          </p>
        )}

        {error && (
          <div className="auth-alert auth-alert--error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="auth-form__group">
            <label htmlFor="reset-password" className="auth-form__label">
              Nouveau mot de passe
            </label>
            <PasswordInput
              id="reset-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoFocus
              autoComplete="new-password"
            />
            <p className="auth-form__hint">
              Au moins 8 caractères, différent de votre nom et de votre email.
            </p>
          </div>

          <div className="auth-form__group">
            <label htmlFor="reset-password-confirm" className="auth-form__label">
              Confirmer le mot de passe
            </label>
            <PasswordInput
              id="reset-password-confirm"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="new-password"
            />
          </div>

          <button type="submit" disabled={loading} className="auth-form__submit">
            {loading ? 'Enregistrement...' : 'Définir le mot de passe'}
          </button>
        </form>
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
            <h1 className="auth-header__title">Nouveau mot de passe</h1>
          </div>

          {renderBody()}

          <div className="auth-footer">
            <p className="auth-footer__text">Vous avez retrouvé vos accès ?</p>
            <Link to="/login" className="auth-footer__link">
              Se connecter
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
