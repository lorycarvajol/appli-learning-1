/**
 * Service API pour la validation de code
 *
 * La validation s'exécute de façon asynchrone côté serveur (worker Celery
 * dédié) : submitCode renvoie immédiatement un task_id, puis pollTaskResult
 * interroge périodiquement le résultat jusqu'à ce qu'il soit disponible.
 */

import apiService from './apiService';

const POLL_INTERVAL_MS = 1000;
const MAX_POLL_ATTEMPTS = 30; // ~30s, cohérent avec le timeout du sandbox (5s) + marge

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const validationApi = {
  /**
   * Soumet du code pour validation.
   *
   * @param {string} exerciseId - ID de l'exercice
   * @param {string} code - Code à valider
   * @returns {Promise<{task_id: string}>}
   */
  submitCode: async (exerciseId, code) => {
    try {
      const response = await apiService.post(
        `/validation/exercises/${exerciseId}/submit/`,
        { code }
      );
      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        'Une erreur est survenue lors de la validation';

      throw new Error(errorMessage);
    }
  },

  /**
   * Interroge une fois le résultat d'une tâche de validation.
   *
   * @param {string} taskId
   * @returns {Promise<{done: boolean, result: object|null}>}
   */
  getTaskResult: async (taskId) => {
    const response = await apiService.get(`/validation/tasks/${taskId}/`);
    if (response.status === 202) {
      return { done: false, result: null };
    }
    return { done: true, result: response.data };
  },

  /**
   * Soumet du code puis attend le résultat en interrogeant le serveur
   * à intervalle régulier.
   *
   * @param {string} exerciseId
   * @param {string} code
   * @returns {Promise<object>} Résultat final de la validation
   */
  submitCodeAndWait: async (exerciseId, code) => {
    const { task_id: taskId } = await validationApi.submitCode(exerciseId, code);

    for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt++) {
      await sleep(POLL_INTERVAL_MS);
      try {
        const { done, result } = await validationApi.getTaskResult(taskId);
        if (done) {
          return result;
        }
      } catch (error) {
        const errorMessage =
          error.response?.data?.error ||
          error.response?.data?.message ||
          error.message ||
          'Une erreur est survenue lors de la validation';
        throw new Error(errorMessage);
      }
    }

    throw new Error(
      "La validation prend plus de temps que prévu. Réessayez dans quelques instants."
    );
  },
};

export default validationApi;
