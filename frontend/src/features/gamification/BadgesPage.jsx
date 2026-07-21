import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import BadgeCard from './BadgeCard';
import {
  fetchBadges,
  fetchGamificationSummary,
  selectBadgeStats,
  selectBadges,
  selectBadgesLoading,
  selectSummary,
} from './gamificationSlice';
import './BadgesPage.css';

const CATEGORIES = [
  { key: 'ALL', label: 'Tout', icon: '✨' },
  { key: 'PROGRESSION', label: 'Progression', icon: '📈' },
  { key: 'MASTERY', label: 'Maîtrise', icon: '🎓' },
  { key: 'REGULARITY', label: 'Régularité', icon: '🔥' },
  { key: 'EXPLORATION', label: 'Exploration', icon: '🧭' },
];

export default function BadgesPage() {
  const dispatch = useDispatch();
  const badges = useSelector(selectBadges);
  const stats = useSelector(selectBadgeStats);
  const summary = useSelector(selectSummary);
  const loading = useSelector(selectBadgesLoading);
  const [category, setCategory] = useState('ALL');

  useEffect(() => {
    dispatch(fetchBadges());
    dispatch(fetchGamificationSummary());
  }, [dispatch]);

  const visible = useMemo(() => {
    const filtered =
      category === 'ALL' ? badges : badges.filter((b) => b.category === category);

    // Obtenus d'abord (c'est la vitrine), puis les objectifs les plus proches
    // du but, et enfin les secrets encore intacts.
    return [...filtered].sort((a, b) => {
      if (a.is_earned !== b.is_earned) return a.is_earned ? -1 : 1;
      const pa = a.progress?.percent ?? -1;
      const pb = b.progress?.percent ?? -1;
      return pb - pa;
    });
  }, [badges, category]);

  const completion = stats.total_count
    ? Math.round((stats.earned_count / stats.total_count) * 100)
    : 0;

  return (
    <div className="badges-page">
      <header className="badges-page__hero">
        <div className="badges-page__hero-content">
          <h1 className="badges-page__title">Vos trophées</h1>
          <p className="badges-page__subtitle">
            Chaque objectif ne se débloque qu’une fois — et pour toujours.
          </p>

          <div className="badges-page__hero-stats">
            <div className="trophy-stat">
              <span className="trophy-stat__value">
                {stats.earned_count}
                <span className="trophy-stat__total">/ {stats.total_count}</span>
              </span>
              <span className="trophy-stat__label">Trophées obtenus</span>
            </div>
            <div className="trophy-stat">
              <span className="trophy-stat__value">
                {stats.secret_found}
                <span className="trophy-stat__total">/ {stats.secret_total}</span>
              </span>
              <span className="trophy-stat__label">Secrets révélés</span>
            </div>
            {summary?.streak && (
              <div className="trophy-stat">
                <span className="trophy-stat__value">
                  {summary.streak.current_streak}
                  <span className="trophy-stat__total">j</span>
                </span>
                <span className="trophy-stat__label">Série en cours</span>
              </div>
            )}
          </div>

          <div
            className="badges-page__completion"
            role="progressbar"
            aria-label="Collection complétée"
            aria-valuenow={completion}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="badges-page__completion-fill"
              style={{ width: `${completion}%` }}
            />
          </div>
          <p className="badges-page__completion-label">
            Collection complétée à {completion} %
          </p>
        </div>
      </header>

      <div className="badges-page__container">
        <nav className="badges-page__filters" aria-label="Filtrer par catégorie">
          {CATEGORIES.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setCategory(item.key)}
              className={`badges-filter ${
                category === item.key ? 'badges-filter--active' : ''
              }`}
              aria-pressed={category === item.key}
            >
              <span aria-hidden="true">{item.icon}</span> {item.label}
            </button>
          ))}
        </nav>

        {loading && badges.length === 0 ? (
          <p className="badges-page__empty">Chargement de vos trophées…</p>
        ) : visible.length === 0 ? (
          <p className="badges-page__empty">Aucun trophée dans cette catégorie.</p>
        ) : (
          <div className="badges-page__grid">
            {visible.map((badge) => (
              <BadgeCard key={badge.id} badge={badge} />
            ))}
          </div>
        )}

        {stats.secret_total > stats.secret_found && (
          <p className="badges-page__teaser">
            🔒 Il reste{' '}
            <strong>{stats.secret_total - stats.secret_found} objectif(s) caché(s)</strong>{' '}
            à découvrir. Personne ne vous dira comment — c’est tout l’intérêt.
          </p>
        )}
      </div>
    </div>
  );
}
