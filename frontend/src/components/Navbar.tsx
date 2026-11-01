import { Link, useNavigate } from 'react-router-dom'
import { FileText, LayoutDashboard, LogOut, Moon, Sun } from 'lucide-react'
import { useAuthStore } from '@/store/useAuthStore'
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [dark, setDark] = useState(true)

  useEffect(() => {
    document.documentElement.classList.toggle('light', !dark)
  }, [dark])

  const handleLogout = () => {
    logout()
    toast.success('Logged out')
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-[#27272A] bg-[#09090B]/80 glass dark:border-[#27272A] light:border-[#E4E4E7] light:bg-white/80">
      <div className="max-w-screen-xl mx-auto px-4 h-14 flex items-center justify-between">

        {/* Brand */}
        <Link to="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-white flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <FileText className="w-4 h-4 text-[#09090B]" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-white light:text-[#09090B]">
            Resume<span className="text-zinc-400 light:text-zinc-500">Builder</span>
          </span>
          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 light:bg-zinc-100 text-zinc-400 light:text-zinc-500 border border-[#27272A] light:border-[#E4E4E7]">
            AI
          </span>
        </Link>

        {/* Right side */}
        <div className="flex items-center gap-1">
          <Link to="/dashboard" className="btn-ghost text-xs hidden sm:inline-flex">
            <LayoutDashboard className="w-3.5 h-3.5" />
            Dashboard
          </Link>

          {/* Theme toggle */}
          <button
            id="theme-toggle"
            onClick={() => setDark(!dark)}
            className="btn-ghost w-9 h-9 p-0 justify-center"
            aria-label="Toggle theme"
          >
            {dark
              ? <Sun className="w-4 h-4" />
              : <Moon className="w-4 h-4" />
            }
          </button>

          {/* User info */}
          {user && (
            <div className="flex items-center gap-2 ml-2 pl-3 border-l border-[#27272A] light:border-[#E4E4E7]">
              <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center">
                <span className="text-[#09090B] font-bold text-xs">
                  {user.username[0].toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-zinc-400 hidden sm:block">{user.username}</span>
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
