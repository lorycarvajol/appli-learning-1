import apiService from './apiService'

/**
 * API de l'espace administration (réservée au rôle ADMIN).
 *
 * Complémentaire de l'admin Django, pas concurrente : le CRUD de contenu
 * (chapitres, leçons, badges) reste sur /admin/, qui le fait mieux.
 *
 * Comme `progressionApi`, ces méthodes renvoient les données **déjà
 * déballées** — ne pas refaire `.data` dans les appelants.
 */
const administrationApi = {
  getOverview: async () => {
    const response = await apiService.get('/administration/overview/')
    return response.data
  },

  getTrainers: async () => {
    const response = await apiService.get('/administration/trainers/')
    return response.data
  },

  getUsers: async (params = {}) => {
    const response = await apiService.get('/administration/users/', { params })
    return response.data.results ?? response.data
  },

  assignCohort: async (userId, cohortId) => {
    const response = await apiService.post(
      `/administration/users/${userId}/assign_cohort/`,
      { cohort_id: cohortId }
    )
    return response.data
  },

  setRole: async (userId, role) => {
    const response = await apiService.post(
      `/administration/users/${userId}/set_role/`,
      { role }
    )
    return response.data
  },

  setActive: async (userId, isActive) => {
    const response = await apiService.post(
      `/administration/users/${userId}/set_active/`,
      { is_active: isActive }
    )
    return response.data
  },

  anonymize: async (userId) => {
    const response = await apiService.post(
      `/administration/users/${userId}/anonymize/`,
      {}
    )
    return response.data
  },
}

export default administrationApi
