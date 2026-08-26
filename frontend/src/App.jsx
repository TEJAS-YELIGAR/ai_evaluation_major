import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { getUser, isLoggedIn } from './utils/auth'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import AdminDashboard from './pages/AdminDashboard'
import EvaluatorDashboard from './pages/EvaluatorDashboard'
import Subjects from './pages/Subjects'
import SoEUpload from './pages/SoEUpload'
import BookletUpload from './pages/BookletUpload'
import Results from './pages/Results'
import Students from './pages/Students'
import EvaluatorFlow from './pages/EvaluatorFlow'

// Smart redirect based on role
function HomeRedirect() {
  if (!isLoggedIn()) return <Navigate to="/login" replace />
  const user = getUser()
  if (user?.role === 'admin') return <Navigate to="/dashboard/admin" replace />
  return <Navigate to="/dashboard/evaluator" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/dashboard" element={<HomeRedirect />} />

        {/* ADMIN ROUTES */}
        <Route path="/dashboard/admin" element={
          <ProtectedRoute><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="/subjects" element={
          <ProtectedRoute><Subjects /></ProtectedRoute>
        } />
        <Route path="/soe/:subjectId" element={
          <ProtectedRoute><SoEUpload /></ProtectedRoute>
        } />
        <Route path="/upload" element={
          <ProtectedRoute role="admin"><BookletUpload /></ProtectedRoute>
        } />
        <Route path="/students" element={
          <ProtectedRoute><Students /></ProtectedRoute>
        } />

        {/* EVALUATOR ROUTES */}
        <Route path="/dashboard/evaluator" element={
          <ProtectedRoute><EvaluatorDashboard /></ProtectedRoute>
        } />
        <Route path="/evaluate" element={
          <ProtectedRoute role="evaluator"><EvaluatorFlow /></ProtectedRoute>
        } />

        {/* SHARED */}
        <Route path="/results/:bookletId" element={
          <ProtectedRoute><Results /></ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}