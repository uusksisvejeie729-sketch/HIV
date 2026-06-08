import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [resetEmail, setResetEmail] = useState('')
  const [resetToken, setResetToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [resetMsg, setResetMsg] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      navigate('/predict')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  const requestReset = async () => {
    try {
      const { data } = await client.post('/auth/reset-password/request', { email: resetEmail })
      setResetMsg(data.reset_token ? `Demo token: ${data.reset_token}` : data.message)
    } catch {
      setResetMsg('Request sent if email exists')
    }
  }

  const confirmReset = async () => {
    try {
      await client.post('/auth/reset-password/confirm', {
        email: resetEmail,
        token: resetToken,
        new_password: newPassword,
      })
      setResetMsg('Password updated. You can log in now.')
    } catch (err) {
      setResetMsg(err.response?.data?.detail || 'Reset failed')
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-6">Login</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
        />
        <input
          type="password"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700"
        />
        <button type="submit" className="w-full py-3 rounded-lg bg-primary font-semibold hover:bg-primary-dark">
          Login
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        No account? <Link to="/register" className="text-accent">Register</Link>
      </p>

      <details className="mt-8 text-sm">
        <summary className="cursor-pointer text-slate-400">Reset password</summary>
        <div className="mt-4 space-y-3">
          <input
            type="email"
            placeholder="Email"
            value={resetEmail}
            onChange={(e) => setResetEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
          />
          <button type="button" onClick={requestReset} className="text-accent hover:underline">
            Request reset token
          </button>
          <input
            type="text"
            placeholder="Reset token"
            value={resetToken}
            onChange={(e) => setResetToken(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
          />
          <input
            type="password"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
          />
          <button type="button" onClick={confirmReset} className="text-accent hover:underline">
            Confirm reset
          </button>
          {resetMsg && <p className="text-slate-400 break-all">{resetMsg}</p>}
        </div>
      </details>
    </div>
  )
}
