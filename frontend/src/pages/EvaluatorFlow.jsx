import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

const STEPS = [
  "Select Scheme Year",
  "Select Semester",
  "Select Subject",
  "Select Student",
  "View Results"
]

export default function EvaluatorFlow() {
  const [step, setStep]           = useState(0)
  const [schemeYears, setSchemeYears] = useState([])
  const [semesters, setSemesters]   = useState([])
  const [subjects, setSubjects]     = useState([])
  const [students, setStudents]     = useState([])
  const [evaluatingId, setEvaluatingId] = useState(null)

  const [selectedYear,    setSelectedYear]    = useState('')
  const [selectedSem,     setSelectedSem]     = useState('')
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [selectedStudent, setSelectedStudent] = useState(null)

  const navigate = useNavigate()

  // Load scheme years on mount
  useEffect(() => {
    api.get('/subjects/scheme-years').then(res => setSchemeYears(res.data))
  }, [])

  // Load semesters when year selected
  useEffect(() => {
    if (selectedYear) {
      api.get(`/subjects/semesters/${selectedYear}`)
        .then(res => setSemesters(res.data))
    }
  }, [selectedYear])

  // Load subjects when sem selected
  useEffect(() => {
    if (selectedYear && selectedSem) {
      api.get(`/subjects/filter/${selectedYear}/${selectedSem}`)
        .then(res => setSubjects(res.data))
    }
  }, [selectedYear, selectedSem])

  // Load students when subject selected
  useEffect(() => {
    if (selectedSubject) {
      api.get(`/subjects/${selectedSubject.id}/students`)
        .then(res => setStudents(res.data))
    }
  }, [selectedSubject])

  const statusIcon = (student) => {
    if (student.is_finalized) return '✅'
    if (student.status === 'completed') return '🔵'
    if (student.status === 'processing') return '⏳'
    if (student.status === 'failed') return '❌'
    return '⬜'
  }

  const evaluateStudent = async (bookletId) => {
    setEvaluatingId(bookletId)
    try {
      await api.post(`/booklets/${bookletId}/evaluate`)

      const interval = setInterval(async () => {
        const response = await api.get(`/booklets/${bookletId}/status`)
        if (response.data.status === 'completed') {
          clearInterval(interval)
          navigate(`/results/${bookletId}`)
        } else if (response.data.status === 'failed') {
          clearInterval(interval)
          setEvaluatingId(null)
          alert('Evaluation failed. Please try again.')
        }
      }, 2000)
    } catch (err) {
      setEvaluatingId(null)
      alert('Unable to start evaluation: ' + (err.response?.data?.detail || err.message))
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">

        {/* Progress Steps */}
        <div className="flex items-center mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold
                ${i < step ? 'bg-green-500 text-white' :
                  i === step ? 'bg-blue-900 text-white' :
                  'bg-gray-200 text-gray-500'}`}>
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`ml-2 text-sm hidden md:block
                ${i === step ? 'text-blue-900 font-medium' : 'text-gray-400'}`}>
                {s}
              </span>
              {i < STEPS.length - 1 && (
                <div className={`h-0.5 w-8 mx-2
                  ${i < step ? 'bg-green-500' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step 0 — Scheme Year */}
        {step === 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-800 mb-6">
              Select Scheme Year
            </h2>
            <div className="grid grid-cols-3 gap-4">
              {schemeYears.map(year => (
                <button key={year}
                  onClick={() => { setSelectedYear(year); setStep(1) }}
                  className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500
                             hover:bg-blue-50 text-center transition-all">
                  <p className="text-2xl font-bold text-blue-900">{year}</p>
                  <p className="text-gray-500 text-sm mt-1">Scheme</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 1 — Semester */}
        {step === 1 && (
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <button onClick={() => setStep(0)}
              className="text-blue-600 text-sm mb-4">← Back</button>
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              Select Semester
            </h2>
            <p className="text-gray-500 text-sm mb-6">
              Scheme: {selectedYear}
            </p>
            <div className="grid grid-cols-4 gap-4">
              {semesters.map(sem => (
                <button key={sem}
                  onClick={() => { setSelectedSem(sem); setStep(2) }}
                  className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500
                             hover:bg-blue-50 text-center transition-all">
                  <p className="text-2xl font-bold text-blue-900">{sem}</p>
                  <p className="text-gray-500 text-sm mt-1">Semester</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2 — Subject */}
        {step === 2 && (
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <button onClick={() => setStep(1)}
              className="text-blue-600 text-sm mb-4">← Back</button>
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              Select Subject
            </h2>
            <p className="text-gray-500 text-sm mb-6">
              Scheme {selectedYear} | Semester {selectedSem}
            </p>
            <div className="space-y-3">
              {subjects.map(sub => (
                <button key={sub.id}
                  onClick={() => { setSelectedSubject(sub); setStep(3) }}
                  className="w-full p-4 border-2 border-gray-200 rounded-xl
                             hover:border-blue-500 hover:bg-blue-50
                             text-left transition-all flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-800">{sub.name}</p>
                    <p className="text-gray-500 text-sm">{sub.subject_code}</p>
                  </div>
                  <span className="text-blue-900 font-bold text-lg">→</span>
                </button>
              ))}
              {subjects.length === 0 && (
                <p className="text-center text-gray-400 py-8">
                  No subjects found for this semester
                </p>
              )}
            </div>
          </div>
        )}

        {/* Step 3 — Student List */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b">
              <button onClick={() => setStep(2)}
                className="text-blue-600 text-sm mb-4 block">← Back</button>
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">
                    {selectedSubject?.name}
                  </h2>
                  <p className="text-gray-500 text-sm">
                    {selectedSubject?.subject_code} |
                    Scheme {selectedYear} | Sem {selectedSem}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {students.filter(s => s.is_finalized).length} /
                    {students.length} Done
                  </p>
                  <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${students.length > 0
                          ? (students.filter(s => s.is_finalized).length / students.length) * 100
                          : 0}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">
                    Student Name
                  </th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">
                    USN
                  </th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">
                    Marks
                  </th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {students.map(student => (
                  <tr key={student.booklet_id}
                    className={`hover:bg-gray-50 ${student.is_finalized ? 'bg-green-50' : ''}`}>
                    <td className="px-6 py-4 text-xl">
                      {statusIcon(student)}
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800">
                      {student.student_name}
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-sm">
                      {student.usn}
                    </td>
                    <td className="px-6 py-4">
                      {student.total_marks !== null ? (
                        <span className={`font-bold ${
                          student.total_marks / student.total_max >= 0.4
                            ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {student.total_marks} / {student.total_max}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {(student.status === 'completed' || student.status === 'pending' || student.status === 'failed') && (
                        <button
                          disabled={evaluatingId === student.booklet_id}
                          onClick={() => student.status === 'completed'
                            ? navigate(`/results/${student.booklet_id}`)
                            : evaluateStudent(student.booklet_id)}
                          className="bg-blue-900 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-800 disabled:opacity-50">
                          {evaluatingId === student.booklet_id ? 'Evaluating...' : student.is_finalized ? 'View' : 'Evaluate →'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {students.length === 0 && (
                  <tr>
                    <td colSpan="5"
                      className="px-6 py-12 text-center text-gray-400">
                      No students found for this subject
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}