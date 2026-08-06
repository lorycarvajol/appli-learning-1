import PropTypes from 'prop-types';

const LearnersList = ({ learners, selectedLearnerId, onSelectLearner }) => {
  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}min`;
    }
    return `${minutes}min`;
  };

  const ratio = (part, total) => (total > 0 ? (part / total) * 100 : 0);

  return (
    <div className="trainer-panel">
      <div className="trainer-panel__header">
        <h2 className="trainer-panel__title">Liste des apprenants</h2>
      </div>
      <div className="trainer-panel__scroll">
        {learners.map((learner) => (
          <button
            type="button"
            key={learner.user.id}
            onClick={() => onSelectLearner(learner.user.id)}
            aria-pressed={selectedLearnerId === learner.user.id}
            className={`learner-row${
              selectedLearnerId === learner.user.id ? ' learner-row--selected' : ''
            }`}
          >
            <span className="learner-row__name">
              {learner.user.first_name} {learner.user.last_name}
            </span>
            <span className="learner-row__email">{learner.user.email}</span>

            <span className="learner-row__meters">
              <span className="meter">
                <span className="meter__head">
                  <span>Chapitres débloqués</span>
                  <span>
                    {learner.unlocked_chapters}/{learner.total_chapters}
                  </span>
                </span>
                <span className="meter__track">
                  <span
                    className="meter__fill"
                    style={{
                      width: `${ratio(learner.unlocked_chapters, learner.total_chapters)}%`
                    }}
                  />
                </span>
              </span>

              <span className="meter">
                <span className="meter__head">
                  <span>Leçons complétées</span>
                  <span>
                    {learner.completed_lessons}/{learner.total_lessons}
                  </span>
                </span>
                <span className="meter__track">
                  <span
                    className="meter__fill meter__fill--lessons"
                    style={{
                      width: `${ratio(learner.completed_lessons, learner.total_lessons)}%`
                    }}
                  />
                </span>
              </span>
            </span>

            <span className="learner-row__stats">
              <span>⏱️ {formatTime(learner.total_time_spent)}</span>
              {learner.average_score && (
                <span>📊 Moy : {Math.round(learner.average_score)} %</span>
              )}
            </span>

            {learner.current_lesson && (
              <span className="learner-row__current">
                📖 En cours : {learner.current_lesson}
              </span>
            )}
          </button>
        ))}

        {learners.length === 0 && (
          <p className="trainer-empty">Aucun apprenant inscrit pour le moment</p>
        )}
      </div>
    </div>
  );
};

LearnersList.propTypes = {
  learners: PropTypes.array.isRequired,
  selectedLearnerId: PropTypes.string,
  onSelectLearner: PropTypes.func.isRequired
};

export default LearnersList;
