import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowDown, ArrowRight, Check, CheckCircle2, FileText, Github, Moon,
  Sparkles, Sun,
} from 'lucide-react'

const FEATURES = [
  {
    number: '01 / CREATE',
    icon: FileText,
    title: 'Bring your experience',
    desc: 'Add your work history, projects, and skills to one private workspace.',
    link: 'Start your resume',
  },
  {
    number: '02 / IMPROVE',
    icon: Sparkles,
    title: 'Make every detail count',
    desc: 'AI agents refine your writing and match your resume to the role you want.',
    link: 'Explore AI tools',
  },
  {
    number: '03 / MOVE FORWARD',
    icon: CheckCircle2,
    title: 'Feel ready to apply',
    desc: 'Check ATS readiness and export a polished, job-ready PDF.',
    link: 'See the templates',
  },
]

const TEMPLATES = [
  { name: 'Executive Monochrome', tag: 'ATS READY', desc: 'Corporate & engineering' },
  { name: 'Modern Tech Minimal', tag: 'TECH', desc: 'Startups & product teams' },
  { name: 'Classic Serif Academic', tag: 'CLASSIC', desc: 'Research & finance' },
  { name: 'Compact Two-Column', tag: 'COMPACT', desc: 'Experienced professionals' },
]

export default function Landing() {
  const [isDark, setIsDark] = useState(() => window.localStorage.getItem('app-theme') === 'dark')

  const toggleTheme = () => {
    setIsDark((current) => {
      const next = !current
      window.localStorage.setItem('app-theme', next ? 'dark' : 'light')
      return next
    })
  }

  return (
    <main className={`landing-page${isDark ? ' theme-dark' : ''}`}>
      <header className="landing-nav">
        <Link to="/" className="landing-brand" aria-label="ResumeBuilder AI home">
          <span className="landing-brand-mark"><FileText aria-hidden="true" /></span>
          <span>ResumeBuilder <span className="landing-brand-ai">AI</span></span>
        </Link>

        <nav className="landing-nav-links" aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#features">What you can do</a>
          <a href="#promise">Our promise</a>
        </nav>

        <div className="landing-nav-actions">
          <button
            type="button"
            className="landing-icon-button"
            onClick={toggleTheme}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            {isDark ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
          </button>
          <a
            className="landing-icon-button"
            href="https://github.com/rahulkate173/resume-builder"
            target="_blank"
            rel="noreferrer"
            aria-label="Open ResumeBuilder on GitHub"
            title="GitHub"
          >
            <Github aria-hidden="true" />
          </a>
          <Link to="/login" className="landing-signin">Sign in</Link>
          <Link to="/register" className="landing-button landing-button-primary landing-nav-cta">
            Get started <ArrowRight aria-hidden="true" />
          </Link>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-orbit landing-hero-orbit-one" aria-hidden="true" />
        <div className="landing-hero-orbit landing-hero-orbit-two" aria-hidden="true" />
        <div className="landing-hero-content">
          <div className="landing-eyebrow"><span /> YOUR NEXT CHAPTER, IN FOCUS</div>
          <h1>Make your experience<br /> <span>impossible to miss.</span></h1>
          <p>
            Turn your story into a resume that feels like you, reads clearly,
            and is ready for the roles you want.
          </p>
          <div className="landing-hero-actions">
            <Link to="/register" id="cta-get-started" className="landing-button landing-button-primary">
              Build my resume <ArrowRight aria-hidden="true" />
            </Link>
            <a href="#how-it-works" className="landing-button landing-button-secondary">
              See how it works <ArrowDown aria-hidden="true" />
            </a>
          </div>
          <div className="landing-proof">
            <span className="landing-proof-check"><Check aria-hidden="true" /></span>
            Free to get started <i /> No credit card <i /> Export as PDF
          </div>

          <div className="landing-resume-window" aria-label="Resume editor preview">
            <div className="landing-window-bar">
              <span className="landing-window-dots"><i /><i /><i /></span>
              <span className="landing-window-title"><FileText aria-hidden="true" /> Your resume, made clear</span>
              <span className="landing-window-status"><span /> ATS CHECK READY</span>
              <span className="landing-window-menu" aria-hidden="true">···</span>
            </div>
            <div className="landing-resume-content">
              <aside className="landing-resume-sidebar">
                <span className="landing-mini-label">YOUR PROFILE</span>
                <div className="landing-resume-avatar">JD</div>
                <strong>Jordan Davis</strong>
                <span className="landing-resume-role">Product designer</span>
                <div className="landing-resume-divider" />
                <span className="landing-mini-label">RESUME SECTIONS</span>
                {['Experience', 'Education', 'Projects', 'Skills'].map((section) => (
                  <span className="landing-resume-item" key={section}><Check aria-hidden="true" /> {section}</span>
                ))}
              </aside>
              <div className="landing-resume-paper">
                <div className="landing-paper-topline"><span>JORDAN DAVIS</span><span>PRODUCT DESIGNER</span></div>
                <h2>Designing products<br />people love to use.</h2>
                <p className="landing-paper-intro">Product designer with 6+ years building thoughtful digital experiences, from early concepts to launch.</p>
                <div className="landing-paper-rule" />
                <span className="landing-mini-label">SELECTED EXPERIENCE</span>
                <div className="landing-paper-job">
                  <strong>Senior Product Designer</strong><span>2021 — PRESENT</span>
                </div>
                <p>Led product design across core workflows, helping teams simplify complex tools for thousands of customers.</p>
                <div className="landing-paper-job">
                  <strong>Product Designer</strong><span>2018 — 2021</span>
                </div>
                <p>Partnered with product and engineering to bring new ideas from research through release.</p>
              </div>
              <div className="landing-score-card">
                <span className="landing-score-icon"><Sparkles aria-hidden="true" /></span>
                <span><strong>Looking good</strong><small>ATS-ready structure</small></span>
                <CheckCircle2 aria-hidden="true" />
              </div>
            </div>
          </div>
          <div className="landing-hero-caption">A clearer view of your experience. Ready for what’s next.</div>
        </div>
      </section>

      <section className="landing-how" id="how-it-works">
        <div className="landing-section-heading">
          <div>
            <span className="landing-kicker">A LITTLE LESS GUESSWORK</span>
            <h2>From first draft<br />to next opportunity.</h2>
          </div>
          <p>Everything you need to bring your experience together, find the right words, and apply with confidence.</p>
        </div>
        <div className="landing-feature-grid">
          {FEATURES.map(({ number, icon: Icon, title, desc, link }, index) => (
            <article className="landing-feature-card" key={title}>
              <span className="landing-kicker">{number}</span>
              <div className={`landing-feature-art landing-feature-art-${index + 1}`}>
                <span className="landing-art-icon"><Icon aria-hidden="true" /></span>
                <span className="landing-art-spark"><Sparkles aria-hidden="true" /></span>
              </div>
              <h3>{title}</h3>
              <p>{desc}</p>
              <Link to="/register">{link} <ArrowRight aria-hidden="true" /></Link>
            </article>
          ))}
        </div>
        <div className="landing-capability-list" aria-label="Resume builder capabilities">
          {['Multi-Agent AI Pipeline', 'JD Gap Analysis', 'ATS Score Auditor', 'LaTeX → PDF Export'].map((capability) => (
            <span key={capability}><Check aria-hidden="true" /> {capability}</span>
          ))}
        </div>
      </section>

      <section className="landing-tools" id="features">
        <div className="landing-tools-copy">
          <span className="landing-kicker">YOUR STORY, NOT A TEMPLATE</span>
          <h2>Clarity you can<br /><span>stand behind.</span></h2>
          <p>AI helps you bring out the impact in your experience. You stay in control of every word, every detail, and the final result.</p>
          <Link to="/register" className="landing-button landing-button-primary">
            Explore the resume builder <ArrowRight aria-hidden="true" />
          </Link>
          <ul>
            <li><CheckCircle2 aria-hidden="true" /> Suggestions grounded in your experience</li>
            <li><CheckCircle2 aria-hidden="true" /> Job description matching and gap analysis</li>
            <li><CheckCircle2 aria-hidden="true" /> ATS-friendly templates, ready to export</li>
          </ul>
        </div>
        <div className="landing-template-panel">
          <div className="landing-template-panel-heading">
            <span className="landing-kicker">MADE FOR YOUR NEXT MOVE</span>
            <span className="landing-template-count">04 TEMPLATES</span>
          </div>
          <div className="landing-template-list">
            {TEMPLATES.map(({ name, tag, desc }, index) => (
              <article className="landing-template-item" key={name}>
                <div className={`landing-template-thumb landing-template-thumb-${index + 1}`} aria-hidden="true">
                  <i /><i /><i /><i /><i /><i />
                </div>
                <div className="landing-template-info">
                  <span className="landing-kicker">{tag}</span>
                  <strong>{name}</strong>
                  <span>{desc}</span>
                </div>
                <ArrowRight className="landing-template-arrow" aria-hidden="true" />
              </article>
            ))}
          </div>
          <p className="landing-template-note">All templates are designed to stay readable by people and applicant tracking systems.</p>
        </div>
      </section>

      <section className="landing-promise" id="promise">
        <span className="landing-promise-icon"><CheckCircle2 aria-hidden="true" /></span>
        <div>
          <span className="landing-kicker">A PROMISE WORTH KEEPING</span>
          <h2>Your experience stays yours.</h2>
          <p>AI can help you tell your story. It doesn’t replace your voice, your judgment, or the real work you’ve done.</p>
        </div>
        <span className="landing-promise-mark">01 <small>Clear.<br />Honest. Yours.</small></span>
      </section>

      <section className="landing-final-cta">
        <span className="landing-kicker">MAKE YOUR NEXT MOVE</span>
        <h2>Know what you bring.<br />Show where you can go.</h2>
        <Link to="/register" className="landing-button landing-button-primary">
          Create your free account <ArrowRight aria-hidden="true" />
        </Link>
        <p>Start building your resume in minutes. No credit card required.</p>
      </section>

      <footer className="landing-footer">
        <Link to="/" className="landing-brand" aria-label="ResumeBuilder AI home">
          <span className="landing-brand-mark"><FileText aria-hidden="true" /></span>
          <span>ResumeBuilder <span className="landing-brand-ai">AI</span></span>
        </Link>
        <span>Thoughtful resumes for what’s next.</span>
        <span>© 2026 ResumeBuilder AI</span>
      </footer>
    </main>
  )
}
