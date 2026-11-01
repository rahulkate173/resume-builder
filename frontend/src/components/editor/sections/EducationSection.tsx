import { useResumeStore, EducationEntry } from '@/store/useResumeStore'
import { Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

function EduCard({ entry, index, onChange, onRemove }: {
  entry: EducationEntry; index: number
  onChange: (idx: number, field: keyof EducationEntry, val: any) => void
  onRemove: (idx: number) => void
}) {
  const [open, setOpen] = useState(index === 0)
  return (
    <div className="card overflow-hidden">
      <button className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/3 transition-colors"
        onClick={() => setOpen(!open)}>
        <div>
          <span className="text-sm font-medium text-white">
            {entry.institution || `Education ${index + 1}`}
          </span>
          {entry.degree && <span className="text-xs text-zinc-500 ml-2">· {entry.degree}</span>}
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
            <div className="col-span-2">
              <label className="label">Institution *</label>
              <input className="input" placeholder="MIT"
                value={entry.institution} onChange={e => onChange(index, 'institution', e.target.value)} />
            </div>
            <div>
              <label className="label">Degree</label>
              <input className="input" placeholder="B.S. / M.S. / Ph.D."
                value={entry.degree} onChange={e => onChange(index, 'degree', e.target.value)} />
            </div>
            <div>
              <label className="label">Field of Study</label>
              <input className="input" placeholder="Computer Science"
                value={entry.field} onChange={e => onChange(index, 'field', e.target.value)} />
            </div>
            <div>
              <label className="label">Duration</label>
              <input className="input" placeholder="Aug 2018 – May 2022"
                value={entry.duration} onChange={e => onChange(index, 'duration', e.target.value)} />
            </div>
            <div>
              <label className="label">GPA (optional)</label>
              <input className="input" placeholder="3.9/4.0"
                value={entry.gpa} onChange={e => onChange(index, 'gpa', e.target.value)} />
            </div>
          </div>
          <div>
            <label className="label">Notable Courses / Achievements (one per line)</label>
            <textarea className="textarea" rows={3}
              placeholder="Distributed Systems · Machine Learning · Dean's List"
              value={entry.bullets.join('\n')}
              onChange={e => onChange(index, 'bullets',
                e.target.value.split('\n').map(b => b.trim()).filter(Boolean))} />
          </div>
        </div>
      )}
    </div>
  )
}

export default function EducationSection() {
  const { resume, setField } = useResumeStore()
  const entries = resume.education

  const update = (idx: number, field: keyof EducationEntry, val: any) =>
    setField('education', entries.map((e, i) => i === idx ? { ...e, [field]: val } : e))
  const add = () => setField('education', [...entries, { institution: '', degree: '', field: '', duration: '', gpa: '', bullets: [] }])
  const remove = (idx: number) => setField('education', entries.filter((_, i) => i !== idx))

  return (
    <div className="space-y-3 animate-slide-up">
      <div className="flex items-center justify-between">
        <p className="section-heading mb-0">Education</p>
        <button onClick={add} className="btn-ghost text-xs py-1 px-2"><Plus className="w-3.5 h-3.5" /> Add</button>
      </div>
      {entries.length === 0 && (
        <div className="card p-8 text-center text-zinc-600 text-sm">
          No education added yet. Click <strong className="text-zinc-400">+ Add</strong> to begin.
        </div>
      )}
      {entries.map((e, i) => <EduCard key={i} entry={e} index={i} onChange={update} onRemove={remove} />)}
      {entries.length > 0 && (
        <button onClick={add} className="btn-secondary w-full justify-center text-xs py-2">
          <Plus className="w-3.5 h-3.5" /> Add Another Education
        </button>
      )}
    </div>
  )
}
