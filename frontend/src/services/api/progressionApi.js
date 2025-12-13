import apiService from './apiService';

/**
 * API service for progression management
 */
const progressionApi = {
  // Chapter Access endpoints
  getMyAccess: () => apiService.get('/progression/chapter-access/my_access/'),

  unlockChapter: (userId, chapterId) =>
    apiService.post('/progression/chapter-access/unlock_chapter/', {
      user_id: userId,
      chapter_id: chapterId
    }),

  lockChapter: (userId, chapterId) =>
    apiService.post('/progression/chapter-access/lock_chapter/', {
      user_id: userId,
      chapter_id: chapterId
    }),

  // User Progress endpoints
  getMyProgress: () => apiService.get('/progression/progress/my_progress/'),

  getUserProgress: (userId) => apiService.get(`/progression/progress/?user_id=${userId}`),

  markLessonCompleted: (lessonId) =>
    apiService.post('/progression/progress/mark_completed/', {
      lesson_id: lessonId
    }),

  updateProgress: (progressId, data) =>
    apiService.patch(`/progression/progress/${progressId}/`, data),

  // Activity Log endpoints
  getMyActivity: () => apiService.get('/progression/activity/'),

  getUserActivity: (userId) => apiService.get(`/progression/activity/?user_id=${userId}`),

  // Trainer Dashboard endpoints
  getLearnersSummary: () =>
    apiService.get('/progression/trainer-dashboard/learners_summary/'),

  getRecentActivity: (limit = 50) =>
    apiService.get(`/progression/trainer-dashboard/recent_activity/?limit=${limit}`),

  getLearnerDetail: (learnerId) =>
    apiService.get(`/progression/trainer-dashboard/${learnerId}/learner_detail/`)
};

export default progressionApi;
