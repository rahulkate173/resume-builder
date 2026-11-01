import { useResumeStore } from '@/store/useResumeStore'

export default function CompactTwoColumn() {
  const { resume } = useResumeStore()
  return (
    <div className="h-full bg-white text-black overflow-hidden flex flex-col"
      style={{ fontFamily: 'Arial, Helvetica, sans-serif', fontSize: '8.5pt' }}>

      {/* Compact header */}
      <div className="bg-gray-900 text-white px-5 py-3">
        <h1 className="text-[15pt] font-black tracking-tight">{resume.full_name || 'Your Name'}</h1>
        <div className="flex flex-wrap gap-x-3 text-[7.5pt] text-gray-300 mt-0.5">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.linkedin && <span>linkedin</span>}
          {resume.github && <span>github</span>}
        </div>
      </div>

      {/* Two column body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Experience + Projects */}
        <div className="flex-1 p-4 border-r border-gray-200 overflow-hidden">
          {resume.experience.length > 0 && (
            <section className="mb-3">
              <h2 className="text-[7.5pt] font-black uppercase tracking-widest text-gray-500 border-b border-gray-300 pb-0.5 mb-1.5">Experience</h2>
              {resume.experience.slice(0, 3).map((e, i) => (
                <div key={i} className="mb-2">
                  <div className="flex justify-between items-baseline">
                    <span className="font-bold text-[8.5pt]">{e.company}</span>
                    <span className="text-[7pt] text-gray-400">{e.duration}</span>
                  </div>
                  <div className="italic text-[8pt] text-gray-600 mb-0.5">{e.role}</div>
                  {e.bullets.slice(0, 3).map((b, j) => (
                    <div key={j} className="flex gap-1 text-[7.5pt] text-gray-800">
                      <span className="text-gray-400 shrink-0">·</span><span>{b}</span>
                    </div>
                  ))}
                </div>
              ))}
            </section>
          )}

          {resume.projects.length > 0 && (
            <section>
              <h2 className="text-[7.5pt] font-black uppercase tracking-widest text-gray-500 border-b border-gray-300 pb-0.5 mb-1.5">Projects</h2>
              {resume.projects.slice(0, 2).map((p, i) => (
                <div key={i} className="mb-1.5">
                  <div className="font-bold text-[8.5pt]">{p.name}</div>
                  {p.tech_stack && <div className="text-[7.5pt] text-gray-500 italic">{p.tech_stack}</div>}
                  {p.bullets.slice(0, 2).map((b, j) => (
                    <div key={j} className="flex gap-1 text-[7.5pt] text-gray-800">
                      <span className="text-gray-400 shrink-0">·</span><span>{b}</span>
                    </div>
                  ))}
                </div>
              ))}
            </section>
          )}
        </div>

        {/* Right: Skills + Education + Certs */}
        <div className="w-[38%] p-4 bg-gray-50 overflow-hidden">
          {(resume.skills.length > 0 || resume.languages.length > 0) && (
            <section className="mb-3">
              <h2 className="text-[7.5pt] font-black uppercase tracking-widest text-gray-500 border-b border-gray-300 pb-0.5 mb-1.5">Skills</h2>
              {resume.languages.length > 0 && (
                <div className="mb-1">
                  <div className="text-[7.5pt] font-semibold text-gray-500 mb-0.5">Languages</div>
                  {resume.languages.map(l => (
                    <span key={l} className="inline-block text-[7pt] bg-gray-200 rounded px-1 py-0.5 mr-0.5 mb-0.5">{l}</span>
                  ))}
                </div>
              )}
              {resume.skills.length > 0 && (
                <div>
                  <div className="text-[7.5pt] font-semibold text-gray-500 mb-0.5">Technologies</div>
                  <div className="text-[7.5pt] leading-relaxed">{resume.skills.join(' · ')}</div>
                </div>
              )}
            </section>
          )}

          {resume.education.length > 0 && (
            <section className="mb-3">
              <h2 className="text-[7.5pt] font-black uppercase tracking-widest text-gray-500 border-b border-gray-300 pb-0.5 mb-1.5">Education</h2>
              {resume.education.map((e, i) => (
                <div key={i} className="mb-1.5">
                  <div className="font-bold text-[8pt]">{e.institution}</div>
                  <div className="text-[7.5pt] italic">{[e.degree, e.field].filter(Boolean).join(', ')}</div>
                  <div className="text-[7pt] text-gray-400">{e.duration}{e.gpa ? ` · GPA ${e.gpa}` : ''}</div>
                </div>
              ))}
            </section>
          )}

          {resume.certifications.length > 0 && (
            <section>
              <h2 className="text-[7.5pt] font-black uppercase tracking-widest text-gray-500 border-b border-gray-300 pb-0.5 mb-1.5">Certifications</h2>
              {resume.certifications.map((c, i) => (
                <div key={i} className="text-[7.5pt] mb-0.5">
                  <span className="font-semibold">{c.name}</span> {c.issuer && `· ${c.issuer}`}
                </div>
              ))}
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
