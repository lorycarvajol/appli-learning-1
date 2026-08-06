import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

// Importé depuis `src/assets/` : Vite hache le nom de fichier, donc cache long
// terme et invalidation automatique quand le logo change. Dans `public/`, le
// nom resterait identique et les visiteurs de retour garderaient l'ancienne
// image en cache.
import logo from '@/assets/logo.png';
import './BrandLogo.css';

/**
 * Bloc de marque des pages hors application (connexion, inscription, mot de
 * passe oublié, invitation).
 *
 * Le même balisage était recopié dans cinq fichiers. Il porte désormais le
 * logo complet — sigle **et** nom — là où la place le permet ; l'en-tête, lui,
 * n'affiche que le sigle, le nom y étant rendu en HTML (illisible à 34 px s'il
 * était dans l'image).
 *
 * L'image est décorative : le nom accessible vit sur le lien, sinon un lecteur
 * d'écran annoncerait deux fois la même chose.
 */
export default function BrandLogo({ to = '/dashboard' }) {
  return (
    <Link to={to} className="brand-logo" aria-label="CodeAcademy — accueil">
      <img
        src={logo}
        alt=""
        aria-hidden="true"
        className="brand-logo__image"
        width="104"
        height="104"
      />
    </Link>
  );
}

BrandLogo.propTypes = {
  /** Destination du lien : le tableau de bord, ou la connexion si l'on n'y a pas accès. */
  to: PropTypes.string,
};
