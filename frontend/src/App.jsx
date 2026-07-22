import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './features/auth/Login'
import Register from './features/auth/Register'
import ForgotPassword from './features/auth/ForgotPassword'
import ResetPassword from './features/auth/ResetPassword'
import JoinCohort from './features/cohorts/JoinCohort'
import PrivacyPolicy from './features/legal/PrivacyPolicy'
import LegalNotice from './features/legal/LegalNotice'
import Terms from './features/legal/Terms'
import Dashboard from './features/dashboard/Dashboard'
import PrivateRoute from './features/auth/PrivateRoute'
import Layout from './components/layout/Layout'
import ChaptersList from './features/chapters/ChaptersList'
import ChapterDetail from './features/chapters/ChapterDetail'
import LessonView from './features/chapters/LessonView'
import TrainerDashboard from './features/trainer/TrainerDashboard'
import ProgressionPage from './features/progression/ProgressionPage'
import BadgesPage from './features/gamification/BadgesPage'
import ProfilePage from './features/profile/ProfilePage'
import useThemePreferenceSync from './features/profile/useThemePreferenceSync'
import { fetchCurrentUser } from './features/auth/authSlice'
import AdminSpace from './features/administration/AdminSpace'
import { ROLES, STAFF_ROLES } from './constants/roles'

function App() {
  const dispatch = useDispatch()
  const { user } = useSelector((state) => state.auth)

  // Monté ici, à l'intérieur du store : `ThemeProvider` est au-dessus et ne
  // peut pas lire le profil lui-même.
  useThemePreferenceSync()

  useEffect(() => {
    const hasToken = localStorage.getItem('accessToken')
    if (hasToken && !user) {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, user])

  return (
    <Routes>
      {/* Public routes - without layout */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />
      {/* Lien d'invitation : public, il doit fonctionner sans session */}
      <Route path="/rejoindre/:token" element={<JoinCohort />} />

      {/* Pages légales : publiques, accessibles avant toute inscription */}
      <Route path="/confidentialite" element={<PrivacyPolicy />} />
      <Route path="/mentions-legales" element={<LegalNotice />} />
      <Route path="/cgu" element={<Terms />} />

      {/* Protected routes - with layout */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/chapters"
        element={
          <PrivateRoute>
            <Layout>
              <ChaptersList />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/chapters/:slug"
        element={
          <PrivateRoute>
            <Layout>
              <ChapterDetail />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/lessons/:slug"
        element={
          <PrivateRoute>
            <Layout>
              <LessonView />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/trainer"
        element={
          <PrivateRoute roles={STAFF_ROLES}>
            <Layout>
              <TrainerDashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/progression"
        element={
          <PrivateRoute>
            <Layout>
              <ProgressionPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/badges"
        element={
          <PrivateRoute>
            <Layout>
              <BadgesPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/profil"
        element={
          <PrivateRoute>
            <Layout>
              <ProfilePage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/administration"
        element={
          <PrivateRoute roles={[ROLES.ADMIN]}>
            <Layout>
              <AdminSpace />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
