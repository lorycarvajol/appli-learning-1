import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '@/features/auth/authSlice';
import './Header.css';

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const navLinks = [
    { path: '/dashboard', label: 'Tableau de bord', icon: '📊' },
    { path: '/chapters', label: 'Chapitres', icon: '📚' },
    { path: '/progression', label: 'Ma progression', icon: '📈' },
  ];

  return (
    <header className="header">
      <div className="header__container">
        {/* Logo */}
        <Link to="/dashboard" className="header__logo">
          <span className="header__logo-icon">🎓</span>
          <span className="header__logo-text">
            <span className="header__logo-name">Code</span>
            <span className="header__logo-suffix">Academy</span>
          </span>
        </Link>

        {/* Navigation Desktop */}
        <nav className="header__nav">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`header__nav-link ${isActive(link.path) ? 'header__nav-link--active' : ''}`}
            >
              <span className="header__nav-icon">{link.icon}</span>
              <span className="header__nav-label">{link.label}</span>
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="header__actions">
          {/* User Profile Dropdown */}
          <div className="header__user-menu">
            <button
              className="header__user-button"
              onClick={() => setShowUserMenu(!showUserMenu)}
              onBlur={() => setTimeout(() => setShowUserMenu(false), 200)}
            >
              <div className="header__user-avatar">
                {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </div>
              <div className="header__user-info">
                <span className="header__user-name">
                  {user?.first_name && user?.last_name
                    ? `${user.first_name} ${user.last_name}`
                    : user?.email}
                </span>
                <span className="header__user-role">
                  {user?.role === 'LEARNER' ? 'Apprenant' : user?.role === 'TRAINER' ? 'Formateur' : 'Admin'}
                </span>
              </div>
              <span className="header__user-arrow">▼</span>
            </button>

            {showUserMenu && (
              <div className="header__user-dropdown">
                <Link to="/profile" className="header__dropdown-item">
                  <span className="header__dropdown-icon">👤</span>
                  Mon profil
                </Link>
                <Link to="/settings" className="header__dropdown-item">
                  <span className="header__dropdown-icon">⚙️</span>
                  Paramètres
                </Link>
                <div className="header__dropdown-divider"></div>
                <button onClick={handleLogout} className="header__dropdown-item header__dropdown-item--logout">
                  <span className="header__dropdown-icon">🚪</span>
                  Déconnexion
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="header__mobile-toggle"
            onClick={() => setShowMobileMenu(!showMobileMenu)}
          >
            <span className="header__mobile-toggle-icon">
              {showMobileMenu ? '✕' : '☰'}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {showMobileMenu && (
        <div className="header__mobile-nav">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`header__mobile-link ${isActive(link.path) ? 'header__mobile-link--active' : ''}`}
              onClick={() => setShowMobileMenu(false)}
            >
              <span className="header__mobile-icon">{link.icon}</span>
              <span className="header__mobile-label">{link.label}</span>
            </Link>
          ))}
          <div className="header__mobile-divider"></div>
          <Link
            to="/profile"
            className="header__mobile-link"
            onClick={() => setShowMobileMenu(false)}
          >
            <span className="header__mobile-icon">👤</span>
            <span className="header__mobile-label">Mon profil</span>
          </Link>
          <Link
            to="/settings"
            className="header__mobile-link"
            onClick={() => setShowMobileMenu(false)}
          >
            <span className="header__mobile-icon">⚙️</span>
            <span className="header__mobile-label">Paramètres</span>
          </Link>
          <button
            onClick={handleLogout}
            className="header__mobile-link header__mobile-link--logout"
          >
            <span className="header__mobile-icon">🚪</span>
            <span className="header__mobile-label">Déconnexion</span>
          </button>
        </div>
      )}
    </header>
  );
}
