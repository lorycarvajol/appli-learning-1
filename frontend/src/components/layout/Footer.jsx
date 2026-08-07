import { Link } from 'react-router-dom';
import logoMark from '@/assets/logo-mark.png';
import './Footer.css';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const links = [
    { label: 'Tableau de bord', path: '/dashboard' },
    { label: 'Chapitres', path: '/chapters' },
    { label: 'Ma progression', path: '/progression' },
  ];

  const legalLinks = [
    { label: 'Confidentialité', path: '/confidentialite' },
    { label: 'Mentions légales', path: '/mentions-legales' },
    { label: 'CGU', path: '/cgu' },
  ];

  /*
    ⚠️ Ce lien n'est pas décoratif : c'est une **obligation de la licence**.
    La plateforme est sous AGPL-3.0, dont la section 13 (« Remote Network
    Interaction ») impose que quiconque utilise le logiciel *à travers le
    réseau* — donc chaque visiteur, sans rien installer — puisse obtenir le
    code source. Un fichier LICENSE dans le dépôt ne suffit pas à satisfaire
    cette clause pour une application déployée : il faut une offre visible
    depuis l'application elle-même. Ne pas le retirer sans changer de licence.
  */
  const SOURCE_URL = 'https://github.com/lorycarvajol/appli-learning-1';

  return (
    <footer className="footer">
      <div className="footer__container">
        <div className="footer__brand">
          <div className="footer__logo">
            {/* Le sigle seul, comme dans l'en-tête : à 24 px, le nom gravé
                dans le logo complet serait illisible. */}
            <img
              src={logoMark}
              alt=""
              aria-hidden="true"
              className="footer__logo-mark"
              width="24"
              height="24"
            />
            <span>CodeAcademy</span>
          </div>
          <p className="footer__tagline">
            Apprenez le développement web pas à pas : HTML, CSS et au-delà,
            avec des exercices corrigés automatiquement.
          </p>
        </div>

        <nav className="footer__links" aria-label="Liens du pied de page">
          {links.map((link) => (
            <Link key={link.path} to={link.path} className="footer__link">
              {link.label}
            </Link>
          ))}
        </nav>

        <nav className="footer__links" aria-label="Liens légaux">
          {legalLinks.map((link) => (
            <Link key={link.path} to={link.path} className="footer__link">
              {link.label}
            </Link>
          ))}
        </nav>

        <p className="footer__copyright">
          © {currentYear} CodeAcademy ·{' '}
          <a
            className="footer__link"
            href={SOURCE_URL}
            target="_blank"
            rel="noreferrer noopener"
          >
            Code source
          </a>{' '}
          <abbr title="GNU Affero General Public License, version 3">(AGPL-3.0)</abbr>
        </p>
      </div>
    </footer>
  );
}
