import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileText, Eye, EyeOff, Loader2, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '@/api/client'
import { useAuthStore } from '@/store/useAuthStore'

const requirements = [
  { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
  { label: 'Contains a number', test: (p: string) => /\d/.test(p) },
]

export default function Register() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.username || !form.email || !form.password) return
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const { data } = await authApi.register(form.username, form.email, form.password)
      setTokens(data.access_token, data.refresh_token)
      const me = await authApi.me()
      setUser(me.data)
      toast.success('Account created! Welcome aboard 🎉')
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#09090B] flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-up">

        <div className="flex flex-col items-center mb-8">
          <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center mb-3 shadow-glow-md">
            <FileText className="w-5 h-5 text-[#09090B]" />
          </div>
          <h1 className="text-xl font-bold text-white">Create account</h1>
          <p className="text-zinc-500 text-sm mt-1">Free forever. No credit card.</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label htmlFor="reg-username" className="label">Username</label>
            <input
              id="reg-username"
              type="text"
              autoComplete="username"
              className="input"
              placeholder="yourname"
              pattern="[a-zA-Z0-9_]{3,32}"
              title="3-32 alphanumeric characters or underscores"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          <div>
            <label htmlFor="reg-email" className="label">Email</label>
            <input
              id="reg-email"
              type="email"
              autoComplete="email"
              className="input"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="label">Password</label>
            <div className="relative">
              <input
                id="reg-password"
                type={show ? 'text' : 'password'}
                autoComplete="new-password"
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
            {/* Requirements */}
            {form.password && (
              <div className="mt-2 space-y-1">
                {requirements.map((r) => (
                  <div key={r.label} className="flex items-center gap-1.5 text-xs">
                    <CheckCircle2
                      className={`w-3.5 h-3.5 ${r.test(form.password) ? 'text-emerald-400' : 'text-zinc-600'}`}
                    />
                    <span className={r.test(form.password) ? 'text-zinc-400' : 'text-zinc-600'}>
                      {r.label}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            id="register-submit"
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center py-2.5"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-zinc-500 mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-white font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
