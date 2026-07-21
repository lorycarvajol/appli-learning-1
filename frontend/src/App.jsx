import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './features/auth/Login'
import Register from './features/auth/Register'
import Dashboard from './features/dashboard/Dashboard'
import PrivateRoute from './features/auth/PrivateRoute'
import Layout from './components/layout/Layout'
import ChaptersList from './features/chapters/ChaptersList'
import ChapterDetail from './features/chapters/ChapterDetail'
import LessonView from './features/chapters/LessonView'
import TrainerDashboard from './features/trainer/TrainerDashboard'
import ProgressionPage from './features/progression/ProgressionPage'
import BadgesPage from './features/gamification/BadgesPage'
import { fetchCurrentUser } from './features/auth/authSlice'

function App() {
  const dispatch = useDispatch()
  const { user } = useSelector((state) => state.auth)

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
          <PrivateRoute>
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
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
