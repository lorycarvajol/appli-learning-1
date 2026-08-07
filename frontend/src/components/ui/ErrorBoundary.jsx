import { Component } from 'react'
import { Link, useLocation } from 'react-router-dom'
import PropTypes from 'prop-types'
import './ErrorBoundary.css'

/**
 * Frontière d'erreur : elle attrape une erreur de **rendu** React et affiche
 * quelque chose plutôt que rien.
 *
 * ⚠️ Sans elle, une seule exception pendant le rendu démonte tout l'arbre et
 * laisse un **écran blanc**. C'est le pire message d'erreur possible : il ne
 * dit pas ce qui s'est passé, ne propose aucune sortie, et se confond avec une
 * panne de réseau ou une page qui n'a pas fini de charger. Personne ne sait
 * quoi faire devant, pas même pour signaler le problème.
 *
 * Elle ne remplace pas la gestion d'erreur des appels réseau — les thunks
 * Redux rangent déjà leurs échecs dans `error`, et les écrans les affichent.
 * Elle attrape ce qui reste : une réponse d'API d'une forme inattendue, un
 * champ absent qu'on déréférence, une régression de rendu.
 *
 * ⚠️ Ce que React ne permet **pas** d'attraper ici, et qu'il ne faut pas
 * croire couvert : les erreurs asynchrones (promesses, `setTimeout`, gestion
 * d'événements) et celles du rendu serveur. Une frontière ne voit que le
 * rendu, les méthodes de cycle de vie et les constructeurs de ses descendants.
 */
class Frontiere extends Component {
  constructor(props) {
    super(props)
    this.state = { erreur: null }
  }

  static getDerivedStateFromError(erreur) {
    return { erreur }
  }

  componentDidCatch(erreur, infos) {
    // React journalise déjà l'erreur ; on garde la pile de composants, qui dit
    // *où* ça a cassé — la seule information vraiment utile au diagnostic.
    // C'est ici que se brancherait un collecteur côté client, le jour où il y
    // en aura un : `SENTRY_DSN` n'est câblé que côté Django.
    console.error('Erreur de rendu attrapée :', erreur, infos?.componentStack)
  }

  render() {
    if (!this.state.erreur) return this.props.children

    return (
      <div className="frontiere-erreur">
        <div className="frontiere-erreur__carte">
          <p className="frontiere-erreur__code">Erreur</p>
          <h1 className="frontiere-erreur__titre">Cette page n’a pas pu s’afficher</h1>

          <p className="frontiere-erreur__texte">
            Quelque chose s’est mal passé de notre côté. Votre travail
            enregistré n’est pas affecté — recharger suffit le plus souvent.
          </p>

          {/*
            Le détail technique n'apparaît qu'en développement. En production
            il n'apprendrait rien à un apprenant, et exposerait des noms de
            composants et de champs internes.
          */}
          {import.meta.env.DEV && (
            <pre className="frontiere-erreur__detail">
              {String(this.state.erreur)}
            </pre>
          )}

          <div className="frontiere-erreur__actions">
            {/*
              Un rechargement complet, pas un `setState` : l'arbre React est
              dans un état inconnu, le remonter à moitié le laisserait dans le
              même. C'est le seul remède fiable.
            */}
            <button
              type="button"
              className="frontiere-erreur__bouton"
              onClick={() => window.location.reload()}
            >
              Recharger la page
            </button>
            <Link to="/dashboard" className="frontiere-erreur__lien">
              Retour au tableau de bord
            </Link>
          </div>
        </div>
      </div>
    )
  }
}

Frontiere.propTypes = {
  children: PropTypes.node,
}

/**
 * ⚠️ La clé n'est pas un détail : une frontière d'erreur **ne se réarme pas
 * toute seule**. Sans elle, un visiteur qui clique « Retour au tableau de
 * bord » changerait d'URL et resterait devant le même message d'erreur —
 * le lien de sortie ne sortirait de rien. La clé remonte le composant à
 * chaque changement de chemin, ce qui l'efface.
 */
export default function ErrorBoundary({ children }) {
  const { pathname } = useLocation()
  return <Frontiere key={pathname}>{children}</Frontiere>
}

ErrorBoundary.propTypes = {
  children: PropTypes.node,
}
