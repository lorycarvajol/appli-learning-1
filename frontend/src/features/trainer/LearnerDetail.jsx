import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import PropTypes from 'prop-types';
import { fetchLearnerDetail, unlockChapter, lockChapter, fetchLearnersSummary } from './trainerSlice';
import { describeActivity } from '@/constants/activity';

const LearnerDetail = ({ learnerId }) => {
  const dispatch = useDispatch();
  const { selectedLearner, loading, unlockLoading } = useSelector((state) => state.trainer);
  const [processingChapter, setProcessingChapter] = useState(null);

  useEffect(() => {
    if (learnerId) {
      dispatch(fetchLearnerDetail(learnerId));
    }
  }, [dispatch, learnerId]);

  const handleToggleChapter = async (chapterId, isUnlocked) => {
    setProcessingChapter(chapterId);
    try {
      if (isUnlocked) {
        await dispatch(lockChapter({ userId: learnerId, chapterId })).unwrap();
      } else {
        await dispatch(unlockChapter({ userId: learnerId, chapterId })).unwrap();
      }
      // Refresh learner detail and summary
      await dispatch(fetchLearnerDetail(learnerId));
      await dispatch(fetchLearnersSummary());
    } catch (error) {
      console.error('Error toggling chapter:', error);
    } finally {
      setProcessingChapter(null);
    }
  };

  if (loading && !selectedLearner) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="text-center text-gray-600">Chargement...</div>
      </div>
    );
  }

  if (!selectedLearner) {
    return null;
  }

  const learner = selectedLearner.learner;

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold">
          {learner.first_name} {learner.last_name}
        </h2>
        <p className="text-sm text-gray-500">{learner.email}</p>
        <div className="mt-2 flex items-center space-x-4 text-sm">
          <span className="text-blue-600">⭐ Niveau {learner.profile.level}</span>
          <span className="text-purple-600">🏆 {learner.profile.points} points</span>
        </div>
      </div>

      <div className="p-4 max-h-[550px] overflow-y-auto">
        <h3 className="font-semibold mb-4">Progression par Chapitre</h3>

        <div className="space-y-4">
          {selectedLearner.chapter_progress.map((chapter) => (
            <div key={chapter.chapter_id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{chapter.chapter_title}</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {chapter.completed_lessons}/{chapter.total_lessons} leçons complétées
                  </p>
                </div>
                <button
                  onClick={() => handleToggleChapter(chapter.chapter_id, chapter.is_unlocked)}
                  disabled={unlockLoading && processingChapter === chapter.chapter_id}
                  className={`${
                    chapter.is_unlocked
                      ? 'bg-green-500 hover:bg-green-600'
                      : 'bg-gray-400 hover:bg-gray-500'
                  } text-white px-4 py-2 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {unlockLoading && processingChapter === chapter.chapter_id ? (
                    <span className="flex items-center">
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      ...
                    </span>
                  ) : chapter.is_unlocked ? (
                    '🔓 Débloqué'
                  ) : (
                    '🔒 Verrouillé'
                  )}
                </button>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${chapter.completion_rate}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">{Math.round(chapter.completion_rate)}% complété</p>
            </div>
          ))}

          {selectedLearner.chapter_progress.length === 0 && (
            <p className="text-center text-gray-500 py-8">Aucun chapitre disponible</p>
          )}
        </div>

        {/* Recent Activity */}
        {selectedLearner.recent_activities.length > 0 && (
          <div className="mt-6">
            <h3 className="font-semibold mb-3">Activité Récente</h3>
            <div className="space-y-2">
              {selectedLearner.recent_activities.slice(0, 5).map((activity) => {
                const { icon, label } = describeActivity(activity);
                return (
                  <div
                    key={activity.id}
                    className="flex items-start space-x-3 text-sm p-2 bg-gray-50 rounded"
                  >
                    <span className="text-gray-500">{icon}</span>
                    <div className="flex-1">
                      <p className="text-gray-900">{label}</p>
                      <p className="text-gray-500 text-xs">
                        {new Date(activity.created_at).toLocaleString('fr-FR')}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

LearnerDetail.propTypes = {
  learnerId: PropTypes.string.isRequired
};

export default LearnerDetail;
