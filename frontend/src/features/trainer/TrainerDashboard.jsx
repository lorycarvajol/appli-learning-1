import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchLearnersSummary, fetchRecentActivity } from './trainerSlice';
import LearnersList from './LearnersList';
import LearnerDetail from './LearnerDetail';
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
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Erreur : {error}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard Trainer</h1>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Total Apprenants</h3>
          <p className="text-3xl font-bold text-blue-600">{learnersSummary.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Activités Récentes</h3>
          <p className="text-3xl font-bold text-green-600">{recentActivity.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Taux de Complétion Moyen</h3>
          <p className="text-3xl font-bold text-purple-600">
            {learnersSummary.length > 0
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
              : 0}
            %
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('learners')}
              className={`${
                activeTab === 'learners'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Apprenants ({learnersSummary.length})
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`${
                activeTab === 'activity'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Activité Récente
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'learners' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <LearnersList
              learners={learnersSummary}
              selectedLearnerId={selectedLearnerId}
              onSelectLearner={setSelectedLearnerId}
            />
          </div>
          <div>
            {selectedLearnerId ? (
              <LearnerDetail learnerId={selectedLearnerId} />
            ) : (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">
                  Sélectionnez un apprenant pour voir ses détails
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'activity' && <RecentActivity activities={recentActivity} />}
    </div>
  );
};

export default TrainerDashboard;
