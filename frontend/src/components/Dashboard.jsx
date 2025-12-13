import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { fetchCurrentUser, logoutUser } from '../features/auth/authSlice'

function Dashboard() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user, loading } = useSelector((state) => state.auth)
  const [hasFetched, setHasFetched] = useState(false)

  useEffect(() => {
    // Only fetch once if user data is not already present
    if (!user && !hasFetched) {
      setHasFetched(true)
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, user, hasFetched])

  const handleLogout = async () => {
    await dispatch(logoutUser())
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
          <div className="loading-spinner"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1 className="dashboard-header__greeting">
            Bienvenue {user?.first_name || 'Utilisateur'} !
          </h1>
          <p className="dashboard-header__subtitle">
            {user?.role === 'TRAINER' && 'Espace Formateur'}
            {user?.role === 'ADMIN' && 'Espace Administrateur'}
            {user?.role === 'LEARNER' && 'Espace Apprenant'}
          </p>
        </div>

        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-card__value">{user?.profile?.total_points || 0}</div>
            <div className="stat-card__label">Points</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__value">{user?.profile?.level || 1}</div>
            <div className="stat-card__label">Niveau</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__value">0</div>
            <div className="stat-card__label">Leçons complétées</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__value">0</div>
            <div className="stat-card__label">Badges</div>
          </div>
        </div>

        <div className="dashboard-actions">
          <h2 className="dashboard-actions__title">Actions rapides</h2>
          <div className="dashboard-actions__buttons">
            <Link to="/chapters" className="dashboard-actions__button">
              📚 Accéder aux chapitres
            </Link>

            {user?.role && (user.role === 'TRAINER' || user.role === 'ADMIN') && (
              <Link to="/trainer" className="dashboard-actions__button">
                👨‍🏫 Dashboard Trainer
              </Link>
            )}

            <button onClick={handleLogout} className="dashboard-actions__button">
              🚪 Déconnexion
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
