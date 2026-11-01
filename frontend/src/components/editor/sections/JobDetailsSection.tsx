import { useResumeStore } from '@/store/useResumeStore'

export default function JobDetailsSection() {
  const { resume, setField } = useResumeStore()
  return (
    <div className="space-y-4 animate-slide-up">
      <p className="section-heading">Target Job</p>
      <div>
        <label className="label">Job Role / Title *</label>
        <input id="job-role" className="input" placeholder="Senior Software Engineer"
          value={resume.job_role}
          onChange={e => setField('job_role', e.target.value)} />
      </div>
      <div>
        <label className="label">Company *</label>
        <input id="company" className="input" placeholder="Google"
          value={resume.company}
          onChange={e => setField('company', e.target.value)} />
      </div>
      <div>
        <label className="label">Resume Title (optional)</label>
        <input id="resume-title" className="input" placeholder="Google SWE Application 2024"
          value={resume.title}
          onChange={e => setField('title', e.target.value)} />
      </div>
      <div>
        <label className="label">Job Description *</label>
        <textarea id="job-description" className="textarea" rows={12}
          placeholder="Paste the full job description here. More detail = better tailoring."
          value={resume.job_description}
          onChange={e => setField('job_description', e.target.value)} />
        <p className="text-xs text-zinc-600 mt-1">
          {resume.job_description.length} chars · paste entire JD for best results
        </p>
      </div>

      {/* ATS Score widget if available */}
      {resume.ats_score > 0 && (
        <div className="card p-4 flex items-center gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold font-mono ${
              resume.ats_score >= 80 ? 'text-emerald-400' :
              resume.ats_score >= 60 ? 'text-amber-400' : 'text-red-400'
            }`}>{resume.ats_score}</div>
            <div className="text-xs text-zinc-500 mt-0.5">ATS Score</div>
          </div>
          <div className="flex-1 grid grid-cols-2 gap-2 text-xs">
            <div><span className="text-zinc-500">JD Match:</span> <span className="text-white font-mono">{resume.jd_match_score}%</span></div>
            <div><span className="text-zinc-500">Verified:</span> <span className={resume.verified ? 'text-emerald-400' : 'text-zinc-500'}>{resume.verified ? 'Yes ✓' : 'No'}</span></div>
            <div><span className="text-zinc-500">Verify Score:</span> <span className="text-white font-mono">{resume.verification_score}/100</span></div>
            <div><span className="text-zinc-500">PDF:</span> <span className={resume.has_pdf ? 'text-emerald-400' : 'text-zinc-500'}>{resume.has_pdf ? 'Ready' : 'None'}</span></div>
          </div>
        </div>
      )}
    </div>
  )
}
