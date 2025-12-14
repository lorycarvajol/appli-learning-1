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

function App() {
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
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
