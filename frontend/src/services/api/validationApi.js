/**
 * Service API pour la validation de code
 */

import apiService from './apiService';

const validationApi = {
  /**
   * Soumet du code pour validation
   *
   * @param {string} exerciseId - ID de l'exercice
   * @param {string} code - Code à valider
   * @returns {Promise} Résultats de la validation
   */
  submitCode: async (exerciseId, code) => {
    try {
      const response = await apiService.post(
        `/validation/exercises/${exerciseId}/submit/`,
        { code }
      );
      return response.data;
    } catch (error) {
      // Extraire le message d'erreur
      const errorMessage =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        'Une erreur est survenue lors de la validation';

      throw new Error(errorMessage);
    }
  },
};

export default validationApi;
