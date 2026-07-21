/**
 * Carte d'un badge.
 *
 * Trois états visuels :
 *  - obtenu      : couleurs du palier, icône pleine, date d'obtention
 *  - à débloquer : grisé, avec barre de progression (objectif visible)
 *  - secret      : silhouette et point d'interrogation, seule l'énigme s'affiche
 *
 * Le masquage vient du serveur : le composant ne connaît tout simplement pas
 * le contenu d'un secret non débloqué.
 */
export default function BadgeCard({ badge }) {
  const isLocked = !badge.is_earned;
  const isHiddenSecret = badge.is_secret && isLocked;
  const progress = badge.progress;

  const modifiers = [
    `badge-card--${badge.tier.toLowerCase()}`,
    badge.is_earned ? 'badge-card--earned' : 'badge-card--locked',
    isHiddenSecret ? 'badge-card--secret' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <article className={`badge-card ${modifiers}`}>
      <div className="badge-card__medal" aria-hidden="true">
        <span className="badge-card__icon">{badge.icon}</span>
      </div>

      <div className="badge-card__body">
        <h3 className="badge-card__name">
          {badge.name}
          {badge.is_earned && badge.is_secret && (
            <span className="badge-card__revealed-tag">révélé</span>
          )}
        </h3>
        <p className="badge-card__description">{badge.description}</p>

        {progress && isLocked && (
          <div className="badge-card__progress">
            <div
              className="badge-card__progress-track"
              role="progressbar"
              aria-label={`Progression vers ${badge.name}`}
              aria-valuenow={progress.percent}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                className="badge-card__progress-fill"
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <span className="badge-card__progress-label">
              {progress.current} / {progress.target}
            </span>
          </div>
        )}

        <div className="badge-card__footer">
          {badge.is_earned ? (
            <span className="badge-card__earned-at">
              Obtenu le{' '}
              {new Date(badge.earned_at).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
              })}
            </span>
          ) : (
            <span className="badge-card__status">
              {isHiddenSecret ? 'Objectif caché' : 'À débloquer'}
            </span>
          )}

          {badge.points_reward > 0 && (
            <span className="badge-card__reward">+{badge.points_reward} pts</span>
          )}
        </div>
      </div>
    </article>
  );
}
