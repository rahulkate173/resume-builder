import { useResumeStore } from '@/store/useResumeStore'
import { X } from 'lucide-react'
import { useState, KeyboardEvent } from 'react'

function TagInput({ label, tags, onAdd, onRemove, placeholder }: {
  label: string; tags: string[]; placeholder: string
  onAdd: (t: string) => void; onRemove: (t: string) => void
}) {
  const [input, setInput] = useState('')
  const commit = () => {
    const val = input.trim()
    if (val && !tags.includes(val)) { onAdd(val); setInput('') }
  }
  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); commit() }
  }
  return (
    <div>
      <label className="label">{label}</label>
      <div className="flex flex-wrap gap-1.5 p-2 rounded-lg border border-[#27272A] bg-[#09090B] min-h-[42px] focus-within:border-zinc-500 transition-colors">
        {tags.map(t => (
          <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-800 border border-[#27272A] text-xs text-white font-medium">
            {t}
            <button onClick={() => onRemove(t)} className="text-zinc-500 hover:text-white"><X className="w-3 h-3" /></button>
          </span>
        ))}
        <input
          className="flex-1 min-w-24 bg-transparent text-sm text-white placeholder-zinc-600 outline-none"
          placeholder={placeholder}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKey}
          onBlur={commit}
        />
      </div>
      <p className="text-xs text-zinc-600 mt-1">Press Enter or comma to add</p>
    </div>
  )
}

export default function SkillsSection() {
  const { resume, setField } = useResumeStore()

  const addSkill    = (t: string) => setField('skills',    [...resume.skills,    t])
  const removeSkill = (t: string) => setField('skills',    resume.skills.filter(s => s !== t))
  const addLang     = (t: string) => setField('languages', [...resume.languages, t])
  const removeLang  = (t: string) => setField('languages', resume.languages.filter(l => l !== t))

  return (
    <div className="space-y-5 animate-slide-up">
      <p className="section-heading">Skills &amp; Technologies</p>

      <TagInput
        label="Technical Skills"
        tags={resume.skills}
        onAdd={addSkill}
        onRemove={removeSkill}
        placeholder="Python, Docker, React…"
      />

      <TagInput
        label="Programming Languages"
        tags={resume.languages}
        onAdd={addLang}
        onRemove={removeLang}
        placeholder="Python, TypeScript, Go…"
      />

      <div className="divider pt-1" />
      <p className="section-heading">Certifications</p>
      {resume.certifications.map((c, i) => (
        <div key={i} className="card p-3 grid grid-cols-2 gap-2">
          <input className="input text-xs" placeholder="Cert name" value={c.name}
            onChange={e => {
              const certs = [...resume.certifications]
              certs[i] = { ...certs[i], name: e.target.value }
              setField('certifications', certs)
            }} />
          <input className="input text-xs" placeholder="Issuer" value={c.issuer}
            onChange={e => {
              const certs = [...resume.certifications]
              certs[i] = { ...certs[i], issuer: e.target.value }
              setField('certifications', certs)
            }} />
        </div>
      ))}
      <button onClick={() => setField('certifications', [...resume.certifications, { name: '', issuer: '', date: '', link: '' }])}
        className="btn-ghost text-xs w-full justify-center">+ Add Certification</button>

      <div className="divider pt-1" />
      <p className="section-heading">Achievements &amp; Awards</p>
      {resume.achievements.map((a, i) => (
        <div key={i} className="card p-3 space-y-2">
          <input className="input text-xs" placeholder="Title (e.g. Hackathon 1st Place)" value={a.title}
            onChange={e => {
              const ach = [...resume.achievements]
              ach[i] = { ...ach[i], title: e.target.value }
              setField('achievements', ach)
            }} />
          <textarea className="textarea text-xs" rows={2} placeholder="Brief description…" value={a.description}
            onChange={e => {
              const ach = [...resume.achievements]
              ach[i] = { ...ach[i], description: e.target.value }
              setField('achievements', ach)
            }} />
        </div>
      ))}
      <button onClick={() => setField('achievements', [...resume.achievements, { title: '', description: '' }])}
        className="btn-ghost text-xs w-full justify-center">+ Add Achievement</button>
    </div>
  )
}
