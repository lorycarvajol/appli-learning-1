import PropTypes from 'prop-types';

const RecentActivity = ({ activities }) => {
  const getActivityIcon = (activityType) => {
    const icons = {
      LESSON_STARTED: '▶️',
      LESSON_COMPLETED: '✅',
      EXERCISE_SUBMITTED: '💻',
      QUIZ_COMPLETED: '📝',
      CHAPTER_UNLOCKED: '🔓',
      BADGE_EARNED: '🏆'
    };
    return icons[activityType] || '📌';
  };

  const getActivityColor = (activityType) => {
    const colors = {
      LESSON_STARTED: 'bg-blue-50 border-blue-200',
      LESSON_COMPLETED: 'bg-green-50 border-green-200',
      EXERCISE_SUBMITTED: 'bg-purple-50 border-purple-200',
      QUIZ_COMPLETED: 'bg-yellow-50 border-yellow-200',
      CHAPTER_UNLOCKED: 'bg-indigo-50 border-indigo-200',
      BADGE_EARNED: 'bg-pink-50 border-pink-200'
    };
    return colors[activityType] || 'bg-gray-50 border-gray-200';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold">Activité Récente</h2>
      </div>
      <div className="p-4">
        <div className="space-y-3 max-h-[700px] overflow-y-auto">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className={`border rounded-lg p-4 ${getActivityColor(activity.activity_type)}`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{getActivityIcon(activity.activity_type)}</span>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{activity.user_full_name}</p>
                      <p className="text-sm text-gray-600">
                        {activity.activity_type.replace('_', ' ').toLowerCase()}
                      </p>
                      {activity.lesson_title && (
                        <p className="text-sm text-gray-700 mt-1">
                          📖 {activity.lesson_title}
                        </p>
                      )}
                      {activity.chapter_title && !activity.lesson_title && (
                        <p className="text-sm text-gray-700 mt-1">
                          📚 {activity.chapter_title}
                        </p>
                      )}
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
          ))}

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
