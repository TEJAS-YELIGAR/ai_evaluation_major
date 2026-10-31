import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { getApiErrorMessage } from '../utils/apiErrors'

export default function SoEUpload() {
  const { subjectId } = useParams()
  const [subject, setSubject] = useState(null)
  const [soe, setSoe] = useState(null)
  const [questions, setQuestions] = useState([])
  const [file, setFile] = useState(null)
  const [questionPaper, setQuestionPaper] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    api.get(`/subjects/${subjectId}`).then(res => setSubject(res.data))
    api.get(`/soe/${subjectId}`).then(res => setSoe(res.data)).catch(() => {})
    api.get(`/soe/${subjectId}/questions`).then(res => setQuestions(res.data.questions)).catch(() => {})
  }, [subjectId])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file || !questionPaper) {
      setMessage('Upload failed: Select both the SoE Excel file and question paper PDF.')
      return
    }

    const data = new FormData()
    data.append('file', file)
    data.append('question_paper', questionPaper)

    try {
      const res = await api.post(`/soe/upload/${subjectId}`, data)
      setMessage(res.data.message)
      const soeRes = await api.get(`/soe/${subjectId}`)
      setSoe(soeRes.data)
    } catch (err) {
      setMessage('Upload failed: ' + getApiErrorMessage(err))
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Scheme of Evaluation
        </h1>
        <p className="text-gray-500 text-sm mb-6">
          {subject?.name} | Semester {subject?.semester}
        </p>

        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">Upload SoE Excel</h2>
          <p className="text-gray-500 text-xs mb-4">
            Excel columns: question_no | criterion_name | max_marks | model_answer
          </p>

          {message && (
            <div className={`${message.startsWith('Upload failed:') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'} px-4 py-3 rounded mb-4 text-sm`}>
              {message}
            </div>
          )}

          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Scheme of Evaluation Excel</label>
              <input
                type="file"
                accept=".xlsx"
                onChange={e => setFile(e.target.files[0])}
                className="border rounded-lg px-3 py-2 text-sm w-full"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Question Paper PDF</label>
              <input
                type="file"
                accept=".pdf"
                onChange={e => setQuestionPaper(e.target.files[0])}
                className="border rounded-lg px-3 py-2 text-sm w-full"
                required
              />
            </div>
            <button
              type="submit"
              className="bg-blue-900 text-white px-6 py-2 rounded-lg text-sm hover:bg-blue-800"
            >
              Upload
            </button>
          </form>
        </div>

        {soe && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h2 className="font-semibold text-gray-700">
                Current SoE ({soe.items.length} criteria)
              </h2>
            </div>
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">Q No.</th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">Criterion</th>
                  <th className="text-left px-6 py-3 text-xs text-gray-500 uppercase">Marks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {soe.items.map((item, i) => (
                  <tr key={i}>
                    <td className="px-6 py-3 text-sm text-gray-600">Q{item.question_no}</td>
                    <td className="px-6 py-3 text-sm font-medium text-gray-800">{item.criterion_name}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{item.max_marks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden mt-6">
            <div className="px-6 py-4 border-b">
              <h2 className="font-semibold text-gray-700">
                Stored Question Paper ({questions.length} questions)
              </h2>
            </div>
            <div className="divide-y divide-gray-100">
              {questions.map(question => (
                <div key={question.question_no} className="px-6 py-4">
                  <p className="font-medium text-gray-800">Q{question.question_no}</p>
                  <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{question.question_text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}