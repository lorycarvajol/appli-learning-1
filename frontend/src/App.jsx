import { useEffect, lazy, Suspense } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Routes, Route, Navigate } from 'react-router-dom'
// Structurels : chargés d'emblée, présents sur (presque) chaque route.
import PrivateRoute from './features/auth/PrivateRoute'
import PublicOnlyRoute from './features/auth/PublicOnlyRoute'
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
const LeaderboardPage = lazy(() => import('./features/gamification/LeaderboardPage'))
const ProfilePage = lazy(() => import('./features/profile/ProfilePage'))
const AdminSpace = lazy(() => import('./features/administration/AdminSpace'))
const NotFound = lazy(() => import('./features/errors/NotFound'))

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
      {/*
        `PublicOnlyRoute` ne protège rien — elle évite une impasse : se
        reconnecter quand on l'est déjà ne mène nulle part. Elle respecte
        `?next=`, sans quoi un visiteur connecté suivant un lien d'invitation
        atterrirait sur le tableau de bord sans jamais rejoindre la classe.
      */}
      <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
      <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
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
        path="/classement"
        element={
          <PrivateRoute>
            <Layout>
              <LeaderboardPage />
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
      {/*
        La racine renvoie au tableau de bord **sans regarder la session**, et
        c'est voulu : `PrivateRoute` est le seul endroit qui tranche
        l'authentification. Dupliquer ici la décision créerait un second
        chemin à maintenir — et surtout un qui ignorerait `initialized`,
        le piège documenté (trancher avant le chargement du profil éjecte un
        formateur vers /dashboard à chaque rafraîchissement). Un visiteur sans
        session est donc redirigé une fois de plus, vers /login.
      */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/*
        Toute autre adresse. ⚠️ Sans cette route, `<Routes>` ne rendait
        **rien** pour une URL inconnue : une page blanche, que l'on prend
        pour une panne du site alors que c'est une faute de frappe.
        Le serveur, lui, faisait déjà sa part — `try_files … /index.html`
        dans `frontend/nginx.conf` sert la SPA pour n'importe quel chemin,
        sans quoi un lien profond aurait donné un 404 nginx.
      */}
      <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}

export default App
