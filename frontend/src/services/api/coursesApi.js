import apiClient from './apiService';

/**
 * Courses API service
 */
const coursesApi = {
  // Chapters
  getChapters: () => apiClient.get('/courses/chapters/'),
  getChapter: (slug) => apiClient.get(`/courses/chapters/${slug}/`),

  // Lessons
  getLessons: (params) => apiClient.get('/courses/lessons/', { params }),
  getLesson: (slug) => apiClient.get(`/courses/lessons/${slug}/`),

  // Exercises
  getExercise: (id) => apiClient.get(`/courses/exercises/${id}/`),

  // Quizzes
  getQuiz: (id) => apiClient.get(`/courses/quizzes/${id}/`),

  // Projects
  getProjects: (params) => apiClient.get('/courses/projects/', { params }),
  getProject: (slug) => apiClient.get(`/courses/projects/${slug}/`),
};

export default coursesApi;
