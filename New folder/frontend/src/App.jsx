import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { useAuth } from './context/AuthContext'
import About from './pages/About'
import Admin from './pages/Admin'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import Home from './pages/Home'
import Login from './pages/Login'
import Predict from './pages/Predict'
import Register from './pages/Register'
import Results from './pages/Results'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function AdminRoute({ children }) {
  const { user, isAdmin } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (!isAdmin) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="predict" element={<PrivateRoute><Predict /></PrivateRoute>} />
        <Route path="results" element={<PrivateRoute><Results /></PrivateRoute>} />
        <Route path="dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="history" element={<PrivateRoute><History /></PrivateRoute>} />
        <Route path="admin" element={<AdminRoute><Admin /></AdminRoute>} />
      </Route>
    </Routes>
  )
}
