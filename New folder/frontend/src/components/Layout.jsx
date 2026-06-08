import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navClass = ({ isActive }) =>
  `px-3 py-2 rounded-lg text-sm font-medium transition ${
    isActive ? 'bg-primary text-white' : 'text-slate-300 hover:bg-slate-800'
  }`

export default function Layout() {
  const { user, logout, isAdmin } = useAuth()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-wrap items-center justify-between gap-4">
          <Link to="/" className="text-xl font-bold text-primary-light">
            HIVCare <span className="text-accent">AI</span>
          </Link>
          <nav className="flex flex-wrap gap-1">
            <NavLink to="/" end className={navClass}>Home</NavLink>
            <NavLink to="/about" className={navClass}>About</NavLink>
            {user && (
              <>
                <NavLink to="/predict" className={navClass}>Predict</NavLink>
                <NavLink to="/dashboard" className={navClass}>Dashboard</NavLink>
                <NavLink to="/history" className={navClass}>History</NavLink>
                {isAdmin && <NavLink to="/admin" className={navClass}>Admin</NavLink>}
              </>
            )}
          </nav>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-slate-400">{user.name}</span>
                <button
                  type="button"
                  onClick={logout}
                  className="text-sm px-4 py-2 rounded-lg border border-slate-600 hover:bg-slate-800"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm px-4 py-2 rounded-lg hover:bg-slate-800">Login</Link>
                <Link to="/register" className="text-sm px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-slate-800 py-6 text-center text-sm text-slate-500">
        HIVCare AI — NUTECH · Not a substitute for professional medical diagnosis.
      </footer>
    </div>
  )
}
