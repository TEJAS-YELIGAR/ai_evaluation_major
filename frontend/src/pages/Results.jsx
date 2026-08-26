import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function Results() {
  const { bookletId } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [overriding, setOverriding] = useState(null)
  const [newMark, setNewMark] = useState('')

  useEffect(() => {
    api.get(`/results/${bookletId}`)
      .then(res => setResults(res.data))
      .finally(() => setLoading(false))
  }, [bookletId])

  const handleOverride = async (evalId) => {
    try {
      await api.put('/results/override', {
        evaluation_id: evalId,
        new_mark: parseFloat(newMark)
      })
      // Refresh results
      const res = await api.get(`/results/${bookletId}`)
      setResults(res.data)
      setOverriding(null)
      setNewMark('')
    } catch (err) {
      alert('Override failed: ' + err.response?.data?.detail)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex justify-center items-center h-64">
        <p className="text-gray-500">Loading results...</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                {results?.student_name}
              </h1>
              <p className="text-gray-500 text-sm">
                USN: {results?.usn} | Subject: {results?.subject_name}
              </p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-blue-900">
                {results?.total_awarded} / {results?.total_max}
              </p>
              <p className="text-gray-500 text-sm">Total Marks</p>
            </div>
          </div>
        </div>

        {/* Questions */}
        {results?.questions.map(q => (
          <div key={q.question_no} className="bg-white rounded-xl p-6 shadow-sm mb-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-800">
                Question {q.question_no}
              </h2>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {q.question_total} / {q.question_max} marks
              </span>
            </div>

            {/* Criteria */}
            <div className="space-y-3">
              {q.scores.map(score => (
                <div key={score.id}
                  className="border border-gray-100 rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700 text-sm">
                        {score.criterion}
                      </span>
                      {score.overridden && (
                        <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded">
                          Overridden
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`font-bold text-sm ${
                        score.awarded >= score.max_marks * 0.7
                          ? 'text-green-600'
                          : score.awarded >= score.max_marks * 0.4
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}>
                        {score.awarded} / {score.max_marks}
                      </span>

                      {/* Override button */}
                      {overriding === score.id ? (
                        <div className="flex gap-2 items-center">
                          <input
                            type="number"
                            min="0"
                            max={score.max_marks}
                            step="0.5"
                            value={newMark}
                            onChange={e => setNewMark(e.target.value)}
                            className="border rounded px-2 py-1 w-16 text-sm"
                          />
                          <button
                            onClick={() => handleOverride(score.id)}
                            className="bg-green-600 text-white text-xs px-2 py-1 rounded"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setOverriding(null)}
                            className="bg-gray-400 text-white text-xs px-2 py-1 rounded"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setOverriding(score.id)
                            setNewMark(score.awarded)
                          }}
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Override
                        </button>
                      )}
                    </div>
                  </div>
                  <p className="text-gray-500 text-sm">{score.reason}</p>
                </div>
              ))}
            </div>

            {q.feedback && (
              <div className="mt-3 bg-blue-50 rounded-lg p-3">
                <p className="text-blue-700 text-sm">
                  <span className="font-medium">Feedback:</span> {q.feedback}
                </p>
              </div>
            )}
          </div>
        ))}

        {!results?.is_finalized && results?.status === 'completed' && (
          <div className="bg-white rounded-xl p-6 shadow-sm mt-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-800">Review Complete?</h3>
                <p className="text-gray-500 text-sm mt-1">
                  Click Done to finalize this evaluation. Student will show as done in the list.
                </p>
              </div>
              <button
                onClick={async () => {
                  await api.post('/results/finalize', { booklet_id: parseInt(bookletId) })
                  navigate(-1)
                }}
                className="bg-green-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-green-700 text-lg">
                Done - Mark as Evaluated
              </button>
            </div>
          </div>
        )}

        {results?.is_finalized && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mt-4 text-center">
            <p className="text-green-700 font-semibold">This evaluation has been finalized</p>
          </div>
        )}
      </div>
    </div>
  )
}