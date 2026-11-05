import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, FileText, CheckCircle2, Loader2,
  ChevronLeft, User, Briefcase, GraduationCap, Code2,
  Award, Wrench, ArrowRight, RefreshCw, Save
} from 'lucide-react'
import toast from 'react-hot-toast'
import { profileApi } from '@/api/client'

// ── Types ─────────────────────────────────────────────────────────────────────

interface ParsedProfile {
  full_name: string
  email: string
  phone: string
  location: string
  linkedin: string
  github: string
  portfolio: string
  professional_summary: string
  skills: string[]
  languages: string[]
  education: Array<{ institution: string; degree: string; field: string; duration: string; gpa: string; bullets: string[] }>
  experience: Array<{ company: string; role: string; duration: string; location: string; bullets: string[] }>
  projects: Array<{ name: string; tech_stack: string; duration: string; bullets: string[]; link: string }>
  certifications: Array<{ name: string; issuer: string; date: string; link: string }>
  achievements: Array<{ title: string; description: string }>
}

// ── Section preview helpers ────────────────────────────────────────────────────

function SectionCard({ icon: Icon, title, count, color, children }: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  count?: number
  color: string
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(true)
  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className={`w-full flex items-center gap-3 p-4 text-left hover:bg-white/3 transition-colors`}
      >
        <div className={`w-8 h-8 rounded-lg ${color} flex items-center justify-center flex-shrink-0`}>
          <Icon className="w-4 h-4" />
        </div>
        <span className="font-semibold text-sm text-white flex-1">{title}</span>
        {count !== undefined && (
          <span className="text-xs font-mono bg-white/5 px-2 py-0.5 rounded-full text-zinc-400">{count}</span>
        )}
        <span className={`text-zinc-600 text-xs transition-transform ${open ? 'rotate-90' : ''}`}>▶</span>
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  if (!value) return null
  return (
    <div className="flex gap-3 text-sm">
      <span className="text-zinc-600 w-28 flex-shrink-0">{label}</span>
      <span className="text-zinc-200 break-all">{value}</span>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function UploadResumePage() {
  const navigate  = useNavigate()
  const fileRef   = useRef<HTMLInputElement>(null)
  const dropRef   = useRef<HTMLDivElement>(null)

  const [file,      setFile]      = useState<File | null>(null)
  const [dragging,  setDragging]  = useState(false)
  const [parsing,   setParsing]   = useState(false)
  const [saving,    setSaving]    = useState(false)
  const [parsed,    setParsed]    = useState<ParsedProfile | null>(null)
  const [charCount, setCharCount] = useState(0)

  // ── Drag & Drop ─────────────────────────────────────────────────────────────

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }, [])

  const handleFile = (f: File) => {
    const ok = f.type === 'application/pdf' || f.name.endsWith('.txt')
    if (!ok) { toast.error('Only PDF or .txt files are supported.'); return }
    if (f.size > 5 * 1024 * 1024) { toast.error('File too large (max 5 MB).'); return }
    setFile(f)
    setParsed(null)
  }

  // ── Parse ───────────────────────────────────────────────────────────────────

  const handleParse = async () => {
    if (!file) return
    setParsing(true)
    try {
      const { data } = await profileApi.parseResume(file)
      setParsed(data.parsed)
      setCharCount(data.char_count)
      toast.success('Resume parsed! Review and save below.')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Parsing failed. Try a text-selectable PDF.'
      toast.error(msg)
    } finally {
      setParsing(false)
    }
  }

  // ── Save ────────────────────────────────────────────────────────────────────

  const handleSave = async () => {
    if (!parsed) return
    setSaving(true)
    try {
      await profileApi.update(parsed as unknown as Record<string, unknown>)
      toast.success('Profile updated from your resume!')
      navigate('/editor/new')
    } catch {
      toast.error('Failed to save profile.')
    } finally {
      setSaving(false)
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#09090B] px-4 py-10">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <button onClick={() => navigate('/dashboard')} className="btn-ghost text-xs mb-5">
            <ChevronLeft className="w-3.5 h-3.5" /> Dashboard
          </button>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30
                          bg-emerald-500/5 text-xs font-mono text-emerald-400 mb-4">
            <Upload className="w-3 h-3" />
            Import Existing Resume
          </div>
          <h1 className="text-3xl font-black text-white mb-2 tracking-tight">
            Upload Your&nbsp;
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Resume
            </span>
          </h1>
          <p className="text-zinc-500 text-sm leading-relaxed">
            Upload your existing PDF resume — our AI extracts your profile details automatically.
            Review, then save to your profile with one click.
          </p>
        </div>

        {/* Upload zone */}
        <div
          ref={dropRef}
          onDragEnter={() => setDragging(true)}
          onDragLeave={() => setDragging(false)}
          onDragOver={e => e.preventDefault()}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          className={`card p-10 cursor-pointer text-center transition-all duration-200 mb-4
            ${dragging
              ? 'border-emerald-500/60 bg-emerald-500/5 scale-[1.01]'
              : file
                ? 'border-emerald-500/30 bg-emerald-500/5'
                : 'border-dashed hover:border-white/20 hover:bg-white/3'
            }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt"
            className="hidden"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />

          {file ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30
                              flex items-center justify-center">
                <FileText className="w-7 h-7 text-emerald-400" />
              </div>
              <div>
                <p className="font-semibold text-white">{file.name}</p>
                <p className="text-xs text-zinc-500 mt-0.5">
                  {(file.size / 1024).toFixed(0)} KB · Click to change
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10
                              flex items-center justify-center">
                <Upload className="w-7 h-7 text-zinc-500" />
              </div>
              <div>
                <p className="font-medium text-zinc-300">
                  Drop your resume here, or <span className="text-emerald-400">browse</span>
                </p>
                <p className="text-xs text-zinc-600 mt-1">PDF or .txt · max 5 MB</p>
              </div>
            </div>
          )}
        </div>

        {/* Tips */}
        <div className="flex flex-wrap gap-2 mb-6">
          {['✓ Text-selectable PDF works best', '✓ Scanned images may fail', '✓ Data stays in your profile'].map(t => (
            <span key={t} className="text-[11px] text-zinc-600">{t}</span>
          ))}
        </div>

        {/* Parse button */}
        {file && !parsed && (
          <button
            id="parse-resume-btn"
            onClick={handleParse}
            disabled={parsing}
            className="btn-primary w-full justify-center py-3 text-base mb-8 animate-slide-up"
          >
            {parsing ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
            {parsing ? 'Extracting & Parsing…' : 'Parse Resume with AI'}
            {!parsing && <ArrowRight className="w-4 h-4" />}
          </button>
        )}

        {/* Parsing progress animation */}
        {parsing && (
          <div className="card p-6 mb-8 animate-slide-up">
            <div className="flex items-center gap-3 mb-4">
              <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
              <span className="text-sm font-medium text-white">AI is reading your resume…</span>
            </div>
            <div className="space-y-2">
              {['Extracting text from PDF…', 'Identifying sections…', 'Parsing with Groq AI…', 'Structuring profile data…'].map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-zinc-500">
                  <div className="w-1.5 h-1.5 rounded-full bg-violet-500/50" />
                  {s}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Parsed result preview */}
        {parsed && (
          <div className="space-y-4 animate-slide-up">
            {/* Status bar */}
            <div className="flex items-center gap-3 p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-white">Parsed successfully</p>
                <p className="text-xs text-zinc-500">
                  {charCount.toLocaleString()} chars extracted · Review details below then save
                </p>
              </div>
              <button
                onClick={() => { setParsed(null); setFile(null) }}
                className="btn-ghost text-xs"
              >
                <RefreshCw className="w-3 h-3" /> Try Again
              </button>
            </div>

            {/* Personal Info */}
            <SectionCard icon={User} title="Personal Info" color="bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <div className="space-y-2">
                <InfoRow label="Name"     value={parsed.full_name} />
                <InfoRow label="Email"    value={parsed.email} />
                <InfoRow label="Phone"    value={parsed.phone} />
                <InfoRow label="Location" value={parsed.location} />
                <InfoRow label="LinkedIn" value={parsed.linkedin} />
                <InfoRow label="GitHub"   value={parsed.github} />
                <InfoRow label="Portfolio" value={parsed.portfolio} />
                {parsed.professional_summary && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-xs text-zinc-500 mb-1">Summary</p>
                    <p className="text-xs text-zinc-300 leading-relaxed">{parsed.professional_summary}</p>
                  </div>
                )}
              </div>
            </SectionCard>

            {/* Experience */}
            {parsed.experience?.length > 0 && (
              <SectionCard icon={Briefcase} title="Experience" count={parsed.experience.length}
                color="bg-violet-500/10 text-violet-400 border border-violet-500/20">
                <div className="space-y-4">
                  {parsed.experience.map((e, i) => (
                    <div key={i} className="border-l-2 border-violet-500/20 pl-3">
                      <p className="text-sm font-semibold text-white">{e.role}</p>
                      <p className="text-xs text-zinc-500">{e.company} · {e.duration} {e.location && `· ${e.location}`}</p>
                      {e.bullets?.length > 0 && (
                        <ul className="mt-1.5 space-y-1">
                          {e.bullets.slice(0, 3).map((b, j) => (
                            <li key={j} className="text-xs text-zinc-400 flex gap-1.5">
                              <span className="text-violet-500 flex-shrink-0">•</span>{b}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </SectionCard>
            )}

            {/* Education */}
            {parsed.education?.length > 0 && (
              <SectionCard icon={GraduationCap} title="Education" count={parsed.education.length}
                color="bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <div className="space-y-3">
                  {parsed.education.map((e, i) => (
                    <div key={i} className="border-l-2 border-amber-500/20 pl-3">
                      <p className="text-sm font-semibold text-white">{e.institution}</p>
                      <p className="text-xs text-zinc-500">
                        {[e.degree, e.field].filter(Boolean).join(' in ')} · {e.duration}
                        {e.gpa && ` · GPA: ${e.gpa}`}
                      </p>
                    </div>
                  ))}
                </div>
              </SectionCard>
            )}

            {/* Projects */}
            {parsed.projects?.length > 0 && (
              <SectionCard icon={Code2} title="Projects" count={parsed.projects.length}
                color="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <div className="space-y-3">
                  {parsed.projects.map((p, i) => (
                    <div key={i} className="border-l-2 border-cyan-500/20 pl-3">
                      <p className="text-sm font-semibold text-white">{p.name}</p>
                      {p.tech_stack && <p className="text-xs text-zinc-500">{p.tech_stack}</p>}
                      {p.bullets?.slice(0,2).map((b, j) => (
                        <p key={j} className="text-xs text-zinc-400">• {b}</p>
                      ))}
                    </div>
                  ))}
                </div>
              </SectionCard>
            )}

            {/* Skills */}
            {(parsed.skills?.length > 0 || parsed.languages?.length > 0) && (
              <SectionCard icon={Wrench} title="Skills & Languages"
                color="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <div className="space-y-3">
                  {parsed.skills?.length > 0 && (
                    <div>
                      <p className="text-xs text-zinc-600 mb-1.5">Technical Skills</p>
                      <div className="flex flex-wrap gap-1.5">
                        {parsed.skills.map((s, i) => (
                          <span key={i} className="text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-zinc-300">{s}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {parsed.languages?.length > 0 && (
                    <div>
                      <p className="text-xs text-zinc-600 mb-1.5">Programming Languages</p>
                      <div className="flex flex-wrap gap-1.5">
                        {parsed.languages.map((l, i) => (
                          <span key={i} className="text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-zinc-300">{l}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </SectionCard>
            )}

            {/* Certifications / Achievements */}
            {(parsed.certifications?.length > 0 || parsed.achievements?.length > 0) && (
              <SectionCard icon={Award} title="Certifications & Achievements"
                color="bg-pink-500/10 text-pink-400 border border-pink-500/20">
                <div className="space-y-2">
                  {parsed.certifications?.map((c, i) => (
                    <p key={i} className="text-xs text-zinc-300">🏅 {c.name}{c.issuer ? ` — ${c.issuer}` : ''}</p>
                  ))}
                  {parsed.achievements?.map((a, i) => (
                    <p key={i} className="text-xs text-zinc-300">⭐ {a.title}{a.description ? `: ${a.description}` : ''}</p>
                  ))}
                </div>
              </SectionCard>
            )}

            {/* Save actions */}
            <div className="flex gap-3 pt-2">
              <button
                id="save-parsed-profile-btn"
                onClick={handleSave}
                disabled={saving}
                className="btn-primary flex-1 justify-center py-3 text-sm"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                {saving ? 'Saving to Profile…' : 'Save to My Profile'}
              </button>
              <button
                onClick={() => navigate('/jd-resume')}
                className="btn-secondary text-sm"
              >
                <ArrowRight className="w-4 h-4" />
                Use for JD Resume
              </button>
            </div>

            <p className="text-xs text-zinc-600 text-center">
              You can edit these details later in the Editor.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
