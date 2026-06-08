import { useEffect, useState } from 'react'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import client from '../api/client'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const chartOpts = {
  responsive: true,
  plugins: { legend: { labels: { color: '#94a3b8' } } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
  },
}

const ROC_COLORS = ['#34d399', '#fbbf24', '#f87171']

export default function Dashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    client.get('/analytics').then(({ data: d }) => setData(d)).catch(() => setData(null))
  }, [])

  if (!data) {
    return <p className="text-center py-16 text-slate-400">Loading analytics…</p>
  }

  const dist = data.prediction_distribution || {}
  const pieData = {
    labels: Object.keys(dist).length ? Object.keys(dist) : ['No data'],
    datasets: [{
      data: Object.keys(dist).length ? Object.values(dist) : [1],
      backgroundColor: ['#34d399', '#fbbf24', '#f87171'],
    }],
  }

  const trend = data.risk_trends || []
  const lineData = {
    labels: trend.map((t) => t.date),
    datasets: [{ label: 'Predictions', data: trend.map((t) => t.count), borderColor: '#a78bfa', tension: 0.3 }],
  }

  const cm = data.charts?.confusion_matrix
  const barData = cm
    ? {
        labels: ['Low', 'Medium', 'High'].map((l) => `Actual ${l}`),
        datasets: ['Pred L', 'Pred M', 'Pred H'].map((label, j) => ({
          label,
          data: cm.map((row) => row[j]),
          backgroundColor: ROC_COLORS[j],
        })),
      }
    : null

  const roc = data.charts?.roc_curves
  const classNames = roc?.class_names || ['Low Risk', 'Medium Risk', 'High Risk']
  const rocData = roc?.fpr?.length
    ? {
        labels: roc.fpr[0]?.map((_, i) => i) || [],
        datasets: roc.fpr.map((fpr, idx) => ({
          label: classNames[idx] || `Class ${idx}`,
          data: (roc.tpr[idx] || []).map((tpr, i) => ({ x: fpr[i], y: tpr })),
          borderColor: ROC_COLORS[idx % 3],
          showLine: true,
          pointRadius: 0,
          parsing: false,
        })),
      }
    : null

  const metrics = data.model_metrics || {}

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold mb-8">Analytics Dashboard</h1>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-10">
        {[
          ['Predictions', data.user_statistics?.total_predictions],
          ['Accuracy', metrics.accuracy != null ? `${(metrics.accuracy * 100).toFixed(1)}%` : '—'],
          ['Precision', metrics.precision != null ? metrics.precision.toFixed(3) : '—'],
          ['Recall', metrics.recall != null ? metrics.recall.toFixed(3) : '—'],
          ['F1', metrics.f1_score != null ? metrics.f1_score.toFixed(3) : '—'],
          ['ROC-AUC', metrics.roc_auc != null ? metrics.roc_auc.toFixed(3) : '—'],
        ].map(([label, value]) => (
          <div key={label} className="p-4 rounded-xl bg-slate-900 border border-slate-800">
            <p className="text-xs text-slate-500 uppercase">{label}</p>
            <p className="text-xl font-bold mt-1">{value ?? '—'}</p>
          </div>
        ))}
      </div>

      {metrics.neural_network_accuracy != null && (
        <p className="text-sm text-slate-400 mb-6">
          TensorFlow MLP baseline accuracy: {(metrics.neural_network_accuracy * 100).toFixed(1)}%
        </p>
      )}

      <div className="grid md:grid-cols-2 gap-8">
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
          <h2 className="font-semibold mb-4">Risk Distribution (Pie)</h2>
          <Doughnut data={pieData} options={{ plugins: { legend: { position: 'bottom' } } }} />
        </div>
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
          <h2 className="font-semibold mb-4">Prediction Trends</h2>
          <Line data={lineData} options={chartOpts} />
        </div>
        {rocData && (
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
            <h2 className="font-semibold mb-4">ROC Curves</h2>
            <Line
              data={rocData}
              options={{
                ...chartOpts,
                scales: {
                  x: { type: 'linear', min: 0, max: 1, title: { display: true, text: 'FPR' } },
                  y: { min: 0, max: 1, title: { display: true, text: 'TPR' } },
                },
              }}
            />
          </div>
        )}
        {barData && (
          <div className={`p-6 rounded-xl bg-slate-900 border border-slate-800 ${rocData ? '' : 'md:col-span-2'}`}>
            <h2 className="font-semibold mb-4">Confusion Matrix (Bar)</h2>
            <Bar data={barData} options={chartOpts} />
          </div>
        )}
      </div>
    </div>
  )
}
