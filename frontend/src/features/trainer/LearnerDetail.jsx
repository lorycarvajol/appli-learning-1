import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import PropTypes from 'prop-types';
import { fetchLearnerDetail, unlockChapter, lockChapter, fetchLearnersSummary } from './trainerSlice';

const ACTIVITY_ICONS = {
  LESSON_STARTED: '▶️',
  LESSON_COMPLETED: '✅',
  EXERCISE_SUBMITTED: '💻',
  QUIZ_COMPLETED: '📝',
  CHAPTER_UNLOCKED: '🔓',
  BADGE_EARNED: '🏆'
};

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
      <div className="trainer-panel">
        <div className="trainer-panel__body">
          <p className="trainer-empty">Chargement…</p>
        </div>
      </div>
    );
  }

  if (!selectedLearner) {
    return null;
  }

  const learner = selectedLearner.learner;

  return (
    <div className="trainer-panel">
      <div className="trainer-panel__header">
        <h2 className="trainer-panel__title">
          {learner.first_name} {learner.last_name}
        </h2>
        <p className="trainer-panel__subtitle">{learner.email}</p>
        <div className="learner-detail__meta">
          <span className="learner-detail__level">⭐ Niveau {learner.profile.level}</span>
          <span className="learner-detail__points">🏆 {learner.profile.points} points</span>
        </div>
      </div>

      <div className="trainer-panel__body trainer-panel__scroll">
        <h3 className="learner-detail__section-title">Progression par chapitre</h3>

        <div className="learner-detail__chapters">
          {selectedLearner.chapter_progress.map((chapter) => {
            const isProcessing = unlockLoading && processingChapter === chapter.chapter_id;

            return (
              <div key={chapter.chapter_id} className="chapter-progress">
                <div className="chapter-progress__head">
                  <div>
                    <h4 className="chapter-progress__title">{chapter.chapter_title}</h4>
                    <p className="chapter-progress__count">
                      {chapter.completed_lessons}/{chapter.total_lessons} leçons complétées
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleToggleChapter(chapter.chapter_id, chapter.is_unlocked)}
                    disabled={isProcessing}
                    className={`chapter-lock ${
                      chapter.is_unlocked ? 'chapter-lock--unlocked' : 'chapter-lock--locked'
                    }`}
                  >
                    {isProcessing ? (
                      <>
                        <span className="chapter-lock__spinner" aria-hidden="true" />
                        En cours…
                      </>
                    ) : chapter.is_unlocked ? (
                      '🔓 Débloqué'
                    ) : (
                      '🔒 Verrouillé'
                    )}
                  </button>
                </div>

                <div className="meter">
                  <div className="meter__track">
                    <div
                      className="meter__fill"
                      style={{ width: `${chapter.completion_rate}%` }}
                    />
                  </div>
                </div>
                <p className="chapter-progress__rate">
                  {Math.round(chapter.completion_rate)} % complété
                </p>
              </div>
            );
          })}

          {selectedLearner.chapter_progress.length === 0 && (
            <p className="trainer-empty">Aucun chapitre disponible</p>
          )}
        </div>

        {selectedLearner.recent_activities.length > 0 && (
          <div className="learner-detail__activities">
            <h3 className="learner-detail__section-title">Activité récente</h3>
            <div className="activity-mini">
              {selectedLearner.recent_activities.slice(0, 5).map((activity) => (
                <div key={activity.id} className="activity-mini__item">
                  <span aria-hidden="true">{ACTIVITY_ICONS[activity.activity_type]}</span>
                  <div>
                    <p className="activity-mini__label">
                      {activity.activity_type.replace('_', ' ').toLowerCase()}
                      {activity.lesson_title && `: ${activity.lesson_title}`}
                    </p>
                    <p className="activity-mini__date">
                      {new Date(activity.created_at).toLocaleString('fr-FR')}
                    </p>
                  </div>
                </div>
              ))}
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
