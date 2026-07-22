import { useEffect, lazy, Suspense } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Routes, Route, Navigate } from 'react-router-dom'
// Structurels : chargés d'emblée, présents sur (presque) chaque route.
import PrivateRoute from './features/auth/PrivateRoute'
import Layout from './components/layout/Layout'
import PageLoader from './components/ui/PageLoader'
import useThemePreferenceSync from './features/profile/useThemePreferenceSync'
import { fetchCurrentUser } from './features/auth/authSlice'
import { ROLES, STAFF_ROLES } from './constants/roles'

// Pages chargées à la demande : chaque route devient un morceau séparé, sorti
// du bundle d'entrée. Gain principal : l'éditeur Monaco (via LessonView →
// ExerciseInterface) ne pèse plus sur le premier chargement — il est de plus
// isolé dans LessonView pour ne se charger qu'à l'ouverture d'un exercice.
const Login = lazy(() => import('./features/auth/Login'))
const Register = lazy(() => import('./features/auth/Register'))
const ForgotPassword = lazy(() => import('./features/auth/ForgotPassword'))
const ResetPassword = lazy(() => import('./features/auth/ResetPassword'))
const JoinCohort = lazy(() => import('./features/cohorts/JoinCohort'))
const PrivacyPolicy = lazy(() => import('./features/legal/PrivacyPolicy'))
const LegalNotice = lazy(() => import('./features/legal/LegalNotice'))
const Terms = lazy(() => import('./features/legal/Terms'))
const Dashboard = lazy(() => import('./features/dashboard/Dashboard'))
const ChaptersList = lazy(() => import('./features/chapters/ChaptersList'))
const ChapterDetail = lazy(() => import('./features/chapters/ChapterDetail'))
const LessonView = lazy(() => import('./features/chapters/LessonView'))
const TrainerDashboard = lazy(() => import('./features/trainer/TrainerDashboard'))
const ProgressionPage = lazy(() => import('./features/progression/ProgressionPage'))
const BadgesPage = lazy(() => import('./features/gamification/BadgesPage'))
const ProfilePage = lazy(() => import('./features/profile/ProfilePage'))
const AdminSpace = lazy(() => import('./features/administration/AdminSpace'))

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
    <Suspense fallback={<PageLoader />}>
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
    </Suspense>
  )
}

export default App
