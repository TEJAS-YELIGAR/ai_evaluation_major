import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { getUser } from '../utils/auth'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0, completed: 0, pending: 0, failed: 0
  })
  const user = getUser()

  useEffect(() => {
    api.get('/booklets').then(res => {
      const booklets = res.data
      setStats({
        total: booklets.length,
        completed: booklets.filter(b => b.status === 'completed').length,
        pending: booklets.filter(b => b.status === 'pending').length,
        failed: booklets.filter(b => b.status === 'failed').length,
      })
    }).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 py-8">

        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">
            Welcome, {user?.full_name}!
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            VTU AI Answer Evaluation System
          </p>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Booklets', value: stats.total, color: 'blue' },
            { label: 'Completed', value: stats.completed, color: 'green' },
            { label: 'Pending', value: stats.pending, color: 'yellow' },
            { label: 'Failed', value: stats.failed, color: 'red' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl p-6 shadow-sm">
              <p className="text-gray-500 text-sm">{s.label}</p>
              <p className={`text-3xl font-bold text-${s.color}-600 mt-1`}>
                {s.value}
              </p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-700 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-3 gap-4">
            <a href="/upload"
              className="bg-blue-900 text-white text-center py-3 rounded-lg hover:bg-blue-800 text-sm font-medium">
              Upload Booklet
            </a>
            <a href="/subjects"
              className="bg-gray-100 text-gray-700 text-center py-3 rounded-lg hover:bg-gray-200 text-sm font-medium">
              Manage Subjects
            </a>
            <a href="/students"
              className="bg-gray-100 text-gray-700 text-center py-3 rounded-lg hover:bg-gray-200 text-sm font-medium">
              View All Students
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}