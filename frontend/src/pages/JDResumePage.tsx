import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, Building2, FileText, Sparkles, ArrowRight,
  CheckCircle2, Loader2, AlertCircle, Github, MinusCircle,
  BookOpen, ChevronDown, X, ExternalLink, Download
} from 'lucide-react'
import toast from 'react-hot-toast'
import { jdResumeApi, resumeApi } from '@/api/client'

interface PipelineStep {
  agent: string
  message: string
  percent: number
  data?: Record<string, unknown>
  ts?: string
  type?: string
  status?: 'running' | 'completed' | 'failed' | 'skipped'
}

const AGENT_META: Record<string, { label: string }> = {
  web_search: { label: 'Web Search' },
  summary:    { label: 'Summary Agent' },
  profile:    { label: 'Profile Agent' },
  github:     { label: 'GitHub Agent' },
  generate:   { label: 'Generate Agent' },
  review:     { label: 'Review Agent' },
  pdf:        { label: 'PDF Agent' },
  save:       { label: 'Save' },
  pipeline:   { label: 'Pipeline' },
}

type StepStatus = 'running' | 'completed' | 'failed' | 'skipped'

function getStepStatus(step: PipelineStep, isRunning: boolean, isLast: boolean): StepStatus {
  if (isRunning && isLast && step.status !== 'failed' && step.status !== 'skipped') return 'running'
  if (step.status) return step.status
  return 'completed'
}

function StepStatusIcon({ status }: { status: StepStatus }) {
  if (status === 'failed') return <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-red-400" />
  if (status === 'skipped') return <MinusCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-400" />
  if (status === 'running') return <Loader2 className="w-4 h-4 flex-shrink-0 mt-0.5 animate-spin text-amber-400" />
  return <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-emerald-400" />
}

function stepStatusClasses(status: StepStatus) {
  if (status === 'failed') return 'bg-red-500/5 border-red-500/25'
  if (status === 'skipped' || status === 'running') return 'bg-amber-500/5 border-amber-500/25'
  return 'bg-emerald-500/5 border-emerald-500/25'
}

