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

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold">Liste des Apprenants</h2>
      </div>
      <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
        {learners.map((learner) => (
          <div
            key={learner.user.id}
            onClick={() => onSelectLearner(learner.user.id)}
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedLearnerId === learner.user.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">
                  {learner.user.first_name} {learner.user.last_name}
                </h3>
                <p className="text-sm text-gray-500">{learner.user.email}</p>

                {/* Progress bars */}
                <div className="mt-3 space-y-2">
                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Chapitres débloqués</span>
                      <span>
                        {learner.unlocked_chapters}/{learner.total_chapters}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{
                          width: `${
                            learner.total_chapters > 0
                              ? (learner.unlocked_chapters / learner.total_chapters) * 100
                              : 0
                          }%`
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Leçons complétées</span>
                      <span>
                        {learner.completed_lessons}/{learner.total_lessons}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full transition-all"
                        style={{
                          width: `${
                            learner.total_lessons > 0
                              ? (learner.completed_lessons / learner.total_lessons) * 100
                              : 0
                          }%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                  <span>⏱️ {formatTime(learner.total_time_spent)}</span>
                  {learner.average_score && (
                    <span>📊 Moy: {Math.round(learner.average_score)}%</span>
                  )}
                </div>

                {learner.current_lesson && (
                  <div className="mt-2 text-xs text-blue-600">
                    📖 En cours: {learner.current_lesson}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {learners.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            Aucun apprenant inscrit pour le moment
          </div>
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
