import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import progressionApi from '../../services/api/progressionApi';

// Async thunks
export const fetchLearnersSummary = createAsyncThunk(
  'trainer/fetchLearnersSummary',
  async (_, { rejectWithValue }) => {
    try {
      const response = await progressionApi.getLearnersSummary();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch learners summary');
    }
  }
);

export const fetchRecentActivity = createAsyncThunk(
  'trainer/fetchRecentActivity',
  async (limit = 50, { rejectWithValue }) => {
    try {
      const response = await progressionApi.getRecentActivity(limit);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch recent activity');
    }
  }
);

export const fetchLearnerDetail = createAsyncThunk(
  'trainer/fetchLearnerDetail',
  async (learnerId, { rejectWithValue }) => {
    try {
      const response = await progressionApi.getLearnerDetail(learnerId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch learner details');
    }
  }
);

export const unlockChapter = createAsyncThunk(
  'trainer/unlockChapter',
  async ({ userId, chapterId }, { rejectWithValue }) => {
    try {
      const response = await progressionApi.unlockChapter(userId, chapterId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to unlock chapter');
    }
  }
);

export const lockChapter = createAsyncThunk(
  'trainer/lockChapter',
  async ({ userId, chapterId }, { rejectWithValue }) => {
    try {
      const response = await progressionApi.lockChapter(userId, chapterId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to lock chapter');
    }
  }
);

const trainerSlice = createSlice({
  name: 'trainer',
  initialState: {
    learnersSummary: [],
    recentActivity: [],
    selectedLearner: null,
    loading: false,
    error: null,
    unlockLoading: false,
    unlockError: null
  },
  reducers: {
    clearSelectedLearner: (state) => {
      state.selectedLearner = null;
    },
    clearError: (state) => {
      state.error = null;
      state.unlockError = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Learners Summary
      .addCase(fetchLearnersSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLearnersSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.learnersSummary = action.payload;
      })
      .addCase(fetchLearnersSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Recent Activity
      .addCase(fetchRecentActivity.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecentActivity.fulfilled, (state, action) => {
        state.loading = false;
        state.recentActivity = action.payload;
      })
      .addCase(fetchRecentActivity.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Learner Detail
      .addCase(fetchLearnerDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLearnerDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedLearner = action.payload;
      })
      .addCase(fetchLearnerDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Unlock Chapter
      .addCase(unlockChapter.pending, (state) => {
        state.unlockLoading = true;
        state.unlockError = null;
      })
      .addCase(unlockChapter.fulfilled, (state) => {
        state.unlockLoading = false;
        // Refresh learner detail if it's the currently selected learner
      })
      .addCase(unlockChapter.rejected, (state, action) => {
        state.unlockLoading = false;
        state.unlockError = action.payload;
      })

      // Lock Chapter
      .addCase(lockChapter.pending, (state) => {
        state.unlockLoading = true;
        state.unlockError = null;
      })
      .addCase(lockChapter.fulfilled, (state) => {
        state.unlockLoading = false;
      })
      .addCase(lockChapter.rejected, (state, action) => {
        state.unlockLoading = false;
        state.unlockError = action.payload;
      });
  }
});

export const { clearSelectedLearner, clearError } = trainerSlice.actions;
export default trainerSlice.reducer;
