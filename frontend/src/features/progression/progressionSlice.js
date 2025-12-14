import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import progressionApi from '@/services/api/progressionApi';

// Async thunks
export const fetchMyProgress = createAsyncThunk(
  'progression/fetchMyProgress',
  async (_, { rejectWithValue }) => {
    try {
      const response = await progressionApi.getMyProgress();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const markLessonCompleted = createAsyncThunk(
  'progression/markLessonCompleted',
  async (lessonId, { rejectWithValue }) => {
    try {
      const response = await progressionApi.markLessonCompleted(lessonId);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateProgress = createAsyncThunk(
  'progression/updateProgress',
  async ({ progressId, data }, { rejectWithValue }) => {
    try {
      const response = await progressionApi.updateProgress(progressId, data);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const progressionSlice = createSlice({
  name: 'progression',
  initialState: {
    // Map de lessonId -> progression object
    progressByLesson: {},
    loading: false,
    error: null,
    markingCompleted: false,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch My Progress
      .addCase(fetchMyProgress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMyProgress.fulfilled, (state, action) => {
        state.loading = false;
        // Convertir le tableau en map pour un accès rapide
        const progressMap = {};
        action.payload.forEach((progress) => {
          progressMap[progress.lesson] = progress;
        });
        state.progressByLesson = progressMap;
      })
      .addCase(fetchMyProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Mark Lesson Completed
      .addCase(markLessonCompleted.pending, (state) => {
        state.markingCompleted = true;
        state.error = null;
      })
      .addCase(markLessonCompleted.fulfilled, (state, action) => {
        state.markingCompleted = false;
        // Mettre à jour la progression dans le map
        state.progressByLesson[action.payload.lesson] = action.payload;
      })
      .addCase(markLessonCompleted.rejected, (state, action) => {
        state.markingCompleted = false;
        state.error = action.payload;
      })

      // Update Progress
      .addCase(updateProgress.fulfilled, (state, action) => {
        // Mettre à jour la progression dans le map
        state.progressByLesson[action.payload.lesson] = action.payload;
      });
  },
});

export const { clearError } = progressionSlice.actions;

// Selectors
export const selectProgressByLesson = (lessonId) => (state) =>
  state.progression.progressByLesson[lessonId] || null;

export const selectAllProgress = (state) => state.progression.progressByLesson;

export const selectProgressLoading = (state) => state.progression.loading;

export const selectProgressError = (state) => state.progression.error;

export const selectMarkingCompleted = (state) => state.progression.markingCompleted;

// Sélecteur pour obtenir le statut d'une leçon
export const selectLessonStatus = (lessonId) => (state) => {
  const progress = state.progression.progressByLesson[lessonId];
  return progress?.status || 'NOT_STARTED';
};

// Sélecteur pour vérifier si une leçon est complétée
export const selectIsLessonCompleted = (lessonId) => (state) => {
  const progress = state.progression.progressByLesson[lessonId];
  return progress?.status === 'COMPLETED';
};

export default progressionSlice.reducer;
