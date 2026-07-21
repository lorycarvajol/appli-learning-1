import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

/**
 * Protège une route par authentification et, optionnellement, par rôle.
 *
 *   <PrivateRoute>...</PrivateRoute>                     → être connecté suffit
 *   <PrivateRoute roles={STAFF_ROLES}>...</PrivateRoute> → rôle requis
 *
 * Cette garde est un **confort d'affichage, pas une sécurité** : elle évite
 * qu'un apprenant qui tape /trainer tombe sur une page vide criblée d'erreurs
 * 403. La protection réelle des données reste côté API (`IsTrainerOrAdmin`).
 *
 * Le rôle ne peut être évalué qu'une fois le profil chargé. Trancher trop tôt
 * renverrait un formateur légitime vers le tableau de bord à chaque
 * rafraîchissement de page — d'où l'attente explicite sur `initialized`.
 */
function PrivateRoute({ children, roles }) {
  const { user, isAuthenticated, initialized, loading } = useSelector(
    (state) => state.auth
  )
  const hasToken = localStorage.getItem('accessToken')

  // Aucun jeton : inutile d'attendre quoi que ce soit.
  if (!hasToken && !isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Jeton présent mais identité pas encore résolue.
  if (loading || (hasToken && !initialized)) {
    return (
      <div className="route-guard">
        <div className="loading-spinner" aria-hidden="true"></div>
        <p className="route-guard__text" role="status">
          Chargement...
        </p>
      </div>
    )
  }

  // Identité résolue mais aucun utilisateur : jeton périmé ou révoqué.
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // Connecté, mais pas avec le bon rôle : retour à son propre espace.
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default PrivateRoute
