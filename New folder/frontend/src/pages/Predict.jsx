import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'

export default function Predict() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    age: 30,
    gender: 'male',
    bmi: 24,
    cd4_count: 500,
    sti_history: 0,
    behavioral_score: 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await client.post('/predict', {
        ...form,
        age: Number(form.age),
        bmi: Number(form.bmi),
        cd4_count: Number(form.cd4_count),
        sti_history: Number(form.sti_history),
        behavioral_score: Number(form.behavioral_score),
      })
      sessionStorage.setItem('lastPrediction', JSON.stringify({ ...data, prediction_id: data.prediction_id }))
      navigate('/results')
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Ensure the ML model is trained.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold mb-2">HIV Risk Assessment</h1>
      <p className="text-slate-400 text-sm mb-8">Enter health and behavioral information below.</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        {error && <p className="text-red-400 text-sm">{error}</p>}

        <label className="block">
          <span className="text-sm text-slate-400">Age</span>
          <input
            type="number"
            min={1}
            max={120}
            value={form.age}
            onChange={(e) => update('age', e.target.value)}
            className="mt-1 w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
          />
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">Gender</span>
          <select
            value={form.gender}
            onChange={(e) => update('gender', e.target.value)}
            className="mt-1 w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">BMI</span>
          <input
            type="number"
            step="0.1"
            min={10}
            max={60}
            value={form.bmi}
            onChange={(e) => update('bmi', e.target.value)}
            className="mt-1 w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
          />
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">CD4 Count</span>
          <input
            type="number"
            min={0}
            max={2000}
            value={form.cd4_count}
            onChange={(e) => update('cd4_count', e.target.value)}
            className="mt-1 w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
          />
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">STI History</span>
          <select
            value={form.sti_history}
            onChange={(e) => update('sti_history', e.target.value)}
            className="mt-1 w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
          >
            <option value={0}>No</option>
            <option value={1}>Yes</option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">Behavioral Risk Score (0–5)</span>
          <input
            type="range"
            min={0}
            max={5}
            value={form.behavioral_score}
            onChange={(e) => update('behavioral_score', e.target.value)}
            className="mt-1 w-full"
          />
          <span className="text-accent">{form.behavioral_score}</span>
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 rounded-xl bg-primary font-semibold hover:bg-primary-dark disabled:opacity-50"
        >
          {loading ? 'Analyzing…' : 'Predict Risk'}
        </button>
      </form>
    </div>
  )
}
