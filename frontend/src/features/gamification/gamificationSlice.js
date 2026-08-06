import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import gamificationApi from '@/services/api/gamificationApi';
import { markLessonCompleted } from '@/features/progression/progressionSlice';

/**
 * État gamifié : points, niveau, série, badges et file de révélation.
 *
 * La file de révélation (`revealQueue`) est dédupliquée par id : un badge ne
 * peut pas être célébré deux fois dans une même session, même si plusieurs
 * réponses d'API le mentionnent. Côté serveur, `mark_seen` verrouille ensuite
 * la révélation pour de bon.
 */

export const fetchGamificationSummary = createAsyncThunk(
  'gamification/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      return await gamificationApi.getSummary();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchBadges = createAsyncThunk(
  'gamification/fetchBadges',
  async (_, { rejectWithValue }) => {
    try {
      return await gamificationApi.getBadges();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

/** Resynchronise côté serveur (idempotent) et récupère les badges manqués. */
export const syncGamification = createAsyncThunk(
  'gamification/sync',
  async (_, { rejectWithValue }) => {
    try {
      return await gamificationApi.sync();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Classement, par portée ('global' ou 'cohort').
 *
 * Les deux portées sont conservées côté store sous leur propre clé : basculer
 * de l'une à l'autre ne doit pas vider l'écran le temps d'un aller-retour
 * réseau, sinon la bascule clignote.
 */
export const fetchLeaderboard = createAsyncThunk(
  'gamification/fetchLeaderboard',
  async ({ scope = 'global', limit } = {}, { rejectWithValue }) => {
    try {
      return await gamificationApi.getLeaderboard({ scope, limit });
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

/** Acquitte les révélations affichées pour qu'elles ne rejouent pas. */
export const acknowledgeBadges = createAsyncThunk(
  'gamification/acknowledge',
  async (badgeIds, { rejectWithValue }) => {
    try {
      await gamificationApi.markBadgesSeen(badgeIds);
      return badgeIds;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  summary: null,
  badges: [],
  badgeStats: { earned_count: 0, total_count: 0, secret_total: 0, secret_found: 0 },
  revealQueue: [],
  celebrated: [], // ids déjà passés dans la file, pour ne jamais les rejouer
  // Une entrée par portée : la bascule global ↔ classe n'efface pas ce qui
  // était déjà affiché.
  leaderboards: {},
  leaderboardLoading: false,
  loading: false,
  badgesLoading: false,
  error: null,
};

/** Ajoute des badges à la file sans jamais en célébrer un deux fois. */
function enqueue(state, badges) {
  if (!Array.isArray(badges)) return;
  badges.forEach((badge) => {
    if (!badge?.id) return;
    if (state.celebrated.includes(badge.id)) return;
    state.celebrated.push(badge.id);
    state.revealQueue.push(badge);
  });
}

const gamificationSlice = createSlice({
  name: 'gamification',
  initialState,
  reducers: {
    /** À appeler avec le `new_badges` renvoyé par une action (quiz, leçon…). */
    badgesEarned: (state, action) => {
      enqueue(state, action.payload);
    },
    /** Retire le badge en tête de file une fois son animation terminée. */
    dismissReveal: (state) => {
      state.revealQueue.shift();
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    const applySummary = (state, action) => {
      state.loading = false;
      state.summary = action.payload;
      enqueue(state, action.payload.unseen_badges);
      enqueue(state, action.payload.newly_earned);
    };

    builder
      .addCase(fetchGamificationSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGamificationSummary.fulfilled, applySummary)
      .addCase(fetchGamificationSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(syncGamification.fulfilled, applySummary)

      // Terminer une leçon peut débloquer des badges : le serveur les renvoie
      // dans la même réponse, on les met directement en file de révélation.
      .addCase(markLessonCompleted.fulfilled, (state, action) => {
        enqueue(state, action.payload.new_badges);
      })

      .addCase(fetchBadges.pending, (state) => {
        state.badgesLoading = true;
      })
      .addCase(fetchBadges.fulfilled, (state, action) => {
        state.badgesLoading = false;
        state.badges = action.payload.badges;
        state.badgeStats = {
          earned_count: action.payload.earned_count,
          total_count: action.payload.total_count,
          secret_total: action.payload.secret_total,
          secret_found: action.payload.secret_found,
        };
      })
      .addCase(fetchBadges.rejected, (state, action) => {
        state.badgesLoading = false;
        state.error = action.payload;
      })

      .addCase(fetchLeaderboard.pending, (state) => {
        state.leaderboardLoading = true;
      })
      .addCase(fetchLeaderboard.fulfilled, (state, action) => {
        state.leaderboardLoading = false;
        state.leaderboards[action.payload.scope] = action.payload;
      })
      .addCase(fetchLeaderboard.rejected, (state, action) => {
        state.leaderboardLoading = false;
        state.error = action.payload;
      });
  },
});

export const { badgesEarned, dismissReveal, clearError } = gamificationSlice.actions;

// Selectors
export const selectSummary = (state) => state.gamification.summary;
export const selectBadges = (state) => state.gamification.badges;
export const selectBadgeStats = (state) => state.gamification.badgeStats;
export const selectBadgesLoading = (state) => state.gamification.badgesLoading;

// Référence stable partagée pour le cas « pas d'objectifs » : un `|| []` créait
// un nouveau tableau à chaque appel du sélecteur, ce que react-redux signale
// comme une source de rerenders inutiles (le tableau du store, lui, est déjà
// une référence stable tant que `summary` ne change pas).
const EMPTY_OBJECTIVES = [];
export const selectNextObjectives = (state) =>
  state.gamification.summary?.next_objectives || EMPTY_OBJECTIVES;
export const selectStreak = (state) => state.gamification.summary?.streak || null;
export const selectLevel = (state) => state.gamification.summary?.level || null;
export const selectPendingReveal = (state) => state.gamification.revealQueue[0] || null;

export const selectLeaderboard = (scope) => (state) =>
  state.gamification.leaderboards[scope] || null;
export const selectLeaderboardLoading = (state) =>
  state.gamification.leaderboardLoading;

export default gamificationSlice.reducer;
