import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { register, clearError } from './authSlice'

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  })
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

    const result = await dispatch(register(formData))

    if (register.fulfilled.match(result)) {
      navigate('/dashboard')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h2 className="auth-header__title">Inscription</h2>
            <p className="auth-header__subtitle">
              Créez votre compte pour accéder à la plateforme
            </p>
          </div>

          {error && (
            <div className="auth-alert auth-alert--error">
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

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-form__group">
              <label className="auth-form__label">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="votre@email.com"
                required
              />
            </div>

            <div className="auth-form__group">
              <label className="auth-form__label">Prénom</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="Jean"
                required
              />
            </div>

            <div className="auth-form__group">
              <label className="auth-form__label">Nom</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="Dupont"
                required
              />
            </div>

            <div className="auth-form__group">
              <label className="auth-form__label">Mot de passe</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="••••••••"
                required
                minLength={8}
              />
              <small className="auth-form__error">Minimum 8 caractères</small>
            </div>

            <div className="auth-form__group">
              <label className="auth-form__label">Confirmer le mot de passe</label>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                className="auth-form__input"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
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
