import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { getApiErrorMessage } from '../utils/apiErrors'

export default function BookletUpload() {
  const [subjects, setSubjects] = useState([])
  const [form, setForm] = useState({
    usn: '', subject_id: ''
  })
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    api.get('/subjects').then(res => setSubjects(res.data))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return alert('Please select a PDF file')

    setLoading(true)
    setStatus('Uploading...')

    try {
      const data = new FormData()
      data.append('usn', form.usn)
      data.append('subject_id', form.subject_id)
      data.append('file', file)

      await api.post('/booklets/upload', data)
      setStatus('Booklet uploaded successfully. Evaluators can now review it.')
      setForm({ usn: '', subject_id: '' })
      setFile(null)
      e.target.reset()
      setLoading(false)

    } catch (err) {
      setStatus('Upload failed: ' + getApiErrorMessage(err))
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          Upload Answer Booklet
        </h1>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                USN
              </label>
              <input
                type="text"
                value={form.usn}
                onChange={e => setForm({...form, usn: e.target.value.toUpperCase()})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                minLength={10}
                maxLength={10}
                pattern="[1-9][A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{3}"
                title="Enter a USN such as 4JD23IS107."
                autoCapitalize="characters"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <select
                value={form.subject_id}
                onChange={e => setForm({...form, subject_id: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select subject...</option>
                {subjects.map(s => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Answer Booklet PDF
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={e => setFile(e.target.files[0])}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
            </div>

            {status && (
              <div className="bg-blue-50 text-blue-700 px-4 py-3 rounded text-sm">
                {status}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-900 text-white py-2 rounded-lg hover:bg-blue-800 disabled:opacity-50 font-medium"
            >
              {loading ? 'Uploading...' : 'Upload Booklet'}
            </button>

          </form>
        </div>
      </div>
    </div>
  )
}