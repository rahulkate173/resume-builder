import { useResumeStore } from '@/store/useResumeStore'

export default function ModernTechMinimal() {
  const { resume } = useResumeStore()
  return (
    <div className="h-full p-[0.45in] text-[9.5pt] bg-white text-black overflow-hidden"
      style={{ fontFamily: 'Helvetica Neue, Arial, sans-serif' }}>

      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h1 className="text-[22pt] font-black tracking-tight text-black leading-none">
            {resume.full_name || 'Your Name'}
          </h1>
          {resume.professional_summary && (
            <p className="text-[8pt] text-gray-500 mt-1 max-w-xs leading-relaxed">
              {resume.professional_summary.substring(0, 120)}…
            </p>
          )}
        </div>
        <div className="text-right text-[8pt] text-gray-500 space-y-0.5 font-mono">
          {resume.email && <div>{resume.email}</div>}
          {resume.phone && <div>{resume.phone}</div>}
          {resume.github && <div>github</div>}
          {resume.linkedin && <div>linkedin</div>}
        </div>
      </div>

      <hr className="border-gray-900 mb-2" />

      {/* Experience */}
      {resume.experience.length > 0 && (
        <section className="mb-2.5">
          <h2 className="text-[8pt] font-black uppercase tracking-[0.15em] text-gray-500 mb-1.5">Experience</h2>
          {resume.experience.slice(0, 3).map((e, i) => (
            <div key={i} className="mb-2">
              <div className="flex justify-between items-baseline">
                <span className="font-bold text-[9.5pt]">{e.company}</span>
                <span className="font-mono text-[7.5pt] text-gray-400">{e.duration}</span>
              </div>
              <div className="italic text-[8.5pt] text-gray-600 mb-0.5">{e.role}</div>
              <ul className="space-y-0.5 pl-0">
                {e.bullets.slice(0, 3).map((b, j) => (
                  <li key={j} className="text-[8pt] text-gray-800 flex gap-1.5">
                    <span className="text-gray-400 shrink-0">›</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Projects */}
      {resume.projects.length > 0 && (
        <section className="mb-2.5">
          <h2 className="text-[8pt] font-black uppercase tracking-[0.15em] text-gray-500 mb-1.5">Projects</h2>
          {resume.projects.slice(0, 2).map((p, i) => (
            <div key={i} className="mb-1.5">
              <div className="flex items-baseline gap-2">
                <span className="font-bold text-[9pt]">{p.name}</span>
                {p.tech_stack && (
                  <span className="font-mono text-[7pt] bg-gray-100 px-1.5 py-0.5 rounded">{p.tech_stack}</span>
                )}
              </div>
              <ul className="space-y-0.5 pl-0 mt-0.5">
                {p.bullets.slice(0, 2).map((b, j) => (
                  <li key={j} className="text-[8pt] text-gray-800 flex gap-1.5">
                    <span className="text-gray-400 shrink-0">›</span><span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Education & Skills side by side */}
      <div className="grid grid-cols-2 gap-4">
        {resume.education.length > 0 && (
          <section>
            <h2 className="text-[8pt] font-black uppercase tracking-[0.15em] text-gray-500 mb-1.5">Education</h2>
            {resume.education.map((e, i) => (
              <div key={i} className="mb-1">
                <div className="font-bold text-[9pt]">{e.institution}</div>
                <div className="text-[8pt] text-gray-600">{[e.degree, e.field].filter(Boolean).join(', ')}</div>
                <div className="font-mono text-[7.5pt] text-gray-400">{e.duration}</div>
              </div>
            ))}
          </section>
        )}
        {(resume.skills.length > 0 || resume.languages.length > 0) && (
          <section>
            <h2 className="text-[8pt] font-black uppercase tracking-[0.15em] text-gray-500 mb-1.5">Skills</h2>
            {resume.languages.length > 0 && <div className="text-[8pt] mb-0.5"><strong>Languages: </strong>{resume.languages.join(', ')}</div>}
            {resume.skills.length > 0 && <div className="text-[8pt]">{resume.skills.join(' · ')}</div>}
          </section>
        )}
      </div>
    </div>
  )
}
