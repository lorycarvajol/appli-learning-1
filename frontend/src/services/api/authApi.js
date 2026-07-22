import apiClient from './apiService'

/**
 * Service d'authentification et de compte.
 *
 * Contrat uniforme avec les autres services : **chaque méthode renvoie les
 * données déjà déballées** (`response.data`), jamais la réponse axios brute.
 * Ne pas refaire `.data` dans les appelants. Verrouillé par `contract.test.js`.
 */
export const authApi = {
  login: async (email, password) =>
    (await apiClient.post('/auth/login/', { email, password })).data,

  register: async (userData) =>
    (await apiClient.post('/auth/register/', userData)).data,

  getCurrentUser: async () =>
    (await apiClient.get('/auth/me/')).data,

  /**
   * Met à jour le compte et, si `payload.profile` est fourni, le profil.
   * L'écriture est imbriquée pour rester atomique : un formulaire de profil
   * qui réussirait à moitié laisserait l'utilisateur devant un état incohérent.
   */
  updateProfile: async (payload) =>
    (await apiClient.patch('/auth/me/', payload)).data,

  getAvatarCatalog: async () =>
    (await apiClient.get('/auth/avatars/')).data,

  refreshToken: async (refreshToken) =>
    (await apiClient.post('/auth/token/refresh/', { refresh: refreshToken })).data,

  logout: async (refreshToken) =>
    (await apiClient.post('/auth/logout/', { refresh: refreshToken })).data,

  // Mot de passe oublié (routes publiques)
  requestPasswordReset: async (email) =>
    (await apiClient.post('/auth/password-reset/', { email })).data,

  validateResetLink: async (uid, token) =>
    (await apiClient.get('/auth/password-reset/validate/', { params: { uid, token } })).data,

  confirmPasswordReset: async (uid, token, newPassword, newPasswordConfirm) =>
    (await apiClient.post('/auth/password-reset/confirm/', {
      uid,
      token,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })).data,

  changePassword: async (oldPassword, newPassword, newPasswordConfirm) =>
    (await apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })).data,

  // RGPD (routes authentifiées, agissent sur le compte courant)
  exportMyData: async () =>
    (await apiClient.get('/auth/export/')).data,

  deleteMyAccount: async (password) =>
    (await apiClient.post('/auth/delete-account/', { password })).data,
}
