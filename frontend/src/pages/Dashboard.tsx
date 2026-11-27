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
    <main className="app-page dashboard-page">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div>
            <span className="dashboard-kicker">YOUR WORKSPACE</span>
            <h1 className="dashboard-title">
              {user ? `Welcome back, ${user.username.split('_')[0]}` : 'My Resumes'}
            </h1>
            <p className="dashboard-subtitle">
              Your next opportunity starts with a clear story.
            </p>
          </div>
          <div className="dashboard-actions">
            <button onClick={handleNew} id="new-resume-btn" className="btn-secondary text-xs">
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
        </header>

        <section className="dashboard-feature-grid" aria-label="Resume tools">
          <Link to="/jd-resume" className="dashboard-feature-card">
            <span className="dashboard-feature-icon"><Sparkles aria-hidden="true" /></span>
            <span className="dashboard-feature-copy">
              <span className="dashboard-feature-heading">
                <strong>Create with Job Description</strong>
                <span className="dashboard-feature-tag">AI</span>
              </span>
              <span className="dashboard-feature-description">
                Add a job description, choose a format, and tailor your saved profile.
              </span>
            </span>
            <ArrowRight className="dashboard-feature-arrow" aria-hidden="true" />
          </Link>

          <Link to="/upload-resume" className="dashboard-feature-card">
            <span className="dashboard-feature-icon"><Upload aria-hidden="true" /></span>
            <span className="dashboard-feature-copy">
              <span className="dashboard-feature-heading">
                <strong>Import Existing Resume</strong>
                <span className="dashboard-feature-tag">NEW</span>
              </span>
              <span className="dashboard-feature-description">
                Upload a PDF — AI extracts your profile automatically.
              </span>
            </span>
            <ArrowRight className="dashboard-feature-arrow" aria-hidden="true" />
          </Link>
        </section>

        <section className="dashboard-stats" aria-label="Resume overview">
          {[
            { label: 'Total resumes', value: resumes.length, icon: FileText },
            { label: 'Verified', value: resumes.filter(r => r.verified).length, icon: Target },
            { label: 'Average ATS score', value: resumes.length ? Math.round(resumes.reduce((a, r) => a + r.ats_score, 0) / resumes.length) : '—', icon: Cpu },
            { label: 'PDF ready', value: resumes.filter(r => r.has_pdf).length, icon: FileText },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="dashboard-stat">
              <span className="dashboard-stat-label">{label}</span>
              <Icon aria-hidden="true" />
              <strong>{value}</strong>
            </div>
          ))}
        </section>

        <div className="dashboard-section-heading">
          <div>
            <span className="dashboard-kicker">YOUR DOCUMENTS</span>
            <h2>Your resumes</h2>
          </div>
          <span>{resumes.length} resume{resumes.length !== 1 ? 's' : ''}</span>
        </div>

        {loading ? (
          <div className="dashboard-resume-grid">
            {[1,2,3].map(i => (
              <div key={i} className="dashboard-resume-card dashboard-loading-card">
                <div className="skeleton h-4 w-3/4" />
                <div className="skeleton h-3 w-1/2" />
                <div className="skeleton h-3 w-2/3" />
              </div>
            ))}
          </div>
        ) : resumes.length === 0 ? (
          <div className="dashboard-empty">
            <span className="dashboard-empty-icon"><FileText aria-hidden="true" /></span>
            <h2>No resumes yet</h2>
            <p>
              Create your first AI-powered resume in under 2 minutes.
            </p>
            <button onClick={handleNew} className="btn-primary">
              <Plus className="w-4 h-4" /> Create First Resume
            </button>
          </div>
        ) : (
          <div className="dashboard-resume-grid">
            {resumes.map((resume) => (
              <article key={resume.id} className="dashboard-resume-card">
                <Link to={`/editor/${resume.id}`} className="dashboard-resume-main">
                  <div className="dashboard-resume-icon"><FileText aria-hidden="true" /></div>
                  <div className="dashboard-resume-title">
                    <h3>{resume.job_role || resume.title || 'Untitled'}</h3>
                    <p>{resume.company || 'No company added'}</p>
                  </div>
                  <ScoreBadge score={resume.ats_score || resume.verification_score} />
                </Link>

                <div className="dashboard-resume-meta">
                  <span>{resume.template_key}</span>
                  {resume.verified && <span className="dashboard-meta-verified">✓ Verified</span>}
                  {resume.has_pdf && <span>PDF ready</span>}
                </div>

                <div className="dashboard-resume-date">
                  {new Date(resume.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </div>

                <div className="dashboard-resume-actions">
                  <Link to={`/editor/${resume.id}`} className="dashboard-open-link">
                    Open editor <ArrowRight aria-hidden="true" />
                  </Link>
                  <button onClick={() => handleDuplicate(resume.id)} className="btn-ghost w-8 h-8 p-0 justify-center" aria-label={`Duplicate ${resume.job_role || resume.title || 'resume'}`} title="Duplicate">
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(resume.id)}
                    className="btn-ghost w-8 h-8 p-0 justify-center hover:text-red-400"
                    aria-label={`Delete ${resume.job_role || resume.title || 'resume'}`}
                    title="Delete"
                    disabled={deletingId === resume.id}
                  >
                    {deletingId === resume.id
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : <Trash2 className="w-3.5 h-3.5" />
                    }
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
