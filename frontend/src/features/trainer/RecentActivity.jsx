import PropTypes from 'prop-types';

const ACTIVITY_ICONS = {
  LESSON_STARTED: '▶️',
  LESSON_COMPLETED: '✅',
  EXERCISE_SUBMITTED: '💻',
  QUIZ_COMPLETED: '📝',
  CHAPTER_UNLOCKED: '🔓',
  BADGE_EARNED: '🏆'
};

// Le type d'activité choisit un modificateur BEM ; les teintes elles-mêmes
// vivent dans styles/components/_trainer.scss, adossées aux tokens de thème.
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
          {activities.map((activity) => (
            <div key={activity.id} className={cardClass(activity.activity_type)}>
              <span className="activity-card__icon" aria-hidden="true">
                {ACTIVITY_ICONS[activity.activity_type] || '📌'}
              </span>
              <div className="activity-card__body">
                <div>
                  <p className="activity-card__user">{activity.user_full_name}</p>
                  <p className="activity-card__type">
                    {activity.activity_type.replace('_', ' ').toLowerCase()}
                  </p>
                  {activity.lesson_title && (
                    <p className="activity-card__context">📖 {activity.lesson_title}</p>
                  )}
                  {activity.chapter_title && !activity.lesson_title && (
                    <p className="activity-card__context">📚 {activity.chapter_title}</p>
                  )}
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
          ))}

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
