import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './features/auth/Login'
import Register from './features/auth/Register'
import Dashboard from './components/Dashboard'
import PrivateRoute from './features/auth/PrivateRoute'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
