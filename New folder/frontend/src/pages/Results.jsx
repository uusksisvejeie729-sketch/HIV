import { Link } from 'react-router-dom'
import client from '../api/client'
import ShapChart from '../components/ShapChart'

const riskColors = {
  'Low Risk': 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10',
  'Medium Risk': 'text-amber-400 border-amber-500/50 bg-amber-500/10',
  'High Risk': 'text-red-400 border-red-500/50 bg-red-500/10',
}

export default function Results() {
  const raw = sessionStorage.getItem('lastPrediction')
  if (!raw) {
    return (
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <p className="text-slate-400 mb-4">No prediction results yet.</p>
        <Link to="/predict" className="text-accent hover:underline">Run assessment</Link>
      </div>
    )
  }

  const data = JSON.parse(raw)
  const colorClass = riskColors[data.risk_level] || riskColors['Medium Risk']

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold mb-8 text-center">Assessment Results</h1>

      <div className={`rounded-2xl border p-8 text-center mb-6 ${colorClass}`}>
        <p className="text-sm uppercase tracking-wide mb-2">Risk Category</p>
        <p className="text-3xl font-bold">{data.risk_level}</p>
        <p className="mt-4 text-slate-300">
          Confidence: <strong>{(data.confidence_score * 100).toFixed(1)}%</strong>
        </p>
        <p className="text-slate-400 text-sm mt-1">Risk score: {data.risk_score}</p>
      </div>

      <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
        <h2 className="font-semibold mb-2">Recommendation</h2>
        <p className="text-slate-300 text-sm leading-relaxed">{data.recommendation}</p>
      </div>

      {data.explanation?.class_probabilities && (
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
          <h2 className="font-semibold mb-3">Class Probabilities</h2>
          <ul className="space-y-2 text-sm">
            {Object.entries(data.explanation.class_probabilities).map(([label, prob]) => (
              <li key={label} className="flex justify-between text-slate-400">
                <span>{label}</span>
                <span>{(prob * 100).toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.explanation?.shap && (
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
          <h2 className="font-semibold mb-3">SHAP Explainability</h2>
          <ShapChart shap={data.explanation.shap} />
        </div>
      )}

      {data.prediction_id && (
        <button
          type="button"
          onClick={() => client.get(`/reports/prediction/${data.prediction_id}`, { responseType: 'blob' }).then((res) => {
            const url = URL.createObjectURL(res.data)
            const a = document.createElement('a')
            a.href = url
            a.download = `hivcare_report_${data.prediction_id}.pdf`
            a.click()
            URL.revokeObjectURL(url)
          })}
          className="w-full mb-6 py-3 rounded-lg border border-primary text-primary hover:bg-primary/10"
        >
          Download PDF Report
        </button>
      )}

      <div className="flex gap-4 justify-center">
        <Link to="/predict" className="px-6 py-2 rounded-lg border border-slate-600 hover:bg-slate-800">
          New Assessment
        </Link>
        <Link to="/history" className="px-6 py-2 rounded-lg bg-primary hover:bg-primary-dark">
          View History
        </Link>
      </div>
    </div>
  )
}
