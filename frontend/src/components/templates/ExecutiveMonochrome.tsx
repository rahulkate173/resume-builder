import { useResumeStore } from '@/store/useResumeStore'

// Shared helper
const Dot = () => <span className="mx-1 text-gray-400">·</span>

export default function ExecutiveMonochrome() {
  const { resume } = useResumeStore()

  return (
    <div className="h-full p-[0.5in] text-[10pt] leading-snug font-sans bg-white text-black overflow-hidden"
      style={{ fontFamily: 'Arial, Helvetica, sans-serif' }}>

      {/* Header */}
      <div className="text-center mb-3">
        <h1 className="text-[18pt] font-black tracking-tight uppercase">{resume.full_name || 'Your Name'}</h1>
        <div className="flex items-center justify-center flex-wrap gap-x-2 text-[8.5pt] text-gray-600 mt-1">
          {resume.phone && <span>{resume.phone}</span>}
          {resume.phone && resume.email && <Dot />}
          {resume.email && <span>{resume.email}</span>}
          {resume.email && resume.linkedin && <Dot />}
          {resume.linkedin && <span>LinkedIn</span>}
          {resume.linkedin && resume.github && <Dot />}
          {resume.github && <span>GitHub</span>}
        </div>
      </div>

      <hr className="border-black mb-2" />

      {/* Education */}
      {resume.education.length > 0 && (
        <section className="mb-2">
          <h2 className="text-[9pt] font-black uppercase tracking-widest border-b border-black pb-0.5 mb-1">Education</h2>
          {resume.education.map((e, i) => (
            <div key={i} className="flex justify-between mb-1">
              <div>
                <div className="font-bold text-[9.5pt]">{e.institution}</div>
                <div className="text-[8.5pt] italic">{[e.degree, e.field].filter(Boolean).join(' in ')}</div>
              </div>
              <div className="text-right text-[8.5pt]">
                <div>{e.duration}</div>
                {e.gpa && <div>GPA: {e.gpa}</div>}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Experience */}
      {resume.experience.length > 0 && (
        <section className="mb-2">
          <h2 className="text-[9pt] font-black uppercase tracking-widest border-b border-black pb-0.5 mb-1">Experience</h2>
          {resume.experience.map((e, i) => (
            <div key={i} className="mb-2">
              <div className="flex justify-between">
                <div className="font-bold text-[9.5pt]">{e.company}</div>
                <div className="text-[8.5pt]">{e.duration}</div>
              </div>
              <div className="flex justify-between mb-1">
                <div className="italic text-[8.5pt]">{e.role}</div>
                <div className="text-[8.5pt]">{e.location}</div>
              </div>
              <ul className="list-disc pl-4 space-y-0.5">
                {e.bullets.slice(0, 4).map((b, j) => (
                  <li key={j} className="text-[8.5pt]">{b}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Projects */}
      {resume.projects.length > 0 && (
        <section className="mb-2">
          <h2 className="text-[9pt] font-black uppercase tracking-widest border-b border-black pb-0.5 mb-1">Projects</h2>
          {resume.projects.slice(0, 3).map((p, i) => (
            <div key={i} className="mb-1.5">
              <div className="flex justify-between mb-0.5">
                <span className="font-bold text-[9pt]">{p.name}</span>
                {p.tech_stack && <span className="italic text-[8pt] text-gray-600">{p.tech_stack}</span>}
              </div>
              <ul className="list-disc pl-4 space-y-0.5">
                {p.bullets.slice(0, 3).map((b, j) => (
                  <li key={j} className="text-[8.5pt]">{b}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {(resume.skills.length > 0 || resume.languages.length > 0) && (
        <section>
          <h2 className="text-[9pt] font-black uppercase tracking-widest border-b border-black pb-0.5 mb-1">Technical Skills</h2>
          <div className="text-[8.5pt] space-y-0.5">
            {resume.skills.length > 0 && (
              <div><strong>Skills: </strong>{resume.skills.join(', ')}</div>
            )}
            {resume.languages.length > 0 && (
              <div><strong>Languages: </strong>{resume.languages.join(', ')}</div>
            )}
          </div>
        </section>
      )}

      {/* Empty state */}
      {!resume.full_name && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-300">
            <div className="text-4xl mb-2">📄</div>
            <div className="text-sm font-medium">Fill in your details<br />to see a live preview</div>
          </div>
        </div>
      )}
    </div>
  )
}
