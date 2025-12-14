import { Link } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    platform: [
      { label: 'Chapitres', path: '/chapters' },
      { label: 'Ma progression', path: '/progression' },
      { label: 'Tableau de bord', path: '/dashboard' },
    ],
    resources: [
      { label: 'Documentation', path: '/docs' },
      { label: 'Tutoriels', path: '/tutorials' },
      { label: 'FAQ', path: '/faq' },
    ],
    legal: [
      { label: 'Mentions légales', path: '/legal' },
      { label: 'Politique de confidentialité', path: '/privacy' },
      { label: 'Conditions d\'utilisation', path: '/terms' },
    ],
  };

  const socialLinks = [
    { icon: '💼', label: 'LinkedIn', url: '#' },
    { icon: '🐙', label: 'GitHub', url: '#' },
    { icon: '🐦', label: 'Twitter', url: '#' },
    { icon: '📘', label: 'Facebook', url: '#' },
  ];

  return (
    <footer className="footer">
      <div className="footer__container">
        {/* Top Section */}
        <div className="footer__top">
          {/* Brand */}
          <div className="footer__brand">
            <div className="footer__logo">
              <span className="footer__logo-icon">🎓</span>
              <span className="footer__logo-text">CodeAcademy</span>
            </div>
            <p className="footer__tagline">
              Apprenez le développement web de manière interactive et pédagogique.
              Maîtrisez HTML, CSS, JavaScript et bien plus encore !
            </p>
            <div className="footer__social">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.url}
                  className="footer__social-link"
                  target="_blank"
                  rel="noopener noreferrer"
                  title={social.label}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Links Columns */}
          <div className="footer__links">
            <div className="footer__column">
              <h4 className="footer__column-title">Plateforme</h4>
              <ul className="footer__column-list">
                {footerLinks.platform.map((link) => (
                  <li key={link.path}>
                    <Link to={link.path} className="footer__link">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="footer__column">
              <h4 className="footer__column-title">Ressources</h4>
              <ul className="footer__column-list">
                {footerLinks.resources.map((link) => (
                  <li key={link.path}>
                    <Link to={link.path} className="footer__link">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="footer__column">
              <h4 className="footer__column-title">Légal</h4>
              <ul className="footer__column-list">
                {footerLinks.legal.map((link) => (
                  <li key={link.path}>
                    <Link to={link.path} className="footer__link">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="footer__bottom">
          <p className="footer__copyright">
            © {currentYear} CodeAcademy. Tous droits réservés.
          </p>
          <p className="footer__credits">
            Fait avec ❤️ par l'équipe CodeAcademy
          </p>
        </div>
      </div>
    </footer>
  );
}
