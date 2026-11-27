import { Link, useNavigate } from 'react-router-dom'
import { FileText, LayoutDashboard, LogOut, Moon, Sun, UserRound } from 'lucide-react'
import { useAuthStore } from '@/store/useAuthStore'
import { useState, useLayoutEffect } from 'react'
import toast from 'react-hot-toast'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [dark, setDark] = useState(() => window.localStorage.getItem('app-theme') === 'dark')

  useLayoutEffect(() => {
    document.documentElement.classList.toggle('light', !dark)
  }, [dark])

  const toggleTheme = () => {
    setDark((current) => {
      const next = !current
      window.localStorage.setItem('app-theme', next ? 'dark' : 'light')
      return next
    })
  }

  const handleLogout = () => {
    logout()
    toast.success('Logged out')
    navigate('/login')
  }

  return (
    <nav className="app-navbar sticky top-0 z-50 border-b glass">
      <div className="max-w-screen-xl mx-auto px-4 h-16 flex items-center justify-between">

        {/* Brand */}
        <Link to="/dashboard" className="flex items-center gap-2.5 group">
          <div className="app-navbar-mark w-8 h-8 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform">
            <FileText className="w-4 h-4" />
          </div>
          <span className="font-semibold text-sm tracking-tight">
            Resume<span className="app-navbar-muted">Builder</span>
          </span>
          <span className="app-navbar-tag font-mono text-[10px] px-1.5 py-0.5 rounded">
            AI
          </span>
        </Link>

        {/* Right side */}
        <div className="flex items-center gap-1">
          <Link to="/dashboard" className="btn-ghost text-xs hidden sm:inline-flex">
            <LayoutDashboard className="w-3.5 h-3.5" />
            Dashboard
          </Link>
          <Link to="/profile" className="btn-ghost text-xs">
            <UserRound className="w-3.5 h-3.5" />
            Profile
          </Link>

          {/* Theme toggle */}
          <button
            id="theme-toggle"
            onClick={toggleTheme}
            className="btn-ghost w-9 h-9 p-0 justify-center"
            aria-label={`Switch to ${dark ? 'light' : 'dark'} mode`}
            title={`Switch to ${dark ? 'light' : 'dark'} mode`}
          >
            {dark
              ? <Sun className="w-4 h-4" />
              : <Moon className="w-4 h-4" />
            }
          </button>

          {/* User info */}
          {user && (
            <div className="app-navbar-user flex items-center gap-2 ml-2 pl-3">
              <div className="app-navbar-avatar w-8 h-8 rounded-full flex items-center justify-center">
                <span className="font-bold text-xs">
                  {user.username[0].toUpperCase()}
                </span>
              </div>
              <span className="app-navbar-muted text-xs hidden sm:block">{user.username}</span>
              <button
                id="logout-btn"
                onClick={handleLogout}
                className="btn-ghost w-8 h-8 p-0 justify-center text-zinc-500 hover:text-red-400"
                aria-label="Logout"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
