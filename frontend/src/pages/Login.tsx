import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileText, Eye, EyeOff, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '@/api/client'
import { useAuthStore } from '@/store/useAuthStore'

export default function Login() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [form, setForm] = useState({ username: '', password: '' })
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.username || !form.password) return
    setLoading(true)
    try {
      const { data } = await authApi.login(form.username, form.password)
      setTokens(data.access_token, data.refresh_token)
      // Fetch user info
      const me = await authApi.me()
      setUser(me.data)
      toast.success(`Welcome back, ${me.data.username}!`)
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Login failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#09090B] flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-up">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center mb-3 shadow-glow-md">
            <FileText className="w-5 h-5 text-[#09090B]" />
          </div>
          <h1 className="text-xl font-bold text-white">Sign in</h1>
          <p className="text-zinc-500 text-sm mt-1">to your Resume Builder account</p>
        </div>

        {/* Card */}
        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label htmlFor="username" className="label">Username</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              className="input"
              placeholder="yourname"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="label">Password</label>
            <div className="relative">
              <input
                id="password"
                type={show ? 'text' : 'password'}
                autoComplete="current-password"
                className="input pr-10"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
              <button
                type="button"
                onClick={() => setShow(!show)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                tabIndex={-1}
              >
                {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            id="login-submit"
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center py-2.5"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-sm text-zinc-500 mt-4">
          Don't have an account?{' '}
          <Link to="/register" className="text-white font-medium hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}
