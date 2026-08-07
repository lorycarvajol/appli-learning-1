import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '@/features/auth/authSlice';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Avatar from '@/components/ui/Avatar';
import { ROLES, ROLE_LABELS, STAFF_ROLES } from '@/constants/roles';
// Importé depuis `src/assets/` et non `public/` : Vite hache le nom de
// fichier, ce qui donne un cache long terme *et* l'invalidation automatique
// le jour où le logo change. Dans `public/`, le nom resterait le même et les
// visiteurs de retour verraient l'ancienne image.
import logoMark from '@/assets/logo-mark.png';
import './Header.css';

// Une entrée sans `roles` est visible par tout le monde.
const NAV_LINKS = [
  { path: '/dashboard', label: 'Tableau de bord' },
  { path: '/chapters', label: 'Chapitres' },
  { path: '/progression', label: 'Ma progression' },
  { path: '/badges', label: 'Trophées' },
  { path: '/classement', label: 'Classement' },
  { path: '/trainer', label: 'Espace formateur', roles: STAFF_ROLES },
  { path: '/administration', label: 'Administration', roles: [ROLES.ADMIN] },
];

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setShowUserMenu(false);
      }
    };
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowUserMenu(false);
        setShowMobileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  useEffect(() => {
    setShowMobileMenu(false);
    setShowUserMenu(false);
  }, [location.pathname]);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Un lien non autorisé n'est pas affiché : inutile de proposer une page
  // dont la garde de route renverra l'utilisateur.
  const navLinks = NAV_LINKS.filter(
    (link) => !link.roles || link.roles.includes(user?.role)
  );

  // Les initiales sont désormais calculées par `Avatar`, qui gère aussi le
  // cas d'un avatar choisi au catalogue.
  const displayName =
    user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email;
  const roleLabel = ROLE_LABELS[user?.role] || '';

  return (
    <header className="header">
      <div className="header__container">
        <Link to="/dashboard" className="header__logo">
          {/*
            Le sigle de marque, pas un placeholder : ce bloc dessinait un
            `</>` en CSS alors que `logo-mark.png` existait.

            Le sigle seul, jamais le logo complet : celui-ci porte
            « CODE ACADEMY » en dur, illisible à 34 px de haut. Le nom reste
            donc du texte HTML — net à toute densité d'écran, et masqué sur
            mobile par la règle existante. L'image est donc décorative, et la
            relire ferait doublon pour un lecteur d'écran.
          */}
          <img
            src={logoMark}
            alt=""
            aria-hidden="true"
            className="header__logo-mark"
            width="34"
            height="34"
          />
          <span className="header__logo-text">
            <span className="header__logo-name">Code</span>
            <span className="header__logo-suffix">Academy</span>
          </span>
        </Link>

        <nav className="header__nav" aria-label="Navigation principale">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`header__nav-link ${isActive(link.path) ? 'header__nav-link--active' : ''}`}
              aria-current={isActive(link.path) ? 'page' : undefined}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="header__actions">
          <ThemeToggle />

          <div className="header__user-menu" ref={userMenuRef}>
            <button
              type="button"
              className="header__user-button"
              onClick={() => setShowUserMenu((open) => !open)}
              aria-haspopup="menu"
              aria-expanded={showUserMenu}
              aria-controls="user-menu"
            >
              <Avatar user={user} size={36} className="header__user-avatar" />
              <span className="header__user-info">
                <span className="header__user-name">{displayName}</span>
                <span className="header__user-role">{roleLabel}</span>
              </span>
              <svg
                className="header__user-arrow"
                viewBox="0 0 24 24"
                width="14"
                height="14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            {showUserMenu && (
              <div className="header__user-dropdown" id="user-menu" role="menu">
                <Link
                  to="/profil"
                  className="header__dropdown-item"
                  role="menuitem"
                  onClick={() => setShowUserMenu(false)}
                >
                  Mon profil
                </Link>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="header__dropdown-item header__dropdown-item--logout"
                  role="menuitem"
                >
                  Déconnexion
                </button>
              </div>
            )}
          </div>

          <button
            type="button"
            className="header__mobile-toggle"
            onClick={() => setShowMobileMenu((open) => !open)}
            aria-expanded={showMobileMenu}
            aria-controls="mobile-nav"
            aria-label={showMobileMenu ? 'Fermer le menu' : 'Ouvrir le menu'}
          >
            <span className={`header__mobile-toggle-icon ${showMobileMenu ? 'header__mobile-toggle-icon--open' : ''}`} aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
          </button>
        </div>
      </div>

      {showMobileMenu && (
        <nav className="header__mobile-nav" id="mobile-nav" aria-label="Navigation mobile">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`header__mobile-link ${isActive(link.path) ? 'header__mobile-link--active' : ''}`}
              aria-current={isActive(link.path) ? 'page' : undefined}
            >
              {link.label}
            </Link>
          ))}
          <div className="header__mobile-divider" role="separator"></div>
          <button type="button" onClick={handleLogout} className="header__mobile-link header__mobile-link--logout">
            Déconnexion
          </button>
        </nav>
      )}
    </header>
  );
}
