import { Link } from 'react-router-dom'
import {
  FileText, Cpu, Target, Zap, ArrowRight, CheckCircle2, Shield, Sparkles
} from 'lucide-react'

const FEATURES = [
  {
    icon: Cpu,
    title: 'Multi-Agent AI Pipeline',
    desc: 'Three specialised agents generate, verify, and polish your resume through a self-correcting loop.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/5 border-blue-500/20',
  },
  {
    icon: Target,
    title: 'JD Gap Analysis',
    desc: 'Paste any job description. Our AI extracts keywords, computes match scores, and tailors every bullet.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/5 border-emerald-500/20',
  },
  {
    icon: Zap,
    title: 'ATS Score Auditor',
    desc: 'Real-time ATS compliance scoring (0–100) with one-click auto-fix suggestions and keyword density.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/5 border-amber-500/20',
  },
  {
    icon: FileText,
    title: 'LaTeX → PDF Export',
    desc: 'Four premium templates compile to pixel-perfect, ATS-parseable PDFs — no watermarks, ever.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/5 border-purple-500/20',
  },
]

const TEMPLATES = [
  { name: 'Executive Monochrome', tag: 'ATS #1', desc: 'Corporate & engineering' },
  { name: 'Modern Tech Minimal',  tag: 'Tech',   desc: 'Startups & FAANG' },
  { name: 'Classic Serif Academic',tag: 'Academia',desc: 'Research & finance' },
  { name: 'Compact Two-Column',   tag: 'Senior',  desc: 'Experienced engineers' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#09090B] text-white">
      {/* ── Top nav ─────────────────────────────────────────────────────── */}
      <header className="fixed top-0 inset-x-0 z-50 border-b border-[#27272A] bg-[#09090B]/80 glass">
        <div className="max-w-screen-xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-white flex items-center justify-center">
              <FileText className="w-4 h-4 text-[#09090B]" />
            </div>
            <span className="font-semibold text-sm">ResumeBuilder <span className="text-zinc-500">AI</span></span>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/login"    className="btn-ghost text-sm">Sign in</Link>
            <Link to="/register" className="btn-primary text-sm py-2 px-3">Get Started →</Link>
          </div>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="pt-36 pb-20 px-4 text-center max-w-4xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#27272A] text-xs font-mono text-zinc-400 mb-8 animate-fade-in">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Multi-Agent AI · LaTeX PDF · ATS Optimised
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.05] text-balance mb-6 animate-slide-up">
          Build resumes that<br />
          <span className="gradient-text">actually get read.</span>
        </h1>

        <p className="text-zinc-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 animate-slide-up leading-relaxed">
          Three specialised AI agents collaborate to craft, verify, and polish your resume
          into a one-page, ATS-perfect PDF — tailored to every job description in seconds.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center animate-fade-in">
          <Link to="/register" id="cta-get-started" className="btn-primary text-base px-6 py-3">
            <Sparkles className="w-4 h-4" />
            Start Building Free
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/login" className="btn-secondary text-base px-6 py-3">
            Sign In
          </Link>
        </div>

        {/* Social proof */}
        <div className="mt-10 flex items-center justify-center gap-6 text-xs text-zinc-600 animate-fade-in">
          {['No credit card', 'Guest mode available', 'Export as PDF'].map((t) => (
            <span key={t} className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-zinc-600" /> {t}
            </span>
          ))}
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section className="py-16 px-4 max-w-screen-xl mx-auto">
        <p className="text-center section-heading mb-10">Why it's different</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map(({ icon: Icon, title, desc, color, bg }) => (
            <div key={title} className={`card-hover p-5 border ${bg}`}>
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-4 ${bg} border ${bg.split(' ')[1]}`}>
                <Icon className={`w-4.5 h-4.5 ${color}`} />
              </div>
              <h3 className="font-semibold text-sm text-white mb-2">{title}</h3>
              <p className="text-xs text-zinc-500 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Templates ─────────────────────────────────────────────────────── */}
      <section className="py-16 px-4 max-w-screen-xl mx-auto">
        <p className="text-center section-heading mb-2">4 Production Templates</p>
        <p className="text-center text-zinc-500 text-sm mb-10">
          Each template is LaTeX-based, ATS-parseable, and fully customisable.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {TEMPLATES.map(({ name, tag, desc }) => (
            <div key={name} className="card p-4 flex flex-col gap-3 hover:border-zinc-600 transition-colors">
              {/* A4 thumbnail placeholder */}
              <div className="w-full aspect-[210/297] bg-white rounded flex items-center justify-center">
                <div className="w-4/5 h-4/5 flex flex-col gap-1.5">
                  <div className="h-2 bg-zinc-200 rounded w-1/2" />
                  <div className="h-1 bg-zinc-100 rounded w-3/4" />
                  <div className="h-1 bg-zinc-100 rounded w-2/3" />
                  <div className="mt-1 h-px bg-zinc-200 w-full" />
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="h-1 bg-zinc-100 rounded" style={{ width: `${70 + (i % 3) * 10}%` }} />
                  ))}
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm text-white">{name}</span>
                  <span className="badge badge-score-high text-[10px]">{tag}</span>
                </div>
                <p className="text-xs text-zinc-500 mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA footer ────────────────────────────────────────────────────── */}
      <section className="py-20 px-4 text-center border-t border-[#27272A]">
        <Shield className="w-8 h-8 text-zinc-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-3">Ready to land your next role?</h2>
        <p className="text-zinc-500 text-sm mb-6">
          Works without an account. Start building instantly, save when you're ready.
        </p>
        <Link to="/register" className="btn-primary text-base px-8 py-3 inline-flex">
          Create Free Account →
        </Link>
        <p className="mt-4 text-xs text-zinc-600">
          Built on Groq · OpenRouter · LaTeX · FastAPI · MongoDB
        </p>
      </section>
    </div>
  )
}
