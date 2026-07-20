import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchMyProgress, selectAllProgress } from '../progression/progressionSlice';
import './Dashboard.css';

export default function Dashboard() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const progressByLesson = useSelector(selectAllProgress);

  useEffect(() => {
    dispatch(fetchMyProgress());
  }, [dispatch]);

  // Calculer les statistiques
  const progressArray = Object.values(progressByLesson);
  const completedLessons = progressArray.filter((p) => p.status === 'COMPLETED').length;
  const inProgressLessons = progressArray.filter((p) => p.status === 'IN_PROGRESS').length;
  const totalTimeSpent = progressArray.reduce((sum, p) => sum + (p.time_spent || 0), 0);
  const avgScore = progressArray.length > 0
    ? progressArray.reduce((sum, p) => sum + (p.score || 0), 0) / progressArray.length
    : 0;

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}min`;
    return `${minutes}min`;
  };

  return (
    <div className="dashboard">
      {/* Hero Section */}
      <section className="dashboard__hero">
        <div className="dashboard__hero-content">
          <h1 className="dashboard__hero-title">
            Bonjour {user?.first_name || 'Apprenant'} ! 👋
          </h1>
          <p className="dashboard__hero-subtitle">
            Prêt à continuer votre apprentissage aujourd'hui ?
          </p>
        </div>
        <div className="dashboard__hero-illustration" aria-hidden="true">
          <div className="dashboard__hero-circle dashboard__hero-circle--1"></div>
          <div className="dashboard__hero-circle dashboard__hero-circle--2"></div>
          <div className="dashboard__hero-circle dashboard__hero-circle--3"></div>
        </div>
      </section>

      <div className="dashboard__container">
        {/* Stats Cards */}
        <section className="dashboard__stats">
          <div className="stat-card stat-card--purple">
            <div className="stat-card__icon" aria-hidden="true">🎯</div>
            <div className="stat-card__content">
              <div className="stat-card__value">{user?.profile?.total_points || 0}</div>
              <div className="stat-card__label">Points totaux</div>
            </div>
            <div className="stat-card__badge">Niveau {user?.profile?.level || 1}</div>
          </div>

          <div className="stat-card stat-card--green">
            <div className="stat-card__icon" aria-hidden="true">✅</div>
            <div className="stat-card__content">
              <div className="stat-card__value">{completedLessons}</div>
              <div className="stat-card__label">Leçons complétées</div>
            </div>
            <div className="stat-card__progress">{inProgressLessons} en cours</div>
          </div>

          <div className="stat-card stat-card--blue">
            <div className="stat-card__icon" aria-hidden="true">⏱️</div>
            <div className="stat-card__content">
              <div className="stat-card__value">{formatTime(totalTimeSpent)}</div>
              <div className="stat-card__label">Temps d'apprentissage</div>
            </div>
          </div>

          <div className="stat-card stat-card--orange">
            <div className="stat-card__icon" aria-hidden="true">📊</div>
            <div className="stat-card__content">
              <div className="stat-card__value">{Math.round(avgScore)}%</div>
              <div className="stat-card__label">Score moyen</div>
            </div>
          </div>
        </section>

        {/* Main Content */}
        <div className="dashboard__content">
          {/* Left Column */}
          <div className="dashboard__main">
            {/* Continue Learning */}
            <section className="dashboard__section">
              <div className="dashboard__section-header">
                <h2 className="dashboard__section-title">📚 Continuer l'apprentissage</h2>
                <Link to="/chapters" className="dashboard__section-link">
                  Voir tout →
                </Link>
              </div>

              <div className="learning-card">
                <div className="learning-card__content">
                  <h3 className="learning-card__title">Introduction au HTML</h3>
                  <p className="learning-card__description">
                    Apprenez les bases du langage HTML et créez votre première page web
                  </p>
                  <div className="learning-card__meta">
                    <span className="learning-card__badge">🏷️ Débutant</span>
                    <span className="learning-card__duration">⏱️ 2h estimées</span>
                  </div>
                </div>
                <Link to="/chapters/introduction-html" className="learning-card__button">
                  Commencer
                </Link>
              </div>
            </section>

            {/* Quick Actions */}
            <section className="dashboard__section">
              <h2 className="dashboard__section-title">⚡ Actions rapides</h2>

              <div className="quick-actions">
                <Link to="/chapters" className="quick-action">
                  <div className="quick-action__icon">📖</div>
                  <div className="quick-action__content">
                    <h3 className="quick-action__title">Explorer les chapitres</h3>
                    <p className="quick-action__description">Découvrez tous nos cours</p>
                  </div>
                  <span className="quick-action__arrow">→</span>
                </Link>

                <Link to="/progression" className="quick-action">
                  <div className="quick-action__icon">📈</div>
                  <div className="quick-action__content">
                    <h3 className="quick-action__title">Ma progression</h3>
                    <p className="quick-action__description">Suivez vos résultats</p>
                  </div>
                  <span className="quick-action__arrow">→</span>
                </Link>
              </div>
            </section>
          </div>

          {/* Right Sidebar */}
          <aside className="dashboard__sidebar">
            {/* Progress Overview */}
            <div className="sidebar-card">
              <h3 className="sidebar-card__title"><span aria-hidden="true">🎯</span> Vue d'ensemble</h3>
              <div className="progress-overview">
                <div className="progress-overview__item">
                  <div className="progress-overview__label" id="global-progress-label">Progression globale</div>
                  <div
                    className="progress-overview__bar"
                    role="progressbar"
                    aria-labelledby="global-progress-label"
                    aria-valuenow={completedLessons > 0 ? Math.round((completedLessons / (completedLessons + inProgressLessons)) * 100) : 0}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="progress-overview__fill"
                      style={{ width: `${completedLessons > 0 ? (completedLessons / (completedLessons + inProgressLessons)) * 100 : 0}%` }}
                    ></div>
                  </div>
                  <div className="progress-overview__value">
                    {completedLessons > 0 ? Math.round((completedLessons / (completedLessons + inProgressLessons)) * 100) : 0}%
                  </div>
                </div>
              </div>
            </div>

            {/* Achievements */}
            <div className="sidebar-card">
              <h3 className="sidebar-card__title">🏆 Prochains objectifs</h3>
              <div className="achievements">
                <div className="achievement">
                  <div className="achievement__icon">🎓</div>
                  <div className="achievement__content">
                    <div className="achievement__name">Premier pas</div>
                    <div className="achievement__progress">Terminer 5 leçons</div>
                  </div>
                </div>
                <div className="achievement">
                  <div className="achievement__icon">⭐</div>
                  <div className="achievement__content">
                    <div className="achievement__name">Expert HTML</div>
                    <div className="achievement__progress">Compléter le chapitre HTML</div>
                  </div>
                </div>
                <div className="achievement">
                  <div className="achievement__icon">🔥</div>
                  <div className="achievement__content">
                    <div className="achievement__name">Série active</div>
                    <div className="achievement__progress">7 jours consécutifs</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tips */}
            <div className="sidebar-card sidebar-card--highlight">
              <h3 className="sidebar-card__title">💡 Conseil du jour</h3>
              <p className="sidebar-card__text">
                Pratiquez régulièrement ! Même 15 minutes par jour peuvent faire une grande différence dans votre apprentissage.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
