import apiService from './apiService';

/**
 * API service for progression management
 */
const progressionApi = {
  // Chapter Access endpoints
  getMyAccess: async () => {
    const response = await apiService.get('/progression/chapter-access/my_access/');
    return response.data;
  },

  unlockChapter: async (userId, chapterId) => {
    const response = await apiService.post('/progression/chapter-access/unlock_chapter/', {
      user_id: userId,
      chapter_id: chapterId
    });
    return response.data;
  },

  lockChapter: async (userId, chapterId) => {
    const response = await apiService.post('/progression/chapter-access/lock_chapter/', {
      user_id: userId,
      chapter_id: chapterId
    });
    return response.data;
  },

  // User Progress endpoints
  getMyProgress: async () => {
    const response = await apiService.get('/progression/progress/my_progress/');
    return response.data;
  },

  getUserProgress: async (userId) => {
    const response = await apiService.get(`/progression/progress/?user_id=${userId}`);
    return response.data;
  },

  markLessonCompleted: async (lessonId) => {
    const response = await apiService.post('/progression/progress/mark_completed/', {
      lesson_id: lessonId
    });
    return response.data;
  },

  // Quiz : sauvegarde progressive (aucune notation) + soumission notée côté serveur
  saveQuizProgress: async (lessonId, answers) => {
    const response = await apiService.post('/progression/progress/save_quiz_progress/', {
      lesson_id: lessonId,
      answers,
    });
    return response.data;
  },

  submitQuiz: async (lessonId, answers) => {
    const response = await apiService.post('/progression/progress/submit_quiz/', {
      lesson_id: lessonId,
      answers,
    });
    return response.data;
  },

  updateProgress: async (progressId, data) => {
    const response = await apiService.patch(`/progression/progress/${progressId}/`, data);
    return response.data;
  },

  // Activity Log endpoints
  getMyActivity: async () => {
    const response = await apiService.get('/progression/activity/');
    return response.data;
  },

  getUserActivity: async (userId) => {
    const response = await apiService.get(`/progression/activity/?user_id=${userId}`);
    return response.data;
  },

  // Trainer Dashboard endpoints
  getLearnersSummary: async () => {
    const response = await apiService.get('/progression/trainer-dashboard/learners_summary/');
    return response.data;
  },

  getRecentActivity: async (limit = 50) => {
    const response = await apiService.get(`/progression/trainer-dashboard/recent_activity/?limit=${limit}`);
    return response.data;
  },

  getLearnerDetail: async (learnerId) => {
    const response = await apiService.get(`/progression/trainer-dashboard/${learnerId}/learner_detail/`);
    return response.data;
  }
};

export default progressionApi;
