import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Trash2, Copy, FileText, Loader2, Target, Cpu, Sparkles, BrainCircuit, ArrowRight, Upload } from 'lucide-react'
import toast from 'react-hot-toast'
import { resumeApi } from '@/api/client'
import { useAuthStore } from '@/store/useAuthStore'
import { useResumeStore } from '@/store/useResumeStore'

interface ResumeListItem {
  id: string; title: string; job_role: string; company: string
  template_key: string; verified: boolean; verification_score: number
  ats_score: number; jd_match_score: number; has_pdf: boolean
  created_at: string; updated_at: string
}

function ScoreBadge({ score }: { score: number }) {
  const cls = score >= 80 ? 'badge-score-high' : score >= 60 ? 'badge-score-mid' : 'badge-score-low'
  return <span className={`badge ${cls}`}>{score}</span>
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const { setResume } = useResumeStore()
  const navigate = useNavigate()
  const [resumes, setResumes] = useState<ResumeListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await resumeApi.list()
      setResumes(data)
    } catch {
      toast.error('Failed to load resumes.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this resume? This cannot be undone.')) return
    setDeletingId(id)
    try {
      await resumeApi.delete(id)
      toast.success('Resume deleted')
      setResumes((r) => r.filter((x) => x.id !== id))
    } catch {
      toast.error('Failed to delete')
    } finally {
      setDeletingId(null)
    }
  }

  const handleDuplicate = async (id: string) => {
    try {
      const { data } = await resumeApi.duplicate(id)
      toast.success('Resume duplicated')
      setResumes((r) => [data, ...r])
    } catch {
      toast.error('Failed to duplicate')
    }
  }

  const handleNew = () => {
    setResume({ id: null, title: '', job_role: '', company: '', job_description: '', latex_output: '' })
    navigate('/editor/new')
  }

  return (
    <div className="min-h-screen bg-[#09090B] px-4 py-8">
      <div className="max-w-screen-xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {user ? `Welcome back, ${user.username.split('_')[0]}` : 'My Resumes'}
            </h1>
            <p className="text-zinc-500 text-sm mt-0.5">
              {resumes.length} resume{resumes.length !== 1 ? 's' : ''} · AI-powered career tools
            </p>
          </div>
          <div className="flex gap-2">
            <button onClick={handleNew} id="new-resume-btn" className="btn-ghost text-xs">
              <Plus className="w-4 h-4" /> New
            </button>
            <button
              id="upload-resume-btn"
              onClick={() => navigate('/upload-resume')}
              className="btn-secondary text-xs"
            >
              <Upload className="w-4 h-4" /> Upload Resume
            </button>
            <button
              id="jd-resume-btn"
              onClick={() => navigate('/jd-resume')}
              className="btn-primary"
            >
              <BrainCircuit className="w-4 h-4" /> Create with JD
            </button>
          </div>
        </div>

        {/* ── Feature Cards Row ─────────────────────────────────────────── */}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          {/* JD Resume */}
          <div
            onClick={() => navigate('/jd-resume')}
            className="relative cursor-pointer rounded-xl border border-violet-500/25
                       bg-gradient-to-br from-violet-950/40 via-[#09090B] to-cyan-950/30
                       p-5 flex items-start gap-4 hover:border-violet-500/50
                       hover:shadow-[0_0_24px_rgba(139,92,246,0.1)] transition-all duration-300 group"
          >
            <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/30
                            flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <Sparkles className="w-5 h-5 text-violet-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h2 className="font-bold text-white text-sm">Create with Job Description</h2>
                <span className="text-[10px] font-mono bg-violet-500/10 text-violet-400 border border-violet-500/20 px-1.5 py-0.5 rounded-full">AI</span>
              </div>
              <p className="text-zinc-500 text-xs leading-relaxed">
                Paste a JD — 7 agents research, generate &amp; review your resume.
              </p>
            </div>
            <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-violet-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-0.5" />
          </div>

          {/* Upload Resume */}
          <div
            onClick={() => navigate('/upload-resume')}
            className="relative cursor-pointer rounded-xl border border-emerald-500/20
                       bg-gradient-to-br from-emerald-950/30 via-[#09090B] to-cyan-950/20
                       p-5 flex items-start gap-4 hover:border-emerald-500/40
                       hover:shadow-[0_0_24px_rgba(16,185,129,0.08)] transition-all duration-300 group"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30
                            flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <Upload className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h2 className="font-bold text-white text-sm">Import Existing Resume</h2>
                <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full">NEW</span>
              </div>
              <p className="text-zinc-500 text-xs leading-relaxed">
                Upload a PDF — AI extracts your profile automatically.
              </p>
            </div>
            <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-0.5" />
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Total Resumes', value: resumes.length, icon: FileText },
            { label: 'Verified',      value: resumes.filter(r => r.verified).length, icon: Target },
            { label: 'Avg ATS Score', value: resumes.length ? Math.round(resumes.reduce((a, r) => a + r.ats_score, 0) / resumes.length) : '—', icon: Cpu },
            { label: 'With PDF',      value: resumes.filter(r => r.has_pdf).length, icon: FileText },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-zinc-500">{label}</span>
                <Icon className="w-3.5 h-3.5 text-zinc-600" />
              </div>
              <div className="text-2xl font-bold font-mono text-white">{value}</div>
            </div>
          ))}
        </div>

        {/* Resume grid */}
        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3].map(i => (
              <div key={i} className="card p-5 space-y-3">
                <div className="skeleton h-4 w-3/4" />
                <div className="skeleton h-3 w-1/2" />
                <div className="skeleton h-3 w-2/3" />
              </div>
            ))}
          </div>
        ) : resumes.length === 0 ? (
          <div className="card p-16 text-center">
            <FileText className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h2 className="text-lg font-semibold text-white mb-2">No resumes yet</h2>
            <p className="text-zinc-500 text-sm mb-6">
              Create your first AI-powered resume in under 2 minutes.
            </p>
            <button onClick={handleNew} className="btn-primary mx-auto">
              <Plus className="w-4 h-4" /> Create First Resume
            </button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {resumes.map((resume) => (
              <div key={resume.id} className="card-hover p-5 group">
                <Link to={`/editor/${resume.id}`} className="block mb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <h3 className="font-semibold text-sm text-white truncate">{resume.job_role || resume.title || 'Untitled'}</h3>
                      <p className="text-xs text-zinc-500 truncate mt-0.5">{resume.company || '—'}</p>
                    </div>
                    <ScoreBadge score={resume.ats_score || resume.verification_score} />
                  </div>
                </Link>

                {/* Meta */}
                <div className="flex flex-wrap gap-x-3 gap-y-1 mb-4">
                  <span className="text-xs text-zinc-600 font-mono">{resume.template_key}</span>
                  {resume.verified && <span className="text-xs text-emerald-500">✓ Verified</span>}
                  {resume.has_pdf && <span className="text-xs text-zinc-500">PDF ready</span>}
                </div>

                <div className="text-xs text-zinc-600 mb-4">
                  {new Date(resume.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </div>

                {/* Actions */}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Link to={`/editor/${resume.id}`} className="btn-secondary text-xs py-1.5 px-2.5 flex-1 justify-center">
                    Open Editor
                  </Link>
                  <button onClick={() => handleDuplicate(resume.id)} className="btn-ghost w-8 h-8 p-0 justify-center" title="Duplicate">
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(resume.id)}
                    className="btn-ghost w-8 h-8 p-0 justify-center hover:text-red-400"
                    title="Delete"
                    disabled={deletingId === resume.id}
                  >
                    {deletingId === resume.id
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : <Trash2 className="w-3.5 h-3.5" />
                    }
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
