import { useResumeStore } from '@/store/useResumeStore'

export default function PersonalSection() {
  const { resume, setField } = useResumeStore()
  return (
    <div className="space-y-5 animate-slide-up">
      <p className="section-heading">Personal Information</p>
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2 sm:col-span-1">
          <label className="label">Full Name *</label>
          <input id="full-name" className="input" placeholder="Jane Doe"
            value={resume.full_name} onChange={e => setField('full_name', e.target.value)} />
        </div>
        <div className="col-span-2 sm:col-span-1">
          <label className="label">Email *</label>
          <input id="email" className="input" type="email" placeholder="jane@example.com"
            value={resume.email} onChange={e => setField('email', e.target.value)} />
        </div>
        <div>
          <label className="label">Phone</label>
          <input id="phone" className="input" placeholder="+1-555-0100"
            value={resume.phone} onChange={e => setField('phone', e.target.value)} />
        </div>
        <div>
          <label className="label">Location</label>
          <input id="location" className="input" placeholder="San Francisco, CA"
            value={resume.location} onChange={e => setField('location', e.target.value)} />
        </div>
      </div>

      <div className="divider pt-1" />
      <p className="section-heading">Online Presence</p>
      <div className="grid grid-cols-2 gap-3">
        {([
          ['linkedin',   'LinkedIn URL',    'https://linkedin.com/in/…'],
          ['github',     'GitHub URL',      'https://github.com/…'],
          ['leetcode',   'LeetCode URL',    'https://leetcode.com/u/…'],
          ['codeforces', 'Codeforces URL',  'https://codeforces.com/profile/…'],
          ['portfolio',  'Portfolio',       'https://yoursite.com'],
          ['kaggle',     'Kaggle URL',      'https://kaggle.com/…'],
          ['twitter',    'Twitter / X URL', 'https://x.com/…'],
        ] as [keyof typeof resume, string, string][]).map(([field, label, ph]) => (
          <div key={field}>
            <label className="label">{label}</label>
            <input className="input" placeholder={ph}
              value={resume[field] as string}
              onChange={e => setField(field, e.target.value)} />
          </div>
        ))}
      </div>

      <div className="divider pt-1" />
      <p className="section-heading">Professional Summary</p>
      <textarea className="textarea" rows={4}
        placeholder="3–4 sentences describing your professional identity, top strengths, and career goals…"
        value={resume.professional_summary}
        onChange={e => setField('professional_summary', e.target.value)} />
    </div>
  )
}
