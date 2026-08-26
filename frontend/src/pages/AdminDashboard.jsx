import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function AdminDashboard() {
  const [stats, setStats]         = useState({ total: 0, completed: 0, pending: 0 })
  const [evaluators, setEvaluators] = useState([])
  const [subjects, setSubjects]   = useState([])
  const [showNewEval, setShowNewEval] = useState(false)
  const [evalForm, setEvalForm]   = useState({ username:'', full_name:'', password:'' })
  const [message, setMessage]     = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/booklets').then(res => {
      const b = res.data
      setStats({
        total:     b.length,
        completed: b.filter(x => x.status === 'completed').length,
        pending:   b.filter(x => x.status === 'pending').length,
      })
    })
    api.get('/subjects').then(res => setSubjects(res.data))
    // fetch evaluators
    api.get('/auth/evaluators').then(res => setEvaluators(res.data)).catch(()=>{})
  }, [])

  const createEvaluator = async (e) => {
    e.preventDefault()
    try {
      await api.post('/auth/register', { ...evalForm, role: 'evaluator' })
      setMessage(`✅ Evaluator "${evalForm.username}" created!`)
      setEvalForm({ username:'', full_name:'', password:'' })
      setShowNewEval(false)
      api.get('/auth/evaluators').then(res => setEvaluators(res.data)).catch(()=>{})
    } catch(err) {
      setMessage('❌ ' + (err.response?.data?.detail || 'Failed'))
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 py-8">

        <h1 className="text-2xl font-bold text-gray-800 mb-8">
          Admin Dashboard
        </h1>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Total Booklets', value: stats.total,     color: 'blue'  },
            { label: 'Evaluated',      value: stats.completed, color: 'green' },
            { label: 'Pending',        value: stats.pending,   color: 'yellow'},
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl p-6 shadow-sm">
              <p className="text-gray-500 text-sm">{s.label}</p>
              <p className={`text-3xl font-bold text-${s.color}-600 mt-1`}>
                {s.value}
              </p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-6">

          {/* Evaluator Management */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-800 text-lg">
                Evaluators
              </h2>
              <button
                onClick={() => setShowNewEval(!showNewEval)}
                className="bg-blue-900 text-white px-3 py-1.5 rounded-lg text-sm">
                + Add Evaluator
              </button>
            </div>

            {message && (
              <div className="bg-blue-50 text-blue-700 px-3 py-2 rounded mb-3 text-sm">
                {message}
              </div>
            )}

            {showNewEval && (
              <form onSubmit={createEvaluator} className="space-y-3 mb-4 p-4 bg-gray-50 rounded-lg">
                <input
                  placeholder="Full Name"
                  value={evalForm.full_name}
                  onChange={e => setEvalForm({...evalForm, full_name: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
                <input
                  placeholder="Username"
                  value={evalForm.username}
                  onChange={e => setEvalForm({...evalForm, username: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={evalForm.password}
                  onChange={e => setEvalForm({...evalForm, password: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
                <button
                  type="submit"
                  className="w-full bg-green-600 text-white py-2 rounded-lg text-sm">
                  Create Evaluator Account
                </button>
              </form>
            )}

            <div className="space-y-2">
              {evaluators.map(ev => (
                <div key={ev.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm text-gray-800">{ev.full_name}</p>
                    <p className="text-gray-400 text-xs">@{ev.username}</p>
                  </div>
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">
                    Evaluator
                  </span>
                </div>
              ))}
              {evaluators.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-4">
                  No evaluators yet
                </p>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="font-semibold text-gray-800 text-lg mb-4">
              Quick Actions
            </h2>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/subjects')}
                className="w-full p-4 border-2 border-gray-200 rounded-xl
                           hover:border-blue-500 hover:bg-blue-50 text-left">
                <p className="font-semibold text-gray-800">📚 Manage Subjects</p>
                <p className="text-gray-500 text-sm">
                  Add subjects with code and scheme year
                </p>
              </button>

              <button
                onClick={() => navigate('/upload')}
                className="w-full p-4 border-2 border-gray-200 rounded-xl
                           hover:border-blue-500 hover:bg-blue-50 text-left">
                <p className="font-semibold text-gray-800">📄 Upload Booklets</p>
                <p className="text-gray-500 text-sm">
                  Upload student answer booklets with USN
                </p>
              </button>

              <button
                onClick={() => navigate('/students')}
                className="w-full p-4 border-2 border-gray-200 rounded-xl
                           hover:border-blue-500 hover:bg-blue-50 text-left">
                <p className="font-semibold text-gray-800">📊 View All Reports</p>
                <p className="text-gray-500 text-sm">
                  See all evaluated booklets and marks
                </p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}