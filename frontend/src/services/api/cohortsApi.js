import apiService from './apiService'

/**
 * API des classes et invitations.
 *
 * Les routes `join/*` sont publiques : elles ne doivent jamais dépendre d'un
 * jeton d'authentification, sauf `attach` qui rattache une session existante.
 */
const cohortsApi = {
  // --- Parcours public d'invitation ---
  getInvite: async (token) => {
    const response = await apiService.get(`/cohorts/join/${token}/`)
    return response.data
  },

  /** Crée le compte et le rattache. Le rôle et la classe viennent du jeton. */
  registerWithInvite: async (token, payload) => {
    const response = await apiService.post(`/cohorts/join/${token}/register/`, payload)
    return response.data
  },

  /** Rattache un utilisateur déjà connecté. */
  attachToInvite: async (token) => {
    const response = await apiService.post(`/cohorts/join/${token}/attach/`, {})
    return response.data
  },

  // --- Espace formateur ---
  listCohorts: async () => {
    const response = await apiService.get('/cohorts/cohorts/')
    return response.data.results ?? response.data
  },

  createCohort: async (payload) => {
    const response = await apiService.post('/cohorts/cohorts/', payload)
    return response.data
  },

  getMembers: async (cohortId) => {
    const response = await apiService.get(`/cohorts/cohorts/${cohortId}/members/`)
    return response.data
  },

  removeMember: async (cohortId, userId) => {
    const response = await apiService.post(
      `/cohorts/cohorts/${cohortId}/remove_member/`,
      { user_id: userId }
    )
    return response.data
  },

  unlockChapterForCohort: async (cohortId, chapterId) => {
    const response = await apiService.post(
      `/cohorts/cohorts/${cohortId}/unlock_chapter/`,
      { chapter_id: chapterId }
    )
    return response.data
  },

  /** Ids des chapitres déjà ouverts à toute la classe (retour visuel). */
  getUnlockedChapters: async (cohortId) => {
    const response = await apiService.get(
      `/cohorts/cohorts/${cohortId}/unlocked_chapters/`
    )
    return response.data.chapter_ids ?? []
  },

  listInvites: async () => {
    const response = await apiService.get('/cohorts/invites/')
    return response.data.results ?? response.data
  },

  createInvite: async (payload) => {
    const response = await apiService.post('/cohorts/invites/', payload)
    return response.data
  },

  revokeInvite: async (inviteId) => {
    await apiService.delete(`/cohorts/invites/${inviteId}/`)
  },
}

export default cohortsApi
