import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import {
  fetchMyProgress,
  fetchNextLesson,
  selectAllProgress,
  selectNextLesson,
} from '../progression/progressionSlice';
import NextObjectives from '../gamification/NextObjectives';
import {
  selectLevel,
  selectSummary,
  syncGamification,
} from '../gamification/gamificationSlice';
import './Dashboard.css';

const LESSON_TYPE_LABELS = {
  THEORY: '📖 Théorie',
  EXERCISE: '💻 Exercice',
  QUIZ: '❓ Quiz',
};

export default function Dashboard() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const progressByLesson = useSelector(selectAllProgress);
  const summary = useSelector(selectSummary);
  const level = useSelector(selectLevel);
  const nextLesson = useSelector(selectNextLesson);

  useEffect(() => {
    dispatch(fetchMyProgress());
    dispatch(fetchNextLesson());
    // `sync` est idempotent côté serveur : il rattrape un éventuel badge
    // manqué (session interrompue, onglet fermé) sans rien redistribuer.
    dispatch(syncGamification());
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
              <div className="stat-card__value">
                {summary?.points ?? user?.profile?.total_points ?? 0}
              </div>
              <div className="stat-card__label">Points totaux</div>
              {level && (
                <div className="stat-card__sublabel">
                  Encore {level.points_for_next} pts avant le niveau {level.level + 1}
                </div>
              )}
            </div>
            <div className="stat-card__badge">
              Niveau {level?.level ?? user?.profile?.level ?? 1}
            </div>
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

          <div className="stat-card stat-card--trophy">
            <div className="stat-card__icon" aria-hidden="true">🏅</div>
            <div className="stat-card__content">
              <div className="stat-card__value">
                {summary?.badges?.earned ?? 0}
                <span className="stat-card__value-total">
                  /{summary?.badges?.total ?? 0}
                </span>
              </div>
              <div className="stat-card__label">Trophées</div>
              <div className="stat-card__sublabel">
                {summary?.badges?.secret_found ?? 0} secret(s) sur{' '}
                {summary?.badges?.secret_total ?? 0} révélé(s)
              </div>
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

              {nextLesson?.lesson ? (
                <div className="learning-card">
                  <div className="learning-card__content">
                    <span className="learning-card__kicker">
                      {nextLesson.chapter.title}
                    </span>
                    <h3 className="learning-card__title">{nextLesson.lesson.title}</h3>
                    <p className="learning-card__description">
                      {nextLesson.is_resuming
                        ? 'Vous aviez commencé cette leçon — reprenez où vous en étiez.'
                        : 'La prochaine étape de votre parcours vous attend.'}
                    </p>
                    <div className="learning-card__meta">
                      <span className="learning-card__badge">
                        {LESSON_TYPE_LABELS[nextLesson.lesson.lesson_type] || '📄 Leçon'}
                      </span>
                      <span className="learning-card__duration">
                        ⏱️ {nextLesson.lesson.estimated_duration} min
                      </span>
                      <span className="learning-card__duration">
                        📍 Leçon {nextLesson.chapter_progress.position} sur{' '}
                        {nextLesson.chapter_progress.total}
                      </span>
                    </div>
                  </div>
                  <Link
                    to={`/lessons/${nextLesson.lesson.slug}`}
                    className="learning-card__button"
                  >
                    {nextLesson.is_resuming ? 'Reprendre' : 'Commencer'}
                  </Link>
                </div>
              ) : nextLesson?.all_completed ? (
                <div className="learning-card learning-card--done">
                  <div className="learning-card__content">
                    <h3 className="learning-card__title">
                      Parcours terminé, félicitations ! 🎉
                    </h3>
                    <p className="learning-card__description">
                      Vous avez complété toutes les leçons disponibles. Il reste
                      peut-être des trophées à décrocher.
                    </p>
                  </div>
                  <Link to="/badges" className="learning-card__button">
                    Voir mes trophées
                  </Link>
                </div>
              ) : (
                <div className="learning-card learning-card--empty">
                  <div className="learning-card__content">
                    <h3 className="learning-card__title">Aucune leçon disponible</h3>
                    <p className="learning-card__description">
                      Le contenu n’est pas encore publié. Revenez bientôt !
                    </p>
                  </div>
                </div>
              )}
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

                <Link to="/badges" className="quick-action">
                  <div className="quick-action__icon">🏆</div>
                  <div className="quick-action__content">
                    <h3 className="quick-action__title">Mes trophées</h3>
                    <p className="quick-action__description">
                      {summary?.badges
                        ? `${summary.badges.earned}/${summary.badges.total} obtenus, ${
                            summary.badges.secret_total - summary.badges.secret_found
                          } encore cachés`
                        : 'Badges obtenus et objectifs cachés'}
                    </p>
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

            {/* Prochains objectifs — alimentés par le moteur de badges */}
            <div className="sidebar-card">
              <h3 className="sidebar-card__title">🏆 Prochains objectifs</h3>
              <NextObjectives />
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
