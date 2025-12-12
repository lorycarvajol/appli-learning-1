import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import chaptersReducer from '../features/chapters/chaptersSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chapters: chaptersReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
})
