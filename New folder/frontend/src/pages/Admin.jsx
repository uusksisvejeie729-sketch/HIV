import { useEffect, useState } from 'react'
import client from '../api/client'

export default function Admin() {
  const [users, setUsers] = useState([])
  const [predictions, setPredictions] = useState([])
  const [activity, setActivity] = useState([])

  useEffect(() => {
    Promise.all([
      client.get('/admin/users'),
      client.get('/admin/predictions'),
      client.get('/admin/activity'),
    ]).then(([u, p, a]) => {
      setUsers(u.data)
      setPredictions(p.data)
      setActivity(a.data)
    })
  }, [])

  const exportCsv = async () => {
    const { data } = await client.get('/admin/export/predictions', { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `hivcare_predictions_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <button
          type="button"
          onClick={exportCsv}
          className="px-4 py-2 rounded-lg bg-primary text-sm font-medium hover:bg-primary-dark"
        >
          Export Reports (CSV)
        </button>
      </div>

      <section className="mb-10">
        <h2 className="font-semibold mb-4">Users ({users.length})</h2>
        <div className="overflow-x-auto rounded-xl border border-slate-800 text-sm">
          <table className="w-full">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="p-3 text-left">ID</th>
                <th className="p-3 text-left">Name</th>
                <th className="p-3 text-left">Email</th>
                <th className="p-3 text-left">Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-slate-800">
                  <td className="p-3">{u.id}</td>
                  <td className="p-3">{u.name}</td>
                  <td className="p-3">{u.email}</td>
                  <td className="p-3">{u.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mb-10">
        <h2 className="font-semibold mb-4">Recent Predictions</h2>
        <div className="overflow-x-auto rounded-xl border border-slate-800 text-sm max-h-64 overflow-y-auto">
          <table className="w-full">
            <thead className="bg-slate-900 text-slate-400 sticky top-0">
              <tr>
                <th className="p-3 text-left">ID</th>
                <th className="p-3 text-left">User</th>
                <th className="p-3 text-left">Result</th>
                <th className="p-3 text-left">Time</th>
                <th className="p-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {predictions.slice(0, 50).map((p) => (
                <tr key={p.id} className="border-t border-slate-800">
                  <td className="p-3">{p.id}</td>
                  <td className="p-3">{p.user_id}</td>
                  <td className="p-3">{p.prediction}</td>
                  <td className="p-3">{new Date(p.created_at).toLocaleString()}</td>
                  <td className="p-3">
                    <button
                      type="button"
                      className="text-red-400 text-xs hover:underline"
                      onClick={async () => {
                        await client.delete(`/admin/predictions/${p.id}`)
                        setPredictions((prev) => prev.filter((x) => x.id !== p.id))
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="font-semibold mb-4">System Activity</h2>
        <ul className="space-y-2 text-sm">
          {activity.slice(0, 30).map((log) => (
            <li key={log.id} className="flex justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span>{log.activity}</span>
              <span className="text-slate-500">{new Date(log.timestamp).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
