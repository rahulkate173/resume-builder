import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Save, Download, Loader2, Bot, Layers, ChevronLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { resumeApi, profileApi } from '@/api/client'
import { useResumeStore } from '@/store/useResumeStore'
import FormEditor from '@/components/editor/FormEditor'
import AIAgentPanel from '@/components/editor/AIAgentPanel'
import ResumePreview from '@/components/preview/ResumePreview'
import TemplateSwitcher from '@/components/editor/TemplateSwitcher'

export default function Editor() {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const {
    resume, setResume, isDirty, markClean,
    showAgentPanel, toggleAgentPanel,
    activeTemplate, setActiveTemplate,
  } = useResumeStore()

  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [pipelineLog, setPipelineLog] = useState<string[]>([])
  const [zoom, setZoom] = useState(85)

  // Load existing resume + profile on mount
  useEffect(() => {
    const init = async () => {
      setLoading(true)
      try {
        // Load profile into store
        const { data: profile } = await profileApi.get()
        setResume({
          full_name: profile.full_name || '',
          email: profile.email || '',
          phone: profile.phone || '',
          location: profile.location || '',
          linkedin: profile.linkedin || '',
          github: profile.github || '',
          leetcode: profile.leetcode || '',
          codeforces: profile.codeforces || '',
          portfolio: profile.portfolio || '',
          kaggle: profile.kaggle || '',
          twitter: profile.twitter || '',
          professional_summary: profile.professional_summary || '',
          experience: profile.experience || [],
          education: profile.education || [],
          projects: profile.projects || [],
          certifications: profile.certifications || [],
          achievements: profile.achievements || [],
          skills: profile.skills || [],
          languages: profile.languages || [],
        })

        if (id && id !== 'new') {
          const { data: resumeDoc } = await resumeApi.get(id)
          setResume({
            id: resumeDoc._id || id,
            title: resumeDoc.title || '',
            job_role: resumeDoc.job_role || '',
            company: resumeDoc.company || '',
            job_description: resumeDoc.job_description || '',
            template_key: resumeDoc.template_key || 'executive',
            latex_output: resumeDoc.latex_output || '',
            verified: resumeDoc.verified || false,
            verification_score: resumeDoc.verification_score || 0,
            ats_score: resumeDoc.ats_score || 0,
            jd_match_score: resumeDoc.jd_match_score || 0,
            has_pdf: resumeDoc.has_pdf || false,
          })
          setActiveTemplate(resumeDoc.template_key || 'executive')
        }
        markClean()
      } catch {
        // Guest mode — profile might not exist
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [id])

  const handleSave = async () => {
    setSaving(true)
    try {
      // Save profile
      await profileApi.update({
        full_name: resume.full_name, email: resume.email, phone: resume.phone,
        location: resume.location, linkedin: resume.linkedin, github: resume.github,
        leetcode: resume.leetcode, codeforces: resume.codeforces, portfolio: resume.portfolio,
        kaggle: resume.kaggle, twitter: resume.twitter,
        professional_summary: resume.professional_summary,
        experience: resume.experience, education: resume.education,
        projects: resume.projects, certifications: resume.certifications,
        achievements: resume.achievements, skills: resume.skills, languages: resume.languages,
      })
      markClean()
      toast.success('Profile saved')
    } catch {
      toast.error('Failed to save')
    } finally {
      setSaving(false)
    }
  }

  const handleGenerate = async () => {
    if (!resume.job_role || !resume.company || !resume.job_description) {
      toast.error('Fill in Job Role, Company and Job Description first.')
      return
    }
    setGenerating(true)
    setPipelineLog([])
    try {
      const log = (msg: string) => setPipelineLog((prev) => [...prev, `${new Date().toLocaleTimeString()} — ${msg}`])
      log('🚀 Starting multi-agent pipeline…')
      log('🎨 Selecting template…')

      const { data } = await resumeApi.create({
        job_role: resume.job_role,
        company: resume.company,
        job_description: resume.job_description,
        template_key: resume.template_key,
      })

      log('✍️ Agent 1 generating resume…')
      log('🔍 Agent 2 verifying output…')
      log('✨ LLM 3 polishing and compiling PDF…')

      setResume({
        id: data._id || data.id,
        latex_output: data.latex_output || '',
        verified: data.verified,
        verification_score: data.verification_score,
        ats_score: data.ats_score,
        jd_match_score: data.jd_match_score,
        has_pdf: data.has_pdf || !!data.pdf_base64,
      })
      markClean()
      log('✅ Done! Resume ready.')
      toast.success(`Resume generated! ATS Score: ${data.ats_score ?? data.verification_score ?? '—'}/100`)

      if (data._id && id === 'new') {
        navigate(`/editor/${data._id}`, { replace: true })
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Pipeline failed. Check API keys.')
    } finally {
      setGenerating(false)
    }
  }

  const handleExportPdf = async () => {
    if (!resume.id) { toast.error('Generate a resume first.'); return }
    try {
      const resp = await resumeApi.exportPdf(resume.id)
      const url = window.URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.download = `resume_${resume.job_role.replace(/\s/g, '_')}.pdf`
      link.click()
      window.URL.revokeObjectURL(url)
      toast.success('PDF downloaded!')
    } catch {
      toast.error('PDF export failed.')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090B] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          <p className="text-zinc-500 text-sm">Loading editor…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-56px)] bg-[#09090B] flex flex-col">
      {/* Editor toolbar */}
      <div className="border-b border-[#27272A] bg-[#09090B] px-4 py-2 flex items-center gap-2">
        <button onClick={() => navigate('/dashboard')} className="btn-ghost text-xs">
          <ChevronLeft className="w-3.5 h-3.5" /> Dashboard
        </button>
        <div className="flex-1" />

        {isDirty && <span className="text-xs text-amber-400 font-mono">● unsaved</span>}

        <button onClick={toggleAgentPanel} className={`btn-ghost text-xs ${showAgentPanel ? 'text-white bg-white/5' : ''}`}>
          <Bot className="w-3.5 h-3.5" /> AI Studio
        </button>
        <button onClick={handleSave} disabled={saving} className="btn-ghost text-xs">
          {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
          {saving ? 'Saving…' : 'Save Profile'}
        </button>
        <button
          id="generate-btn"
          onClick={handleGenerate}
          disabled={generating}
          className="btn-primary text-xs py-2 px-3"
        >
          {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
          {generating ? 'Generating…' : 'Generate Resume'}
        </button>
        <button onClick={handleExportPdf} disabled={!resume.id} className="btn-secondary text-xs py-2 px-3">
          <Download className="w-3.5 h-3.5" /> PDF
        </button>
      </div>

      {/* Main split layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT: Form Editor (45%) */}
        <div className="w-[45%] min-w-0 border-r border-[#27272A] overflow-y-auto flex flex-col">
          {showAgentPanel
            ? <AIAgentPanel onClose={toggleAgentPanel} pipelineLog={pipelineLog} />
            : <FormEditor />
          }
        </div>

        {/* RIGHT: Live Preview (55%) */}
        <div className="flex-1 overflow-auto bg-zinc-950 flex flex-col">
          {/* Preview toolbar */}
          <div className="sticky top-0 z-10 border-b border-[#27272A] bg-zinc-950/80 glass px-4 py-2 flex items-center gap-3">
            <TemplateSwitcher />
            <div className="flex-1" />
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500 font-mono">Zoom</span>
              {[75, 85, 100].map((z) => (
                <button
                  key={z}
                  onClick={() => setZoom(z)}
                  className={`text-xs font-mono px-2 py-1 rounded transition-colors ${zoom === z ? 'bg-white text-[#09090B]' : 'text-zinc-500 hover:text-white'}`}
                >
                  {z}%
                </button>
              ))}
            </div>
          </div>

          {/* A4 resume preview */}
          <div className="flex-1 p-8 flex items-start justify-center">
            <div style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
                 className="w-[210mm] transition-transform duration-200">
              <ResumePreview />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
