import PropTypes from 'prop-types';
import { describeActivity } from '@/constants/activity';

const RecentActivity = ({ activities }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold">Activité Récente</h2>
      </div>
      <div className="p-4">
        <div className="space-y-3 max-h-[700px] overflow-y-auto">
          {activities.map((activity) => {
            const { icon, color, label } = describeActivity(activity);
            return (
              <div
                key={activity.id}
                className={`border rounded-lg p-4 ${color}`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{icon}</span>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{activity.user_full_name}</p>
                        {/* Le libellé porte déjà le titre de la leçon ou du
                            chapitre : l'afficher à nouveau ferait doublon. */}
                        <p className="text-sm text-gray-600">{label}</p>
                      </div>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {new Date(activity.created_at).toLocaleString('fr-FR', {
                          day: '2-digit',
                          month: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {activities.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              Aucune activité récente
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

RecentActivity.propTypes = {
  activities: PropTypes.array.isRequired
};

export default RecentActivity;
