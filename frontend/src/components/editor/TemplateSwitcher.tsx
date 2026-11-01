import { useResumeStore } from '@/store/useResumeStore'
import clsx from 'clsx'

const TEMPLATES = [
  { key: 'executive', label: 'Executive', tag: 'ATS' },
  { key: 'modern',    label: 'Modern',    tag: 'Tech' },
  { key: 'classic',   label: 'Classic',   tag: 'Academic' },
  { key: 'compact',   label: 'Compact',   tag: 'Senior' },
]

export default function TemplateSwitcher() {
  const { activeTemplate, setActiveTemplate } = useResumeStore()

  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-zinc-500 mr-1 font-mono">Template:</span>
      {TEMPLATES.map(({ key, label, tag }) => (
        <button
          key={key}
          id={`template-${key}`}
          onClick={() => setActiveTemplate(key)}
          className={clsx(
            'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all',
            activeTemplate === key
              ? 'bg-white text-[#09090B] font-semibold'
              : 'text-zinc-500 hover:text-white hover:bg-white/5 border border-transparent hover:border-[#27272A]'
          )}
        >
          {label}
          <span className={clsx(
            'text-[9px] font-mono px-1 py-0.5 rounded',
            activeTemplate === key ? 'bg-black/10 text-[#09090B]' : 'text-zinc-600'
          )}>
            {tag}
          </span>
        </button>
      ))}
    </div>
  )
}
