import { Navigate, useSearchParams } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { safeRedirectPath } from '@/utils/safePath'

/**
 * Renvoie ailleurs un visiteur **déjà connecté** qui arrive sur une page
 * d'authentification. Sans elle, `/login` affichait son formulaire à quelqu'un
 * dont la session est ouverte — une impasse : se reconnecter alors qu'on l'est
 * déjà ne mène nulle part.
 *
 * ⚠️ **Elle n'attend pas `initialized`, et c'est délibéré.** `PrivateRoute`
 * doit attendre, lui, parce qu'il tranche un *refus* : décider trop tôt
 * éjecterait un formateur légitime. Ici la décision est inverse — on ne
 * redirige que sur une **présence** d'utilisateur. Attendre aurait posé un
 * écran de chargement sur la page de connexion de quiconque traîne un jeton
 * périmé, et c'est exactement la famille de symptômes (« la connexion charge
 * sans fin ») que ce dépôt a déjà payée une fois.
 *
 * Conséquence assumée : avec un jeton mort, le formulaire s'affiche
 * normalement. C'est le bon comportement — il faut bien pouvoir se
 * reconnecter.
 */
export default function PublicOnlyRoute({ children }) {
  const { user } = useSelector((state) => state.auth)
  const [searchParams] = useSearchParams()

  if (!user) return children

  // ⚠️ On respecte `?next=` : sans cela, quelqu'un de déjà connecté qui suit
  // un lien d'invitation (`/login?next=/rejoindre/<jeton>`) serait renvoyé au
  // tableau de bord et **ne serait jamais rattaché à la classe**. Le chemin
  // passe par `safeRedirectPath`, qui écarte les adresses externes.
  return <Navigate to={safeRedirectPath(searchParams.get('next'))} replace />
}
