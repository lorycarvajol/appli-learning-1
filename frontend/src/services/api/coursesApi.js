import apiClient from './apiService';

/**
 * Service des cours (chapitres, leçons, exercices, quiz, projets).
 *
 * Contrat uniforme avec les autres services : **chaque méthode renvoie les
 * données déjà déballées** (`response.data`), jamais la réponse axios brute.
 * Ne pas refaire `.data` dans les appelants. Verrouillé par `contract.test.js`.
 */
const coursesApi = {
  // Chapters
  getChapters: async () => (await apiClient.get('/courses/chapters/')).data,
  getChapter: async (slug) => (await apiClient.get(`/courses/chapters/${slug}/`)).data,

  // Lessons
  getLessons: async (params) => (await apiClient.get('/courses/lessons/', { params })).data,
  getLesson: async (slug) => (await apiClient.get(`/courses/lessons/${slug}/`)).data,

  // Exercises
  getExercise: async (id) => (await apiClient.get(`/courses/exercises/${id}/`)).data,

  // Quizzes
  getQuiz: async (id) => (await apiClient.get(`/courses/quizzes/${id}/`)).data,

  // Projects
  getProjects: async (params) => (await apiClient.get('/courses/projects/', { params })).data,
  getProject: async (slug) => (await apiClient.get(`/courses/projects/${slug}/`)).data,
};

export default coursesApi;
