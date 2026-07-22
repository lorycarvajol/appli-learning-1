import { Link } from 'react-router-dom'
import './legal.css'

/**
 * Cadre commun aux trois pages légales publiques.
 *
 * Les `<a href="...">` de sortie (accueil, autres pages légales) sont
 * volontairement présents en pied : ces pages doivent rester navigables même
 * ouvertes seules, sans le header applicatif (qui exige une session).
 */
export default function LegalLayout({ title, updated, children }) {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <Link to="/" className="legal-back">
          <span aria-hidden="true">&larr;</span> Retour à l’accueil
        </Link>

        <article className="legal-card">
          <h1>{title}</h1>
          {updated && (
            <p className="legal-updated">Dernière mise à jour : {updated}</p>
          )}
          {children}
        </article>

        <nav className="legal-footer-nav" aria-label="Pages légales">
          <Link to="/confidentialite">Politique de confidentialité</Link>
          <Link to="/mentions-legales">Mentions légales</Link>
          <Link to="/cgu">Conditions d’utilisation</Link>
        </nav>
      </div>
    </div>
  )
}

/** Marqueur visuel d'une information que l'exploitant doit renseigner. */
export function Todo({ children }) {
  return <span className="legal-todo">[À COMPLÉTER : {children}]</span>
}
