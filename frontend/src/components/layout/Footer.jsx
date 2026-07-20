import { Link } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const links = [
    { label: 'Tableau de bord', path: '/dashboard' },
    { label: 'Chapitres', path: '/chapters' },
    { label: 'Ma progression', path: '/progression' },
  ];

  return (
    <footer className="footer">
      <div className="footer__container">
        <div className="footer__brand">
          <div className="footer__logo">
            <span className="footer__logo-mark" aria-hidden="true">&lt;/&gt;</span>
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

        <p className="footer__copyright">
          © {currentYear} CodeAcademy
        </p>
      </div>
    </footer>
  );
}