export default function JDResumePage() {
  const navigate = useNavigate()
  const abortRef = useRef<AbortController | null>(null)

  const [form, setForm] = useState({ jobRole: '', company: '', jobDescription: '' })
  const [running, setRunning]         = useState(false)
  const [done, setDone]               = useState(false)
  const [steps, setSteps]             = useState<PipelineStep[]>([])
  const [percent, setPercent]         = useState(0)
  const [finalData, setFinalData]     = useState<Record<string, unknown> | null>(null)
  const [showJd, setShowJd]           = useState(false)
  const [downloading, setDownloading] = useState(false)
  const savedResumeId = typeof finalData?.resume_id === 'string' ? finalData.resume_id : ''

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.jobRole.trim() || !form.company.trim() || !form.jobDescription.trim()) {
      toast.error('Please fill in all three fields.')
      return
    }

    setRunning(true)
    setDone(false)
    setSteps([])
    setPercent(0)
    setFinalData(null)

    const ctrl = new AbortController()
    abortRef.current = ctrl

    try {
      const result = await jdResumeApi.streamGenerate(
        form.jobRole,
        form.company,
        form.jobDescription,
        (step) => {
          const received = step as unknown as PipelineStep
          const s = received.type === 'error'
            ? { ...received, agent: 'pipeline', status: 'failed' as const }
            : received
          setSteps((prev) => {
            // Replace the last step from same agent if it's a progress update
            const last = prev[prev.length - 1]
            if (last && last.agent === s.agent && s.type !== 'done') {
              return [...prev.slice(0, -1), s]
            }
            return [...prev, s]
          })
          if (typeof s.percent === 'number') setPercent(s.percent)
        },
        ctrl.signal,
      )
      if (result.type !== 'error' && typeof result.resume_id !== 'string') {
        throw new Error('Resume was generated, but could not be saved. Please try again.')
      }
      setFinalData(result)
      setDone(true)
      if (result.type === 'error') {
        toast.error((result.message as string) || 'Pipeline failed.')
      } else {
        toast.success('Resume generated successfully! 🎉')
      }
    } catch (err: unknown) {
      if ((err as Error).name !== 'AbortError') {
        const message = (err as Error).message || 'Something went wrong.'
        setFinalData({ type: 'error', message })
        setSteps((prev) => prev.some((step) => step.agent === 'pipeline' && step.status === 'failed')
          ? prev
          : [...prev, { agent: 'pipeline', message, percent, status: 'failed' }])
        setDone(true)
        toast.error(message)
      }
    } finally {
      setRunning(false)
    }
  }

  const handleCancel = () => {
    abortRef.current?.abort()
    setRunning(false)
    toast('Pipeline cancelled.', { icon: '🛑' })
  }

  const handleViewResume = () => {
    if (!savedResumeId) {
      toast.error('This generated resume was not saved and cannot be opened in the editor.')
      return
    }
    navigate(`/editor/${savedResumeId}`)
  }

  const handleDownloadPdf = async () => {
    if (!savedResumeId) { toast.error('This generated resume was not saved and cannot be downloaded.'); return }
    setDownloading(true)
    try {
      const resp = await resumeApi.exportPdf(savedResumeId)
      const blob = new Blob([resp.data], { type: 'application/pdf' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `resume_${(finalData?.job_role as string || 'download').replace(/\s+/g, '_')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('PDF downloaded!')
    } catch (err: unknown) {
      toast.error('PDF download failed — the LaTeX may still be compiling. Try again in a moment.')
      console.error(err)
    } finally {
      setDownloading(false)
    }
  }

  const handleReset = () => {
    setDone(false)
    setSteps([])
    setPercent(0)
    setFinalData(null)
  }

  return (
    <div className="min-h-screen bg-[#09090B] px-4 py-10">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-violet-500/30
                          bg-violet-500/5 text-xs font-mono text-violet-400 mb-5">
            <Sparkles className="w-3 h-3" />
            7-Agent Agentic Pipeline
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white mb-3 tracking-tight">
            Create Resume with&nbsp;
            <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Job Description
            </span>
          </h1>
          <p className="text-zinc-500 text-sm max-w-xl mx-auto leading-relaxed">
            Our AI agents research the company, analyse your GitHub, and craft a tailored
            one-page resume — automatically.
          </p>
        </div>

        {/* Pipeline architecture mini-diagram */}
        <div className="card p-4 mb-8 overflow-x-auto">
          <p className="text-xs font-mono text-zinc-600 uppercase tracking-widest mb-3">Agent Flow</p>
          <div className="flex items-center gap-1.5 flex-wrap">
            {[
              { icon: Search,    label: 'Web Search' },
              { icon: BookOpen,  label: 'Summary' },
              { icon: FileText,  label: 'Profile' },
              { icon: Github,    label: 'GitHub Repos' },
              { icon: Sparkles,  label: 'Generate' },
              { icon: CheckCircle2, label: 'Review' },
              { icon: FileText,  label: 'PDF' },
            ].map(({ icon: Icon, label }, i) => (
              <div key={label} className="flex items-center gap-1.5">
                <div className="flex items-center gap-1 bg-white/5 border border-white/10 rounded-lg px-2 py-1">
                  <Icon className="w-3 h-3 text-zinc-400" />
                  <span className="text-[10px] text-zinc-400 font-mono whitespace-nowrap">{label}</span>
                </div>
                {i < 6 && <ArrowRight className="w-3 h-3 text-zinc-700 flex-shrink-0" />}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        {!running && !done && (
          <form onSubmit={handleSubmit} className="card p-6 space-y-5 animate-slide-up">
            {/* Job Role */}
            <div>
              <label htmlFor="jd-job-role" className="label">Job Role</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
                <input
                  id="jd-job-role"
                  type="text"
                  className="input pl-9"
                  placeholder="e.g. Senior Backend Engineer"
                  value={form.jobRole}
                  onChange={(e) => setForm({ ...form, jobRole: e.target.value })}
                  required
                />
              </div>
            </div>

            {/* Company Name */}
            <div>
              <label htmlFor="jd-company" className="label">Company Name</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
                <input
                  id="jd-company"
                  type="text"
                  className="input pl-9"
                  placeholder="e.g. Google, Stripe, Vercel…"
                  value={form.company}
                  onChange={(e) => setForm({ ...form, company: e.target.value })}
                  required
                />
              </div>
              <p className="text-[11px] text-zinc-600 mt-1">
                Our Web Search Agent will gather company intel from the web.
              </p>
            </div>

            {/* Job Description */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="jd-description" className="label mb-0">Job Description</label>
                <span className="text-[11px] text-zinc-600 font-mono">
                  {form.jobDescription.length}/10000
                </span>
              </div>
              <textarea
                id="jd-description"
                rows={8}
                className="textarea"
                placeholder="Paste the full job description here…&#10;&#10;The more detail you provide, the better the AI can tailor your resume."
                value={form.jobDescription}
                onChange={(e) => setForm({ ...form, jobDescription: e.target.value })}
                required
                minLength={10}
                maxLength={10000}
              />
            </div>

            <button
              id="jd-generate-btn"
              type="submit"
              className="btn-primary w-full justify-center py-3 text-base"
            >
              <Sparkles className="w-4 h-4" />
              Generate My Resume
              <ArrowRight className="w-4 h-4" />
            </button>

            <p className="text-center text-[11px] text-zinc-600">
              Make sure your profile (GitHub link, skills, education) is filled in for best results.
            </p>
          </form>
        )}

        {/* Pipeline Running */}
        {running && (
          <div className="card p-6 animate-slide-up">
            {/* Progress bar */}
            <div className="mb-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-white">
                  Running 7-Agent Pipeline…
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-zinc-400">{percent}%</span>
                  <button
                    onClick={handleCancel}
                    className="btn-ghost text-xs py-1 px-2 text-red-400 hover:text-red-300"
                  >
                    <X className="w-3 h-3" /> Cancel
                  </button>
                </div>
              </div>
              <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-violet-500 to-cyan-500 rounded-full transition-all duration-700"
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>

            {/* Steps */}
            <div className="space-y-2">
              {steps.map((step, i) => {
                const meta = AGENT_META[step.agent] || { label: step.agent }
                const isLast = i === steps.length - 1
                const status = getStepStatus(step, running, isLast)
                return (
                  <div
                    key={i}
                    className={`flex items-start gap-3 p-3 rounded-lg border text-sm transition-all duration-300 ${stepStatusClasses(status)}`}
                  >
                    <StepStatusIcon status={status} />
                    <div className="min-w-0">
                      <span className="font-mono text-[10px] uppercase tracking-wider mr-2 text-zinc-400">
                        {meta.label}
                      </span>
                      <span className="text-zinc-300">{step.message}</span>
                      {step.data && Object.keys(step.data).length > 0 && (
                        <div className="mt-1 text-[11px] text-zinc-600 font-mono">
                          {JSON.stringify(step.data).slice(0, 120)}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
              {/* Shimmer placeholder */}
              <div className="skeleton h-10 rounded-lg opacity-30" />
            </div>
          </div>
        )}

        {/* Done State */}
        {done && finalData && finalData.type !== 'error' && (
          <div className="card p-6 animate-slide-up">
            {/* Success header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-emerald-500/10 border border-emerald-500/30
                              flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h2 className="font-bold text-white">Resume Generated!</h2>
                <p className="text-zinc-500 text-xs">
                  {finalData.iterations as number} iteration{(finalData.iterations as number) !== 1 ? 's' : ''},&nbsp;
                  {finalData.repos_used as number} GitHub repo{(finalData.repos_used as number) !== 1 ? 's' : ''} used
                </p>
              </div>
              <div className="ml-auto">
                <div className={`text-2xl font-black font-mono ${
                  (finalData.review_score as number) >= 80 ? 'text-emerald-400' :
                  (finalData.review_score as number) >= 60 ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {finalData.review_score as number}
                  <span className="text-xs text-zinc-600">/100</span>
                </div>
                <div className="text-[10px] text-zinc-600 text-right">review score</div>
              </div>
            </div>

            {/* Completed steps summary */}
            <div className="mb-6 space-y-1.5">
              {steps.filter((s) => s.type !== 'done').map((step, i) => {
                const status = getStepStatus(step, false, false)
                return (
                  <div key={i} className={`flex items-center gap-2 text-xs ${
                    status === 'failed' ? 'text-red-400' :
                    status === 'skipped' ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    <StepStatusIcon status={status} />
                    <span className="text-zinc-500">{step.message}</span>
                  </div>
                )
              })}
            </div>

            {/* PDF status banner */}
            {finalData.pdf_success === false && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-300 mb-2">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                PDF compile issue — clicking Download will attempt recompilation.
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 flex-wrap">
              <button
                id="jd-download-pdf-btn"
                onClick={handleDownloadPdf}
                disabled={downloading || !savedResumeId}
                className="btn-primary flex-1 justify-center min-w-[140px]"
              >
                {downloading
                  ? <Loader2 className="w-4 h-4 animate-spin" />
                  : <Download className="w-4 h-4" />}
                {downloading ? 'Downloading…' : 'Download PDF'}
              </button>
              <button
                id="jd-view-resume-btn"
                onClick={handleViewResume}
                className="btn-secondary flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Open in Editor
              </button>
              <button
                onClick={handleReset}
                className="btn-ghost text-sm"
              >
                Generate Another
              </button>
            </div>
          </div>
        )}

        {/* Error state */}
        {done && finalData?.type === 'error' && (
          <div className="card p-6 border-red-500/30 bg-red-500/5 animate-slide-up">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <h2 className="font-bold text-white">Pipeline Failed</h2>
            </div>
            <p className="text-zinc-400 text-sm mb-4">{finalData.message as string}</p>
            {steps.filter((step) => step.status === 'failed').map((step, index) => (
              <div key={index} className="flex items-center gap-2 text-sm text-red-400 mb-4">
                <StepStatusIcon status="failed" />
                <span>{step.message}</span>
              </div>
            ))}
            <button onClick={handleReset} className="btn-secondary">
              Try Again
            </button>
          </div>
        )}

        {/* JD preview accordion */}
        {!running && !done && form.jobDescription && (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setShowJd(!showJd)}
              className="btn-ghost text-xs gap-1 text-zinc-600"
            >
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showJd ? 'rotate-180' : ''}`} />
              Preview job description
            </button>
            {showJd && (
              <div className="mt-2 card p-4 text-xs text-zinc-500 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                {form.jobDescription}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
