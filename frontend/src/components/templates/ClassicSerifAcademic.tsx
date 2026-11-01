import { useResumeStore } from '@/store/useResumeStore'

export default function ClassicSerifAcademic() {
  const { resume } = useResumeStore()
  return (
    <div className="h-full p-[0.75in] text-[10.5pt] bg-white text-black overflow-hidden"
      style={{ fontFamily: 'Georgia, "Times New Roman", serif', lineHeight: '1.4' }}>

      {/* Header */}
      <div className="text-center mb-4">
        <h1 className="text-[20pt] font-bold tracking-wide" style={{ fontVariant: 'small-caps' }}>
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="text-[9pt] text-gray-600 mt-1.5 space-x-3">
          {[resume.phone, resume.email, resume.linkedin && 'LinkedIn', resume.github && 'GitHub']
            .filter(Boolean).join('  ·  ')}
        </div>
      </div>

      <div className="border-b border-black mb-3" />

      {/* Summary */}
      {resume.professional_summary && (
        <section className="mb-3">
          <h2 className="font-bold text-[10pt]" style={{ fontVariant: 'small-caps' }}>Professional Summary</h2>
          <div className="border-b border-gray-300 mb-1.5" />
          <p className="text-[9.5pt] leading-relaxed text-justify">{resume.professional_summary}</p>
        </section>
      )}

      {/* Education */}
      {resume.education.length > 0 && (
        <section className="mb-3">
          <h2 className="font-bold text-[10pt]" style={{ fontVariant: 'small-caps' }}>Education</h2>
          <div className="border-b border-gray-300 mb-1.5" />
          {resume.education.map((e, i) => (
            <div key={i} className="flex justify-between mb-1">
              <div>
                <div className="font-semibold">{e.institution}</div>
                <div className="italic text-[9pt]">{[e.degree, e.field].filter(Boolean).join(', ')}</div>
                {e.gpa && <div className="text-[9pt]">GPA: {e.gpa}</div>}
              </div>
              <div className="text-right text-[9pt] text-gray-600 shrink-0 ml-4">{e.duration}</div>
            </div>
          ))}
        </section>
      )}

      {/* Experience */}
      {resume.experience.length > 0 && (
        <section className="mb-3">
          <h2 className="font-bold text-[10pt]" style={{ fontVariant: 'small-caps' }}>Professional Experience</h2>
          <div className="border-b border-gray-300 mb-1.5" />
          {resume.experience.slice(0, 3).map((e, i) => (
            <div key={i} className="mb-2">
              <div className="flex justify-between">
                <span className="font-semibold">{e.role}</span>
                <span className="text-[9pt] text-gray-600">{e.duration}</span>
              </div>
              <div className="italic text-[9pt] mb-1">{e.company}{e.location ? `, ${e.location}` : ''}</div>
              <ul className="list-disc pl-5 space-y-0.5">
                {e.bullets.slice(0, 4).map((b, j) => (
                  <li key={j} className="text-[9pt]">{b}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Projects */}
      {resume.projects.length > 0 && (
        <section className="mb-3">
          <h2 className="font-bold text-[10pt]" style={{ fontVariant: 'small-caps' }}>Research &amp; Projects</h2>
          <div className="border-b border-gray-300 mb-1.5" />
          {resume.projects.slice(0, 2).map((p, i) => (
            <div key={i} className="mb-1.5">
              <div className="font-semibold">{p.name} {p.tech_stack && <span className="font-normal italic text-[9pt]">· {p.tech_stack}</span>}</div>
              <ul className="list-disc pl-5">
                {p.bullets.slice(0, 2).map((b, j) => <li key={j} className="text-[9pt]">{b}</li>)}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {(resume.skills.length > 0 || resume.languages.length > 0) && (
        <section>
          <h2 className="font-bold text-[10pt]" style={{ fontVariant: 'small-caps' }}>Skills</h2>
          <div className="border-b border-gray-300 mb-1.5" />
          <div className="text-[9pt] space-y-0.5">
            {resume.languages.length > 0 && <div><strong>Programming: </strong>{resume.languages.join(', ')}</div>}
            {resume.skills.length > 0 && <div><strong>Technical: </strong>{resume.skills.join(', ')}</div>}
          </div>
        </section>
      )}
    </div>
  )
}
