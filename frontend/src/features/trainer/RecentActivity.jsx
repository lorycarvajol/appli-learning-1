import PropTypes from 'prop-types';
import { describeActivity } from '@/constants/activity';

/*
  Fusion des deux moitiés du travail formateur.

  Les deux branches avaient chacune une partie : celle-ci portait les classes
  BEM (retrait de Tailwind), l'autre `describeActivity` (centralisation de la
  table des types d'activité). Prises séparément, chacune gardait le défaut que
  l'autre corrigeait — ici, le libellé était fabriqué par
  `activity_type.replace('_', ' ').toLowerCase()`, soit « lesson started » en
  anglais dans une interface française.

  ⚠️ `describeActivity` renvoie aussi un `color`, qui est une paire de classes
  Tailwind (`bg-blue-50 border-blue-200`). Tailwind ayant été retiré, ce champ
  ne sert plus à rien : la teinte vient du modificateur BEM ci-dessous, adossé
  aux tokens de thème dans `styles/components/_trainer.scss`. À nettoyer dans
  `constants/activity.js` — pas dans un commit de fusion.
*/
const ACTIVITY_MODIFIERS = {
  LESSON_STARTED: 'lesson-started',
  LESSON_COMPLETED: 'lesson-completed',
  EXERCISE_SUBMITTED: 'exercise-submitted',
  QUIZ_COMPLETED: 'quiz-completed',
  CHAPTER_UNLOCKED: 'chapter-unlocked',
  BADGE_EARNED: 'badge-earned'
};

const RecentActivity = ({ activities }) => {
  const cardClass = (activityType) => {
    const modifier = ACTIVITY_MODIFIERS[activityType];
    return modifier ? `activity-card activity-card--${modifier}` : 'activity-card';
  };

  return (
    <div className="trainer-panel">
      <div className="trainer-panel__header">
        <h2 className="trainer-panel__title">Activité récente</h2>
      </div>
      <div className="trainer-panel__body">
        <div className="activity-feed trainer-panel__scroll trainer-panel__scroll--tall">
          {activities.map((activity) => {
            const { icon, label } = describeActivity(activity);
            return (
              <div key={activity.id} className={cardClass(activity.activity_type)}>
                <span className="activity-card__icon" aria-hidden="true">{icon}</span>
                <div className="activity-card__body">
                  <div>
                    <p className="activity-card__user">{activity.user_full_name}</p>
                    {/* Le libellé porte déjà le titre de la leçon ou du
                        chapitre : l'afficher à nouveau ferait doublon. */}
                    <p className="activity-card__type">{label}</p>
                  </div>
                  <span className="activity-card__date">
                    {new Date(activity.created_at).toLocaleString('fr-FR', {
                      day: '2-digit',
                      month: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            );
          })}

          {activities.length === 0 && <p className="trainer-empty">Aucune activité récente</p>}
        </div>
      </div>
    </div>
  );
};

RecentActivity.propTypes = {
  activities: PropTypes.array.isRequired
};

export default RecentActivity;
