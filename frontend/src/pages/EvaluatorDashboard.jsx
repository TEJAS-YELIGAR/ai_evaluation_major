import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { getUser } from '../utils/auth'

export default function EvaluatorDashboard() {
  const [stats, setStats] = useState({ total: 0, done: 0, pending: 0 })
  const user = getUser()
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/booklets').then(res => {
      const b = res.data
      setStats({
        total:   b.length,
        done:    b.filter(x => x.is_finalized).length,
        pending: b.filter(x => x.status === 'completed' && !x.is_finalized).length,
      })
    })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">

        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">
            Welcome, {user?.full_name}!
          </h1>
          <p className="text-gray-500 text-sm mt-1">Evaluator Dashboard</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Total Booklets', value: stats.total,   color: 'blue'  },
            { label: 'Finalized ✅',   value: stats.done,    color: 'green' },
            { label: 'To Evaluate',    value: stats.pending, color: 'yellow'},
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl p-6 shadow-sm">
              <p className="text-gray-500 text-sm">{s.label}</p>
              <p className={`text-3xl font-bold text-${s.color}-600 mt-1`}>
                {s.value}
              </p>
            </div>
          ))}
        </div>

        {/* Main Action */}
        <div className="bg-white rounded-xl p-8 shadow-sm text-center">
          <div className="text-6xl mb-4">📋</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            Start Evaluating
          </h2>
          <p className="text-gray-500 mb-6">
            Select scheme year → semester → subject → student to begin evaluation
          </p>
          <button
            onClick={() => navigate('/evaluate')}
            className="bg-blue-900 text-white px-8 py-3 rounded-xl
                       font-semibold hover:bg-blue-800 text-lg">
            Start Evaluation →
          </button>
        </div>
      </div>
    </div>
  )
}