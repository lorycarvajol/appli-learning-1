import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import chaptersReducer from '../features/chapters/chaptersSlice'
import trainerReducer from '../features/trainer/trainerSlice'
import progressionReducer from '../features/progression/progressionSlice'
import gamificationReducer from '../features/gamification/gamificationSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chapters: chaptersReducer,
    trainer: trainerReducer,
    progression: progressionReducer,
    gamification: gamificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
})
