import { useState } from 'react'
import { Bot, X, Wand2, Target, FileSearch, Sparkles, Loader2, CheckCircle2, XCircle, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { agentApi } from '@/api/client'
import { useResumeStore } from '@/store/useResumeStore'
import clsx from 'clsx'

interface AgentStepUI { step: string; status: 'pending' | 'running' | 'done' | 'failed'; message: string }

interface DiffCard {
  id: string; type: string; original: string; proposed: string; confidence: number; accepted: boolean | null
}

export default function AIAgentPanel({ onClose, pipelineLog }: { onClose: () => void; pipelineLog: string[] }) {
  const { resume, setField } = useResumeStore()
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [steps, setSteps] = useState<AgentStepUI[]>([])
  const [diffs, setDiffs] = useState<DiffCard[]>([])
  const [bulletInput, setBulletInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [summaryResult, setSummaryResult] = useState('')
  const [atsResult, setAtsResult] = useState<any>(null)

  const addStep = (step: string, status: AgentStepUI['status'], message = '') =>
    setSteps(s => [...s, { step, status, message }])

  const run = async (agentType: string) => {
    setActiveAgent(agentType)
    setSteps([])
    setDiffs([])
    setAtsResult(null)
    setSummaryResult('')
    setLoading(true)

    try {
      if (agentType === 'bullet') {
        if (!bulletInput.trim()) { toast.error('Enter a bullet point first.'); setLoading(false); return }
        addStep('Parsing bullet', 'running', 'Analysing action verb & metrics…')
        const { data } = await agentApi.rewriteBullet(bulletInput, resume.job_role, resume.job_description)
        addStep('Parsing bullet', 'done', '')
        addStep('Applying XYZ formula', 'done', '')
        if (data.status === 'done' && data.result) {
          setDiffs([{
            id: crypto.randomUUID(),
            type: 'bullet',
            original: data.result.original,
            proposed: data.result.rewritten,
            confidence: data.result.confidence,
            accepted: null,
          }])
        }
      }

      else if (agentType === 'ats') {
        addStep('Fetching resume LaTeX', 'running', '')
        addStep('Fetching resume LaTeX', 'done', '')
        addStep('Auditing ATS compliance', 'running', 'Checking keyword density…')
        const { data } = await agentApi.atsAudit(resume.id || undefined, resume.latex_output, resume.job_description)
        addStep('Auditing ATS compliance', 'done', '')
        if (data.result) setAtsResult(data.result)
      }

      else if (agentType === 'summary') {
        addStep('Analysing profile & JD', 'running', '')
        addStep('Analysing profile & JD', 'done', '')
        addStep('Synthesising executive summary', 'running', '')
        const snap = {
          full_name: resume.full_name, skills: resume.skills,
          experience: resume.experience, education: resume.education,
          languages: resume.languages,
        }
        const { data } = await agentApi.generateSummary(resume.job_role, resume.job_description, 'senior', snap)
        addStep('Synthesising executive summary', 'done', '')
        if (data.result?.summary) {
          setSummaryResult(data.result.summary)
          setDiffs([{
            id: crypto.randomUUID(),
            type: 'summary',
            original: resume.professional_summary,
            proposed: data.result.summary,
            confidence: 0.85,
            accepted: null,
          }])
        }
      }

      else if (agentType === 'jd') {
        addStep('Parsing job description', 'running', 'Extracting hard & soft skills…')
        const { data } = await agentApi.tailorToJd(
          resume.id || 'new', resume.job_description, resume.job_role, resume.company
        )
        addStep('Parsing job description', 'done', '')
        addStep('Computing gap matrix', 'done', '')
        if (data.result) {
          const r = data.result
          addStep(
            `Match Score: ${r.match_score}%`,
            r.match_score >= 70 ? 'done' : 'failed',
            `Missing: ${r.missing_keywords?.slice(0, 5).join(', ')}`
          )
        }
      }

    } catch (err: any) {
      addStep('Error', 'failed', err?.response?.data?.detail || String(err))
      toast.error('Agent failed. Check API key configuration.')
    } finally {
      setLoading(false)
    }
  }

  const acceptDiff = (diff: DiffCard) => {
    if (diff.type === 'summary') setField('professional_summary', diff.proposed)
    setDiffs(d => d.map(x => x.id === diff.id ? { ...x, accepted: true } : x))
    toast.success('Applied!')
  }
  const rejectDiff = (id: string) => setDiffs(d => d.map(x => x.id === id ? { ...x, accepted: false } : x))

  const AGENTS = [
    { key: 'bullet',  icon: Wand2,       label: 'Rewrite Bullet',  desc: 'XYZ formula rewriter' },
    { key: 'ats',     icon: FileSearch,   label: 'ATS Audit',       desc: 'Score & fix warnings' },
    { key: 'jd',      icon: Target,       label: 'JD Gap Analysis', desc: 'Keyword match matrix' },
    { key: 'summary', icon: Sparkles,     label: 'Gen Summary',     desc: 'Executive 3-sentence' },
  ]

  return (
    <div className="flex flex-col h-full bg-[#09090B] animate-slide-in-right">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#27272A]">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-white" />
          <span className="font-semibold text-sm text-white">AI Agent Studio</span>
          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-[#27272A]">β</span>
        </div>
        <button onClick={onClose} className="btn-ghost w-8 h-8 p-0 justify-center"><X className="w-4 h-4" /></button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Agent selector */}
        <div className="grid grid-cols-2 gap-2">
          {AGENTS.map(({ key, icon: Icon, label, desc }) => (
            <button
              key={key}
              onClick={() => run(key)}
              disabled={loading}
              className={clsx(
                'card p-3 text-left hover:border-zinc-600 transition-all disabled:opacity-40 disabled:cursor-not-allowed',
                activeAgent === key && 'border-zinc-500 bg-white/3'
              )}
            >
              <Icon className="w-4 h-4 text-white mb-2" />
              <div className="text-xs font-medium text-white">{label}</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">{desc}</div>
            </button>
          ))}
        </div>

        {/* Bullet input (only for bullet rewriter) */}
        {(activeAgent === 'bullet' || !activeAgent) && (
          <div>
            <label className="label">Bullet to Rewrite</label>
            <textarea className="textarea text-xs" rows={3}
              placeholder="Worked on backend microservices to improve performance…"
              value={bulletInput}
              onChange={e => setBulletInput(e.target.value)} />
          </div>
        )}

        {/* Agent steps log */}
        {steps.length > 0 && (
          <div className="space-y-1">
            <p className="section-heading">Agent Reasoning</p>
            {steps.map((s, i) => (
              <div key={i} className={clsx('agent-step',
                s.status === 'done'    && 'agent-step-done',
                s.status === 'running' && 'agent-step-running',
                s.status === 'failed'  && 'agent-step-failed',
                s.status === 'pending' && 'agent-step-pending',
              )}>
                {s.status === 'done'    && <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />}
                {s.status === 'running' && <Loader2 className="w-3.5 h-3.5 shrink-0 animate-spin" />}
                {s.status === 'failed'  && <XCircle className="w-3.5 h-3.5 shrink-0" />}
                {s.status === 'pending' && <ChevronRight className="w-3.5 h-3.5 shrink-0" />}
                <div>
                  <div className="font-medium text-xs">{s.step}</div>
                  {s.message && <div className="text-[10px] opacity-70 mt-0.5">{s.message}</div>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ATS Result */}
        {atsResult && (
          <div className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-white">ATS Score</span>
              <span className={clsx('text-2xl font-bold font-mono',
                atsResult.score >= 80 ? 'text-emerald-400' :
                atsResult.score >= 60 ? 'text-amber-400' : 'text-red-400')}>
                {atsResult.score}/100
              </span>
            </div>
            {atsResult.warnings?.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-semibold text-zinc-400">Warnings</p>
                {atsResult.warnings.map((w: string, i: number) => (
                  <div key={i} className="text-xs text-amber-300 flex gap-1.5">
                    <span>⚠</span><span>{w}</span>
                  </div>
                ))}
              </div>
            )}
            {atsResult.missing_keywords?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-zinc-400 mb-1">Missing Keywords</p>
                <div className="flex flex-wrap gap-1">
                  {atsResult.missing_keywords.map((kw: string) => (
                    <span key={kw} className="badge badge-score-low">{kw}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Diff cards */}
        {diffs.map((diff) => diff.accepted === null && (
          <div key={diff.id} className="card overflow-hidden">
            <div className="px-4 py-2 border-b border-[#27272A] flex items-center justify-between">
              <span className="text-xs font-semibold text-white capitalize">{diff.type} suggestion</span>
              <span className="font-mono text-[10px] text-zinc-500">{Math.round(diff.confidence * 100)}% confidence</span>
            </div>
            {diff.original && (
              <div className="px-4 py-2 border-b border-[#27272A] bg-red-500/5">
                <p className="text-[10px] text-red-400 font-mono mb-1">ORIGINAL</p>
                <p className="text-xs text-zinc-400 leading-relaxed">{diff.original}</p>
              </div>
            )}
            <div className="px-4 py-2 bg-emerald-500/5">
              <p className="text-[10px] text-emerald-400 font-mono mb-1">PROPOSED</p>
              <p className="text-xs text-white leading-relaxed">{diff.proposed}</p>
            </div>
            <div className="px-4 py-3 flex gap-2 border-t border-[#27272A]">
              <button onClick={() => acceptDiff(diff)} className="btn-primary text-xs py-1.5 px-3">
                <CheckCircle2 className="w-3.5 h-3.5" /> Accept
              </button>
              <button onClick={() => rejectDiff(diff.id)} className="btn-ghost text-xs py-1.5 px-3 hover:text-red-400">
                <XCircle className="w-3.5 h-3.5" /> Reject
              </button>
            </div>
          </div>
        ))}

        {/* Pipeline log */}
        {pipelineLog.length > 0 && (
          <div>
            <p className="section-heading">Pipeline Log</p>
            <div className="card p-3 max-h-40 overflow-y-auto">
              {pipelineLog.map((line, i) => (
                <p key={i} className="font-mono text-[10px] text-zinc-500 leading-5">{line}</p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
