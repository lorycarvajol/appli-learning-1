import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authApi } from '@/services/api/authApi'
import BrandLogo from '@/components/ui/BrandLogo';

/**
 * Demande d'un lien de réinitialisation.
 *
 * Le serveur répond la même chose que le compte existe ou non — l'écran de
 * confirmation ne doit donc jamais laisser deviner si l'email est connu.
 */
export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const data = await authApi.requestPasswordReset(email)
      setSent(data.message)
    } catch (err) {
      const detail = err.response?.data
      setError(
        detail?.email?.[0] ||
          detail?.detail ||
          "Impossible d'envoyer la demande pour le moment. Réessayez plus tard."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <BrandLogo to="/login" />

        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-header__title">Mot de passe oublié</h1>
            <p className="auth-header__subtitle">
              Indiquez votre adresse email, nous vous enverrons un lien pour en
              choisir un nouveau.
            </p>
          </div>

          {sent ? (
            <>
              <div className="auth-alert auth-alert--success" role="status">
                {sent}
              </div>
              <p className="auth-form__hint">
                Le lien expire dans une heure et ne fonctionne qu’une fois.
              </p>
            </>
          ) : (
            <>
              {error && (
                <div className="auth-alert auth-alert--error" role="alert">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="auth-form" noValidate>
                <div className="auth-form__group">
                  <label htmlFor="forgot-email" className="auth-form__label">
                    Email
                  </label>
                  <input
                    id="forgot-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="auth-form__input"
                    placeholder="votre@email.com"
                    required
                    autoFocus
                    autoComplete="email"
                  />
                </div>

                <button type="submit" disabled={loading} className="auth-form__submit">
                  {loading ? 'Envoi en cours...' : 'Envoyer le lien'}
                </button>
              </form>
            </>
          )}

          <div className="auth-footer">
            <p className="auth-footer__text">Vous vous en souvenez ?</p>
            <Link to="/login" className="auth-footer__link">
              Retour à la connexion
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
