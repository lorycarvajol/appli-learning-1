import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { login, clearError } from './authSlice'
import PasswordInput from '@/components/ui/PasswordInput'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { loading, error } = useSelector((state) => state.auth)

  // Destination après connexion. Sert au parcours d'invitation : quelqu'un qui
  // a déjà un compte doit revenir sur le lien pour être rattaché.
  // On n'accepte qu'un chemin interne : une URL absolue permettrait de
  // rediriger vers un site tiers depuis un lien de connexion piégé.
  const rawNext = searchParams.get('next')
  const nextPath =
    rawNext && rawNext.startsWith('/') && !rawNext.startsWith('//')
      ? rawNext
      : '/dashboard'

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(clearError())

    const result = await dispatch(login({ email, password }))

    if (login.fulfilled.match(result)) {
      navigate(nextPath)
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
            <h1 className="auth-header__title">Connexion</h1>
            <p className="auth-header__subtitle">
              Connectez-vous pour accéder à la plateforme
            </p>
          </div>

          {error && (
            <div className="auth-alert auth-alert--error" role="alert">
              {error.detail || error.message || 'Erreur de connexion'}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            <div className="auth-form__group">
              <label htmlFor="login-email" className="auth-form__label">Email</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="auth-form__input"
                placeholder="votre@email.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="auth-form__group">
              <label htmlFor="login-password" className="auth-form__label">Mot de passe</label>
              <PasswordInput
                id="login-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
              <Link to="/forgot-password" className="auth-form__forgot">
                Mot de passe oublié ?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="auth-form__submit"
            >
              {loading ? 'Connexion en cours...' : 'Se connecter'}
            </button>
          </form>

          <div className="auth-footer">
            <p className="auth-footer__text">Pas encore de compte ?</p>
            <Link to="/register" className="auth-footer__link">
              S’inscrire
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
