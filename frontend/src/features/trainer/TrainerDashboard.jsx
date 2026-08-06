import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchLearnersSummary, fetchRecentActivity } from './trainerSlice';
import LearnersList from './LearnersList';
import LearnerDetail from './LearnerDetail';
import CohortsPanel from '@/features/cohorts/CohortsPanel';
import RecentActivity from './RecentActivity';

const TrainerDashboard = () => {
  const dispatch = useDispatch();
  const { learnersSummary, recentActivity, loading, error } = useSelector((state) => state.trainer);
  const [selectedLearnerId, setSelectedLearnerId] = useState(null);
  const [activeTab, setActiveTab] = useState('learners'); // 'learners' or 'activity'

  useEffect(() => {
    dispatch(fetchLearnersSummary());
    dispatch(fetchRecentActivity(50));
  }, [dispatch]);

  if (loading && !learnersSummary.length) {
    return (
      <div className="trainer">
        <div className="trainer__loading">
          <div className="loading-spinner"></div>
          <p>Chargement…</p>
        </div>
      </div>
    );
  }

  if (error) {
    // DRF renvoie souvent un objet ({detail: "..."}). Rendre un objet
    // directement fait planter React — d'où l'aplatissement en texte.
    const message =
      typeof error === 'string' ? error : error?.detail || JSON.stringify(error);
    return (
      <div className="trainer">
        <div className="trainer__error" role="alert">
          Erreur : {message}
        </div>
      </div>
    );
  }

  const averageCompletion =
    learnersSummary.length > 0
      ? Math.round(
          learnersSummary.reduce(
            (acc, learner) =>
              acc +
              (learner.total_lessons > 0
                ? (learner.completed_lessons / learner.total_lessons) * 100
                : 0),
            0
          ) / learnersSummary.length
        )
      : 0;

  return (
    <div className="trainer">
      <div className="trainer__hero">
        <div className="trainer__hero-content">
          <h1 className="trainer__title">Espace formateur</h1>
          <p className="trainer__subtitle">
            Suivez la progression de vos apprenants et ouvrez-leur les chapitres.
          </p>
        </div>
      </div>

      <div className="trainer__container">
        <div className="trainer-stats">
          <div className="trainer-stat trainer-stat--learners">
            <span className="trainer-stat__label">Total apprenants</span>
            <span className="trainer-stat__value">{learnersSummary.length}</span>
          </div>
          <div className="trainer-stat trainer-stat--activity">
            <span className="trainer-stat__label">Activités récentes</span>
            <span className="trainer-stat__value">{recentActivity.length}</span>
          </div>
          <div className="trainer-stat trainer-stat--completion">
            <span className="trainer-stat__label">Taux de complétion moyen</span>
            <span className="trainer-stat__value">{averageCompletion} %</span>
          </div>
        </div>

        <div className="trainer__tabs">
          <button
            type="button"
            onClick={() => setActiveTab('learners')}
            className={`trainer-tab${activeTab === 'learners' ? ' trainer-tab--active' : ''}`}
            aria-pressed={activeTab === 'learners'}
          >
            Apprenants ({learnersSummary.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('activity')}
            className={`trainer-tab${activeTab === 'activity' ? ' trainer-tab--active' : ''}`}
            aria-pressed={activeTab === 'activity'}
          >
            Activité récente
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('cohorts')}
            className={`trainer-tab${activeTab === 'cohorts' ? ' trainer-tab--active' : ''}`}
            aria-pressed={activeTab === 'cohorts'}
          >
            Mes classes
          </button>
        </div>

        {activeTab === 'learners' && (
          <div className="trainer__split">
            <LearnersList
              learners={learnersSummary}
              selectedLearnerId={selectedLearnerId}
              onSelectLearner={setSelectedLearnerId}
            />
            {selectedLearnerId ? (
              <LearnerDetail learnerId={selectedLearnerId} />
            ) : (
              <div className="trainer__placeholder">
                <p>Sélectionnez un apprenant pour voir ses détails</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'activity' && <RecentActivity activities={recentActivity} />}

        {activeTab === 'cohorts' && <CohortsPanel />}
      </div>
    </div>
  );
};

export default TrainerDashboard;
