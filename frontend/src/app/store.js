import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import chaptersReducer from '../features/chapters/chaptersSlice'
import trainerReducer from '../features/trainer/trainerSlice'
import progressionReducer from '../features/progression/progressionSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chapters: chaptersReducer,
    trainer: trainerReducer,
    progression: progressionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
})
