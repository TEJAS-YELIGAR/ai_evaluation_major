import { useState, useEffect } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function Results() {
  const { bookletId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [overriding, setOverriding] = useState(null)
  const [newMark, setNewMark] = useState('')
  const [bookletUrl, setBookletUrl] = useState(null)
  const [questionPaperUrl, setQuestionPaperUrl] = useState(null)
  const [bookletError, setBookletError] = useState('')
  const [questionPaperError, setQuestionPaperError] = useState('')
  const [activeQuestion, setActiveQuestion] = useState(null)
  const [evaluationStatus, setEvaluationStatus] = useState('')

  useEffect(() => {
    let mounted = true
    const loadResults = async () => {
      try {
        const resultResponse = await api.get(`/results/${bookletId}`)
        if (!mounted) return
        setResults(resultResponse.data)
        setEvaluationStatus(resultResponse.data.status)
        setActiveQuestion(resultResponse.data.questions[0]?.question_no ?? null)

        try {
          const bookletResponse = await api.get(`/booklets/${bookletId}/file`, { responseType: 'blob' })
          if (mounted) setBookletUrl(URL.createObjectURL(bookletResponse.data))
        } catch {
          if (mounted) setBookletError('Student booklet could not be loaded.')
        }

        try {
          const paperResponse = await api.get(`/soe/${resultResponse.data.subject_id}/question-paper`, { responseType: 'blob' })
          if (mounted) setQuestionPaperUrl(URL.createObjectURL(paperResponse.data))
        } catch {
          if (mounted) setQuestionPaperError('Question paper has not been uploaded for this subject yet.')
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }
    loadResults()
    return () => {
      mounted = false
      if (bookletUrl) URL.revokeObjectURL(bookletUrl)
      if (questionPaperUrl) URL.revokeObjectURL(questionPaperUrl)
    }
  }, [bookletId])

  useEffect(() => {
    if (!results || results.status === 'completed' || results.status === 'failed') return undefined
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/results/${bookletId}`)
        setResults(response.data)
        setEvaluationStatus(response.data.status)
      } catch {
        // The initial result remains visible while processing.
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [bookletId, results?.status])

  useEffect(() => {
    if (results?.questions.length && activeQuestion === null) {
      setActiveQuestion(results.questions[0].question_no)
    }
  }, [results, activeQuestion])

  const refreshResults = async () => {
    const res = await api.get(`/results/${bookletId}`)
    setResults(res.data)
  }

  const startEvaluation = async () => {
    try {
      await api.post(`/booklets/${bookletId}/evaluate`)
      const res = await api.get(`/results/${bookletId}`)
      setResults(res.data)
      setEvaluationStatus(res.data.status)
    } catch (err) {
      alert('Unable to start evaluation: ' + (err.response?.data?.detail || err.message))
    }
  }

  const showStartButton = !!results && !results.is_finalized && results.status !== 'completed' && results.status !== 'failed' && results.status !== 'processing'
  const showEvaluationProgress = !!results && !results.is_finalized && (results.status === 'processing' || results.status === 'pending') && results?.questions?.length > 0

  const selectQuestion = (questionNo) => {
    setActiveQuestion(questionNo)
    document.getElementById(`question-${questionNo}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const handleOverride = async (evalId) => {
    try {
      await api.put('/results/override', {
        evaluation_id: evalId,
        new_mark: parseFloat(newMark)
      })
      // Refresh results
      await refreshResults()
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
      <div className="max-w-7xl mx-auto px-6 py-8">
        <button
          onClick={() => {
            const state = location.state || {}
            if (state.returnStep !== undefined) {
              navigate('/evaluate', { state: { ...state, returnStep: state.returnStep } })
              return
            }
            navigate('/evaluate')
          }}
          className="text-blue-600 text-sm mb-4 inline-block"
        >
          ← Back
        </button>

        {/* Header */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                USN: {results?.usn}
              </h1>
              <p className="text-gray-500 text-sm">
                Subject: {results?.subject_name}
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

        {showStartButton && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <p className="font-semibold text-blue-900">Begin Evaluation</p>
                <p className="text-sm text-blue-700 mt-1">
                  This booklet is ready to be evaluated question by question.
                </p>
              </div>
              <button
                onClick={startEvaluation}
                className="bg-blue-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-800"
              >
                Start Evaluate
              </button>
            </div>
          </div>
        )}

        {showEvaluationProgress && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <p className="font-semibold text-blue-900">AI is evaluating this booklet question by question...</p>
            <p className="text-sm text-blue-700 mt-1">
              Completed questions appear below as soon as their marks are available.
            </p>
          </div>
        )}

        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="font-semibold text-gray-800">Question Marks</h2>
              <p className="text-sm text-gray-500 mt-1">Select a question to review or override its marks.</p>
            </div>
            <span className="text-sm text-gray-500">
              {results?.questions.length || 0} questions
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {results?.questions.map(q => {
              const isLowScore = q.question_max > 0 && q.question_total / q.question_max < 0.4
              return (
                <button
                  key={q.question_no}
                  onClick={() => selectQuestion(q.question_no)}
                  className={`text-left border-2 rounded-lg p-3 transition-colors ${
                    activeQuestion === q.question_no
                      ? 'border-blue-500 bg-blue-50'
                      : isLowScore
                        ? 'border-red-200 bg-red-50 hover:border-red-400'
                        : 'border-gray-200 hover:border-blue-300'
                  }`}>
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-gray-800">Q{q.question_no}</span>
                    {isLowScore && <span className="text-xs font-medium text-red-600">Review</span>}
                  </div>
                  <p className={`text-lg font-bold mt-1 ${isLowScore ? 'text-red-600' : 'text-blue-900'}`}>
                    {q.question_total} / {q.question_max}
                  </p>
                  <p className="text-xs text-gray-500">marks</p>
                </button>
              )
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h2 className="font-semibold text-gray-800">Student Answer Booklet</h2>
            </div>
            {bookletUrl ? (
              <iframe title="Student answer booklet" src={bookletUrl} className="w-full h-[700px]" />
            ) : (
              <p className="p-6 text-sm text-gray-500">{bookletError || 'Loading student booklet...'}</p>
            )}
          </div>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h2 className="font-semibold text-gray-800">Question Paper</h2>
            </div>
            {questionPaperUrl ? (
              <iframe title="Question paper" src={questionPaperUrl} className="w-full h-[700px]" />
            ) : (
              <p className="p-6 text-sm text-gray-500">{questionPaperError || 'Loading question paper...'}</p>
            )}
          </div>
        </div>

        {/* Questions */}
        {results?.questions.map(q => (
          <div id={`question-${q.question_no}`} key={q.question_no}
            className={`bg-white rounded-xl p-6 shadow-sm mb-4 border-2 ${activeQuestion === q.question_no ? 'border-blue-500' : 'border-transparent'}`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-800">
                Question {q.question_no}
              </h2>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {q.question_total} / {q.question_max} marks
              </span>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-4">
              <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Question paper text</p>
              <p className="text-gray-800 text-sm whitespace-pre-wrap">
                {q.question_text || 'Question text is not available for this question.'}
              </p>
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
                  const state = location.state || {}
                  navigate('/evaluate', {
                    state: {
                      ...state,
                      returnStep: 4
                    }
                  })
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