import { Bar } from 'react-chartjs-2'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  Tooltip,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

export default function ShapChart({ shap }) {
  const items = shap?.feature_importance || []
  if (!items.length) return null

  const data = {
    labels: items.map((i) => i.feature),
    datasets: [
      {
        label: 'SHAP value',
        data: items.map((i) => i.shap_value),
        backgroundColor: items.map((i) =>
          i.shap_value >= 0 ? 'rgba(248, 113, 113, 0.7)' : 'rgba(52, 211, 153, 0.7)'
        ),
      },
    ],
  }

  return (
    <div className="h-64">
      <Bar
        data={data}
        options={{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
            y: { ticks: { color: '#94a3b8', font: { size: 10 } } },
          },
        }}
      />
    </div>
  )
}
