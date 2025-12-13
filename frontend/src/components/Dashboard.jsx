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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Learning Platform
          </h1>
          <button
            onClick={handleLogout}
            className="btn btn-secondary"
          >
            Déconnexion
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">
            Bienvenue {user?.first_name || 'Utilisateur'} !
          </h2>

          <div className="space-y-4">
            <div>
              <p className="text-gray-600">
                <strong>Email:</strong> {user?.email}
              </p>
              <p className="text-gray-600">
                <strong>Nom complet:</strong> {user?.first_name} {user?.last_name}
              </p>
              <p className="text-gray-600">
                <strong>Rôle:</strong> <span className="capitalize">{user?.role?.toLowerCase()}</span>
              </p>
            </div>

            {user?.profile && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">Profil</h3>
                <p className="text-gray-600">
                  <strong>Points:</strong> {user.profile.total_points}
                </p>
                <p className="text-gray-600">
                  <strong>Niveau:</strong> {user.profile.level}
                </p>
              </div>
            )}

            <div className="border-t pt-4">
              <p className="text-green-600 font-medium">
                ✅ L'authentification fonctionne correctement !
              </p>
              <p className="text-gray-600 mt-2">
                Vous êtes connecté avec succès.
              </p>

              <div className="mt-4 flex flex-wrap gap-3">
                <Link
                  to="/chapters"
                  className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Accéder aux chapitres
                </Link>

                {user?.role && (user.role === 'TRAINER' || user.role === 'ADMIN') && (
                  <Link
                    to="/trainer"
                    className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
                  >
                    Dashboard Trainer
                  </Link>
                )}
              </div>

              <p className="text-gray-600 mt-4">Les prochaines fonctionnalités incluent :</p>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Système de progression</li>
                <li>Éditeur de code intégré</li>
                <li>Gamification (badges, points)</li>
                <li>WebSocket pour le temps réel</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
