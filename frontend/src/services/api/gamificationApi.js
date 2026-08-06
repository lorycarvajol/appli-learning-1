import apiService from './apiService';

/**
 * API de gamification : badges, points, série de jours.
 *
 * Les objectifs secrets non débloqués arrivent déjà masqués depuis le
 * serveur (nom générique + énigme) : rien à filtrer côté client.
 */
const gamificationApi = {
  // Catalogue complet, du point de vue de l'utilisateur connecté
  getBadges: async () => {
    const response = await apiService.get('/gamification/badges/');
    return response.data;
  },

  getMyBadges: async () => {
    const response = await apiService.get('/gamification/badges/mine/');
    return response.data;
  },

  // Accuse réception d'une révélation : l'animation ne rejoue pas au reload
  markBadgesSeen: async (badgeIds) => {
    const response = await apiService.post('/gamification/badges/mark_seen/', {
      badge_ids: badgeIds || [],
    });
    return response.data;
  },

  // Points, niveau, série, prochains objectifs, révélations en attente
  getSummary: async () => {
    const response = await apiService.get('/gamification/summary/');
    return response.data;
  },

  // Resynchronisation (idempotente côté serveur) : filet de sécurité
  sync: async () => {
    const response = await apiService.post('/gamification/summary/sync/');
    return response.data;
  },

  getPointHistory: async () => {
    const response = await apiService.get('/gamification/points/');
    return response.data;
  },

  // Classement. `scope` vaut 'global' ou 'cohort' (sa classe). Les noms
  // arrivent déjà réduits à « Prénom N. » et aucun email n'est transmis :
  // rien à masquer côté client.
  getLeaderboard: async ({ scope = 'global', limit } = {}) => {
    const response = await apiService.get('/gamification/leaderboard/', {
      params: limit ? { scope, limit } : { scope },
    });
    return response.data;
  },
};

export default gamificationApi;
