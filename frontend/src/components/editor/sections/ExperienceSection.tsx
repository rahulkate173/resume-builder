import { useResumeStore, ExperienceEntry } from '@/store/useResumeStore'
import { Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

function ExpCard({ entry, index, onChange, onRemove }: {
  entry: ExperienceEntry; index: number
  onChange: (idx: number, field: keyof ExperienceEntry, val: any) => void
  onRemove: (idx: number) => void
}) {
  const [open, setOpen] = useState(index === 0)
  return (
    <div className="card overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/3 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <div>
          <span className="text-sm font-medium text-white">
            {entry.company || `Experience ${index + 1}`}
          </span>
          {entry.role && <span className="text-xs text-zinc-500 ml-2">· {entry.role}</span>}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={(e) => { e.stopPropagation(); onRemove(index) }}
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
              <label className="label">Company *</label>
              <input className="input" placeholder="Google"
                value={entry.company} onChange={e => onChange(index, 'company', e.target.value)} />
            </div>
            <div>
              <label className="label">Role / Title *</label>
              <input className="input" placeholder="Software Engineer"
                value={entry.role} onChange={e => onChange(index, 'role', e.target.value)} />
            </div>
            <div>
              <label className="label">Duration</label>
              <input className="input" placeholder="Jan 2022 – Dec 2023"
                value={entry.duration} onChange={e => onChange(index, 'duration', e.target.value)} />
            </div>
            <div>
              <label className="label">Location</label>
              <input className="input" placeholder="Mountain View, CA"
                value={entry.location} onChange={e => onChange(index, 'location', e.target.value)} />
            </div>
          </div>
          <div>
            <label className="label">Bullet Points (one per line)</label>
            <textarea className="textarea" rows={4}
              placeholder="• Built scalable REST APIs serving 10M+ requests/day&#10;• Reduced latency by 40% through caching…"
              value={entry.bullets.join('\n')}
              onChange={e => onChange(index, 'bullets',
                e.target.value.split('\n').map(b => b.replace(/^[•●\-–]\s*/, '').trim()).filter(Boolean)
              )} />
          </div>
        </div>
      )}
    </div>
  )
}

export default function ExperienceSection() {
  const { resume, setField } = useResumeStore()
  const entries = resume.experience

  const update = (idx: number, field: keyof ExperienceEntry, val: any) => {
    const updated = entries.map((e, i) => i === idx ? { ...e, [field]: val } : e)
    setField('experience', updated)
  }

  const add = () => setField('experience', [
    ...entries,
    { company: '', role: '', duration: '', location: '', bullets: [] }
  ])

  const remove = (idx: number) => setField('experience', entries.filter((_, i) => i !== idx))

  return (
    <div className="space-y-3 animate-slide-up">
      <div className="flex items-center justify-between">
        <p className="section-heading mb-0">Work Experience</p>
        <button onClick={add} className="btn-ghost text-xs py-1 px-2">
          <Plus className="w-3.5 h-3.5" /> Add
        </button>
      </div>
      {entries.length === 0 && (
        <div className="card p-8 text-center text-zinc-600 text-sm">
          No experience added yet. Click <strong className="text-zinc-400">+ Add</strong> to begin.
        </div>
      )}
      {entries.map((e, i) => (
        <ExpCard key={i} entry={e} index={i} onChange={update} onRemove={remove} />
      ))}
      {entries.length > 0 && (
        <button onClick={add} className="btn-secondary w-full justify-center text-xs py-2">
          <Plus className="w-3.5 h-3.5" /> Add Another Experience
        </button>
      )}
    </div>
  )
}
