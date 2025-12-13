import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { login, clearError } from './authSlice'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error } = useSelector((state) => state.auth)

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(clearError())

    const result = await dispatch(login({ email, password }))

    if (login.fulfilled.match(result)) {
      navigate('/dashboard')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h2 className="auth-header__title">Connexion</h2>
            <p className="auth-header__subtitle">
              Connectez-vous pour accéder à la plateforme
            </p>
          </div>

          {error && (
            <div className="auth-alert auth-alert--error">
              {error.detail || error.message || 'Erreur de connexion'}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-form__group">
              <label className="auth-form__label">Email</label>
              <input
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
              <label className="auth-form__label">Mot de passe</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="auth-form__input"
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
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
              S'inscrire
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
