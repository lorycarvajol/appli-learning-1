import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectBadgeStats, selectNextObjectives, selectSummary } from './gamificationSlice';
import './NextObjectives.css';

/**
 * Les trois objectifs visibles dont l'apprenant est le plus proche, plus un
 * rappel du nombre d'objectifs cachés restants.
 *
 * Le tri « du plus proche du but » vient du serveur : on montre ce qui est
 * atteignable maintenant, pas un mur d'objectifs lointains.
 */
export default function NextObjectives() {
  const objectives = useSelector(selectNextObjectives);
  const stats = useSelector(selectBadgeStats);
  const summary = useSelector(selectSummary);

  const secretsLeft = Math.max(
    0,
    (summary?.badges?.secret_total ?? stats.secret_total) -
      (summary?.badges?.secret_found ?? stats.secret_found)
  );

  return (
    <div className="next-objectives">
      {objectives.length === 0 ? (
        <p className="next-objectives__empty">
          Tous les objectifs visibles sont atteints. Il ne reste que les secrets…
        </p>
      ) : (
        <ul className="next-objectives__list">
          {objectives.map((objective) => (
            <li key={objective.code} className="objective">
              <span className="objective__icon" aria-hidden="true">
                {objective.icon}
              </span>
              <div className="objective__content">
                <div className="objective__header">
                  <span className="objective__name">{objective.name}</span>
                  <span className="objective__count">
                    {objective.progress.current}/{objective.progress.target}
                  </span>
                </div>
                <div
                  className="objective__track"
                  role="progressbar"
                  aria-label={`Progression vers ${objective.name}`}
                  aria-valuenow={objective.progress.percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="objective__fill"
                    style={{ width: `${objective.progress.percent}%` }}
                  />
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {secretsLeft > 0 && (
        <p className="next-objectives__secret">
          <span aria-hidden="true">🔒</span> {secretsLeft} objectif
          {secretsLeft > 1 ? 's' : ''} caché{secretsLeft > 1 ? 's' : ''} vous attend
          {secretsLeft > 1 ? 'ent' : ''}.
        </p>
      )}

      <Link to="/badges" className="next-objectives__link">
        Voir tous les trophées →
      </Link>
    </div>
  );
}
