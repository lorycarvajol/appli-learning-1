import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { register, clearError } from './authSlice'
import PasswordInput from '@/components/ui/PasswordInput'

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  })
  // Consentement RGPD, distinct du reste du formulaire : c'est un acte
  // d'acceptation, pas une donnée de compte. Envoyé au serveur, qui refuse
  // l'inscription et horodate l'acceptation.
  const [acceptTerms, setAcceptTerms] = useState(false)
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error } = useSelector((state) => state.auth)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(clearError())

    const result = await dispatch(register({ ...formData, accept_terms: acceptTerms }))

    if (register.fulfilled.match(result)) {
      navigate('/dashboard')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <Link to="/dashboard" className="auth-logo">
          <span className="auth-logo__mark" aria-hidden="true">&lt;/&gt;</span>
          <span>CodeAcademy</span>
        </Link>

        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-header__title">Inscription</h1>
            <p className="auth-header__subtitle">
              Créez votre compte pour accéder à la plateforme
            </p>
          </div>

          {error && (
            <div className="auth-alert auth-alert--error" role="alert">
              {typeof error === 'object' ? (
                <ul>
                  {Object.entries(error).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {Array.isArray(value) ? value[0] : value}
                    </li>
                  ))}
                </ul>
              ) : (
                error
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            <div className="auth-form__group">
              <label htmlFor="register-email" className="auth-form__label">Email</label>
              <input
                id="register-email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="votre@email.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="auth-form__row">
              <div className="auth-form__group">
                <label htmlFor="register-first-name" className="auth-form__label">Prénom</label>
                <input
                  id="register-first-name"
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="auth-form__input"
                  placeholder="Jean"
                  required
                  autoComplete="given-name"
                />
              </div>

              <div className="auth-form__group">
                <label htmlFor="register-last-name" className="auth-form__label">Nom</label>
                <input
                  id="register-last-name"
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="auth-form__input"
                  placeholder="Dupont"
                  required
                  autoComplete="family-name"
                />
              </div>
            </div>

            <div className="auth-form__group">
              <label htmlFor="register-password" className="auth-form__label">Mot de passe</label>
              <PasswordInput
                id="register-password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                minLength={8}
                autoComplete="new-password"
                aria-describedby="register-password-hint"
              />
              <small id="register-password-hint" className="auth-form__hint">Minimum 8 caractères</small>
            </div>

            <div className="auth-form__group">
              <label htmlFor="register-password-confirm" className="auth-form__label">Confirmer le mot de passe</label>
              <PasswordInput
                id="register-password-confirm"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
            </div>

            <div className="auth-form__consent">
              <input
                id="register-accept-terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                required
              />
              <label htmlFor="register-accept-terms">
                J’accepte la{' '}
                <Link to="/confidentialite" target="_blank" rel="noreferrer">
                  politique de confidentialité
                </Link>{' '}
                et les{' '}
                <Link to="/cgu" target="_blank" rel="noreferrer">
                  conditions d’utilisation
                </Link>
                .
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !acceptTerms}
              className="auth-form__submit"
            >
              {loading ? 'Inscription en cours...' : 'S\'inscrire'}
            </button>
          </form>

          <div className="auth-footer">
            <p className="auth-footer__text">Déjà un compte ?</p>
            <Link to="/login" className="auth-footer__link">
              Se connecter
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
