import { Link, useNavigate } from 'react-router-dom'
import { getUser, logout, isAdmin } from '../utils/auth'

export default function Navbar() {
  const user = getUser()
  const navigate = useNavigate()

  return (
    <nav className="bg-blue-900 text-white px-6 py-3 flex justify-between items-center shadow-lg">
      <div className="flex items-center gap-6">
        <span className="font-bold text-lg">VTU AI Evaluator</span>

        {/* ADMIN links */}
        {isAdmin() && (
          <>
            <Link to="/dashboard/admin"
              className="hover:text-blue-300 text-sm">Dashboard</Link>
            <Link to="/subjects"
              className="hover:text-blue-300 text-sm">Subjects</Link>
            <Link to="/upload"
              className="hover:text-blue-300 text-sm">Upload Booklets</Link>
            <Link to="/students"
              className="hover:text-blue-300 text-sm">All Students</Link>
          </>
        )}

        {/* EVALUATOR links */}
        {!isAdmin() && (
          <>
            <Link to="/dashboard/evaluator"
              className="hover:text-blue-300 text-sm">Dashboard</Link>
            <Link to="/evaluate"
              className="hover:text-blue-300 text-sm">Evaluate</Link>
          </>
        )}
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-blue-300">
          {user?.full_name}
          <span className={`ml-2 text-xs px-2 py-0.5 rounded ${
            isAdmin()
              ? 'bg-red-500 text-white'
              : 'bg-green-500 text-white'
          }`}>
            {user?.role?.toUpperCase()}
          </span>
        </span>
        <button
          onClick={logout}
          className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm">
          Logout
        </button>
      </div>
    </nav>
  )
}