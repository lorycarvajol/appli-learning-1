import apiClient from './apiService'

export const authApi = {
  login: (email, password) =>
    apiClient.post('/auth/login/', { email, password }),

  register: (userData) =>
    apiClient.post('/auth/register/', userData),

  getCurrentUser: () =>
    apiClient.get('/auth/me/'),

  refreshToken: (refreshToken) =>
    apiClient.post('/auth/token/refresh/', { refresh: refreshToken }),

  logout: (refreshToken) =>
    apiClient.post('/auth/logout/', { refresh: refreshToken }),

  changePassword: (oldPassword, newPassword, newPasswordConfirm) =>
    apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    }),
}
