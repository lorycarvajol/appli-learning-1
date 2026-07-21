import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '@/features/auth/authSlice';
import ThemeToggle from '@/components/ui/ThemeToggle';
import './Header.css';

const ROLE_LABELS = {
  LEARNER: 'Apprenant',
  TRAINER: 'Formateur',
  ADMIN: 'Admin',
};

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

  const navLinks = [
    { path: '/dashboard', label: 'Tableau de bord' },
    { path: '/chapters', label: 'Chapitres' },
    { path: '/progression', label: 'Ma progression' },
    { path: '/badges', label: 'Trophées' },
  ];

  const initials =
    (user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U').toUpperCase();
  const displayName =
    user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email;
  const roleLabel = ROLE_LABELS[user?.role] || '';

  return (
    <header className="header">
      <div className="header__container">
        <Link to="/dashboard" className="header__logo">
          <span className="header__logo-mark" aria-hidden="true">
            &lt;/&gt;
          </span>
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
              <span className="header__user-avatar" aria-hidden="true">
                {initials}
              </span>
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
