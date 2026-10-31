import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function Students() {
  const [booklets, setBooklets] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/booklets').then(res => setBooklets(res.data))
  }, [])

  const statusColor = (status) => {
    if (status === 'completed') return 'bg-green-100 text-green-700'
    if (status === 'failed') return 'bg-red-100 text-red-700'
    if (status === 'processing') return 'bg-blue-100 text-blue-700'
    return 'bg-yellow-100 text-yellow-700'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">All Students</h1>
          <button
            onClick={() => navigate('/upload')}
            className="bg-blue-900 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-800"
          >
            + Upload Booklet
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">USN</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {booklets.map(b => (
                <tr key={b.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-500">{b.usn}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(b.status)}`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(b.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    {b.status === 'completed' && (
                      <button
                        onClick={() => navigate(`/results/${b.id}`)}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        View Results
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {booklets.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-400 text-sm">
                    No booklets uploaded yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}