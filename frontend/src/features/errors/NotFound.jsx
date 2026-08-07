import { Link, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Layout from '@/components/layout/Layout'
import './NotFound.css'

/**
 * Page servie pour toute URL qui ne correspond à aucune route.
 *
 * ⚠️ Avant elle, `<Routes>` n'avait **aucune route `*`** : une adresse
 * inconnue ne rendait rien du tout. Pas d'erreur, pas de message — une page
 * blanche, le pire des cas parce qu'elle ressemble à une panne du site alors
 * qu'il s'agit d'une faute de frappe.
 *
 * Le chemin demandé est affiché tel quel, en chasse fixe : c'est la seule
 * information qui permet à quelqu'un de repérer sa propre coquille. React
 * échappe le contenu, il n'y a donc rien à assainir ; seule la mise en page
 * doit résister à une adresse absurdement longue (cf. `NotFound.css`).
 */
export default function NotFound() {
  const location = useLocation()
  const { user } = useSelector((state) => state.auth)

  // On enveloppe dans `Layout` dès qu'un jeton existe, sans attendre que le
  // profil soit chargé : `localStorage` répond tout de suite, et `Header`
  // tolère l'absence d'utilisateur (`user?.` partout). Attendre `initialized`
  // aurait fait clignoter la page — version sans en-tête, puis avec.
  const connecte = Boolean(user) || Boolean(localStorage.getItem('accessToken'))

  const contenu = (
    <div className="not-found">
      <div className="not-found__card">
        <p className="not-found__code">404</p>
        <h1 className="not-found__title">Cette page n’existe pas</h1>

        <p className="not-found__path" title={location.pathname}>
          {location.pathname}
        </p>

        <p className="not-found__text">
          L’adresse demandée ne correspond à aucune page de la plateforme.
          Elle a peut-être été mal recopiée, ou le contenu qu’elle désignait
          a changé d’adresse.
        </p>

        {/*
          Deux issues, jamais zéro. Elles diffèrent selon qu'on est connecté :
          proposer le tableau de bord à un visiteur sans session l'enverrait
          vers la page de connexion, ce qui ressemble à une seconde erreur.
        */}
        <div className="not-found__actions">
          {connecte ? (
            <>
              <Link to="/dashboard" className="not-found__button">
                Retour au tableau de bord
              </Link>
              <Link to="/chapters" className="not-found__link">
                Parcourir les chapitres
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="not-found__button">
                Se connecter
              </Link>
              <Link to="/register" className="not-found__link">
                Créer un compte
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )

  return connecte ? <Layout>{contenu}</Layout> : contenu
}
