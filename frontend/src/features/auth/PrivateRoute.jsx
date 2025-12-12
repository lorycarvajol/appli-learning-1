import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useSelector((state) => state.auth)
  const hasToken = localStorage.getItem('accessToken')

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

  if (!isAuthenticated && !hasToken) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default PrivateRoute
