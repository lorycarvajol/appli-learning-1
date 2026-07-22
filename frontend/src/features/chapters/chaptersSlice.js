import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import coursesApi from '../../services/api/coursesApi';

// Async thunks
export const fetchChapters = createAsyncThunk(
  'chapters/fetchChapters',
  async (_, { rejectWithValue }) => {
    try {
      return await coursesApi.getChapters();
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch chapters');
    }
  }
);

export const fetchChapterDetails = createAsyncThunk(
  'chapters/fetchChapterDetails',
  async (slug, { rejectWithValue }) => {
    try {
      return await coursesApi.getChapter(slug);
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch chapter details');
    }
  }
);

export const fetchLesson = createAsyncThunk(
  'chapters/fetchLesson',
  async (slug, { rejectWithValue }) => {
    try {
      return await coursesApi.getLesson(slug);
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch lesson');
    }
  }
);

const initialState = {
  chapters: [],
  currentChapter: null,
  currentLesson: null,
  loading: false,
  error: null,
};

const chaptersSlice = createSlice({
  name: 'chapters',
  initialState,
  reducers: {
    clearCurrentChapter: (state) => {
      state.currentChapter = null;
    },
    clearCurrentLesson: (state) => {
      state.currentLesson = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch chapters
    builder
      .addCase(fetchChapters.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChapters.fulfilled, (state, action) => {
        state.loading = false;
        state.chapters = action.payload.results || action.payload;
      })
      .addCase(fetchChapters.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Fetch chapter details
    builder
      .addCase(fetchChapterDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChapterDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChapter = action.payload;
      })
      .addCase(fetchChapterDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Fetch lesson
    builder
      .addCase(fetchLesson.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLesson.fulfilled, (state, action) => {
        state.loading = false;
        state.currentLesson = action.payload;
      })
      .addCase(fetchLesson.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearCurrentChapter, clearCurrentLesson, clearError } = chaptersSlice.actions;
export default chaptersSlice.reducer;
