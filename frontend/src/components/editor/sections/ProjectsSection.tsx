import { useResumeStore, ProjectEntry } from '@/store/useResumeStore'
import { Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

function ProjCard({ entry, index, onChange, onRemove }: {
  entry: ProjectEntry; index: number
  onChange: (idx: number, field: keyof ProjectEntry, val: any) => void
  onRemove: (idx: number) => void
}) {
  const [open, setOpen] = useState(index === 0)
  return (
    <div className="card overflow-hidden">
      <button className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/3 transition-colors"
        onClick={() => setOpen(!open)}>
        <div>
          <span className="text-sm font-medium text-white">{entry.name || `Project ${index + 1}`}</span>
          {entry.tech_stack && <span className="text-xs text-zinc-500 ml-2">· {entry.tech_stack.split(',')[0]}</span>}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={e => { e.stopPropagation(); onRemove(index) }}
            className="text-zinc-600 hover:text-red-400 transition-colors p-1">
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          {open ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
        </div>
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-[#27272A]">
          <div className="grid grid-cols-2 gap-3 mt-3">
            <div>
              <label className="label">Project Name *</label>
              <input className="input" placeholder="ResumeBuilder AI"
                value={entry.name} onChange={e => onChange(index, 'name', e.target.value)} />
            </div>
            <div>
              <label className="label">Tech Stack</label>
              <input className="input" placeholder="Python, FastAPI, React"
                value={entry.tech_stack} onChange={e => onChange(index, 'tech_stack', e.target.value)} />
            </div>
            <div>
              <label className="label">Duration</label>
              <input className="input" placeholder="Jan 2024 – Present"
                value={entry.duration} onChange={e => onChange(index, 'duration', e.target.value)} />
            </div>
            <div>
              <label className="label">Link (GitHub / Live)</label>
              <input className="input" placeholder="https://github.com/…"
                value={entry.link} onChange={e => onChange(index, 'link', e.target.value)} />
            </div>
          </div>
          <div>
            <label className="label">Description Bullets (one per line)</label>
            <textarea className="textarea" rows={4}
              placeholder="• Built end-to-end resume pipeline using multi-agent AI&#10;• Achieved 95% ATS pass rate…"
              value={entry.bullets.join('\n')}
              onChange={e => onChange(index, 'bullets',
                e.target.value.split('\n').map(b => b.replace(/^[•●\-–]\s*/, '').trim()).filter(Boolean))} />
          </div>
        </div>
      )}
    </div>
  )
}

export default function ProjectsSection() {
  const { resume, setField } = useResumeStore()
  const entries = resume.projects

  const update = (idx: number, field: keyof ProjectEntry, val: any) =>
    setField('projects', entries.map((e, i) => i === idx ? { ...e, [field]: val } : e))
  const add = () => setField('projects', [...entries, { name: '', tech_stack: '', duration: '', bullets: [], link: '' }])
  const remove = (idx: number) => setField('projects', entries.filter((_, i) => i !== idx))

  return (
    <div className="space-y-3 animate-slide-up">
      <div className="flex items-center justify-between">
        <p className="section-heading mb-0">Projects</p>
        <button onClick={add} className="btn-ghost text-xs py-1 px-2"><Plus className="w-3.5 h-3.5" /> Add</button>
      </div>
      {entries.length === 0 && (
        <div className="card p-8 text-center text-zinc-600 text-sm">
          No projects added. Click <strong className="text-zinc-400">+ Add</strong> to begin.
        </div>
      )}
      {entries.map((e, i) => <ProjCard key={i} entry={e} index={i} onChange={update} onRemove={remove} />)}
      {entries.length > 0 && (
        <button onClick={add} className="btn-secondary w-full justify-center text-xs py-2">
          <Plus className="w-3.5 h-3.5" /> Add Another Project
        </button>
      )}
    </div>
  )
}
