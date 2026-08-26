import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { isAdmin } from '../utils/auth'
import { useNavigate } from 'react-router-dom'

export default function Subjects() {
  const [subjects, setSubjects] = useState([])
  const emptyForm = { name: '', subject_code: '', scheme_year: '', semester: '', department: '' }
  const [form, setForm] = useState(emptyForm)
  const [showForm, setShowForm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/subjects').then(res => setSubjects(res.data))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post('/subjects', form)
    const res = await api.get('/subjects')
    setSubjects(res.data)
    setForm(emptyForm)
    setShowForm(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Subjects</h1>
          {isAdmin() && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-blue-900 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-800"
            >
              + New Subject
            </button>
          )}
        </div>

        {showForm && (
          <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
            <h2 className="font-semibold text-gray-700 mb-4">Create Subject</h2>
            <form onSubmit={handleCreate} className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <input
                placeholder="Subject name"
                value={form.name}
                onChange={e => setForm({...form, name: e.target.value})}
                className="border rounded-lg px-3 py-2 text-sm"
                required
              />
              <input
                placeholder="Code (e.g. BCS305)"
                value={form.subject_code}
                onChange={e => setForm({...form, subject_code: e.target.value})}
                className="border rounded-lg px-3 py-2 text-sm"
                required
              />
              <input
                placeholder="Scheme year (e.g. 2022)"
                value={form.scheme_year}
                onChange={e => setForm({...form, scheme_year: e.target.value})}
                className="border rounded-lg px-3 py-2 text-sm"
                required
              />
              <input
                placeholder="Semester (e.g. 6)"
                value={form.semester}
                onChange={e => setForm({...form, semester: e.target.value})}
                className="border rounded-lg px-3 py-2 text-sm"
                required
              />
              <input
                placeholder="Department"
                value={form.department}
                onChange={e => setForm({...form, department: e.target.value})}
                className="border rounded-lg px-3 py-2 text-sm"
                required
              />
              <button
                type="submit"
                className="col-span-2 md:col-span-5 bg-blue-900 text-white py-2 rounded-lg text-sm"
              >
                Create Subject
              </button>
            </form>
          </div>
        )}

        <div className="grid gap-4">
          {subjects.map(s => (
            <div key={s.id}
              className="bg-white rounded-xl p-6 shadow-sm flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-800">{s.name}</h3>
                <p className="text-gray-500 text-sm">
                  Semester {s.semester} | {s.department}
                </p>
              </div>
              {isAdmin() && (
                <button
                  onClick={() => navigate(`/soe/${s.id}`)}
                  className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200"
                >
                  Manage SoE
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}