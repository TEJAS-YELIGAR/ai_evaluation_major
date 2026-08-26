import { Navigate } from 'react-router-dom'
import { getUser, isLoggedIn } from '../utils/auth'

export default function ProtectedRoute({ children, role }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  if (role && getUser()?.role !== role) {
    return <Navigate to="/" replace />
  }
  return children
}