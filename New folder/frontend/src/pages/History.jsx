import { useEffect, useState } from 'react'
import client from '../api/client'

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get('/history')
      .then(({ data }) => setItems(data))
      .catch(() => setItems([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-center py-16 text-slate-400">Loading history…</p>

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold mb-8">Prediction History</h1>
      {items.length === 0 ? (
        <p className="text-slate-400">No predictions yet.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="text-left p-3">Date</th>
                <th className="text-left p-3">Risk</th>
                <th className="text-left p-3">Score</th>
                <th className="text-left p-3">Confidence</th>
                <th className="text-left p-3">Age</th>
                <th className="text-left p-3">Report</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id} className="border-t border-slate-800">
                  <td className="p-3">{new Date(row.created_at).toLocaleString()}</td>
                  <td className="p-3 font-medium">{row.prediction}</td>
                  <td className="p-3">{row.risk_score}</td>
                  <td className="p-3">{(row.confidence_score * 100).toFixed(1)}%</td>
                  <td className="p-3">{row.age}</td>
                  <td className="p-3">
                    <button
                      type="button"
                      className="text-accent text-xs hover:underline"
                      onClick={() =>
                        client.get(`/reports/prediction/${row.id}`, { responseType: 'blob' }).then((res) => {
                          const url = URL.createObjectURL(res.data)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = `hivcare_report_${row.id}.pdf`
                          a.click()
                          URL.revokeObjectURL(url)
                        })
                      }
                    >
                      PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
