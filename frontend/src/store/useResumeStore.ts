import { create } from 'zustand'

export type ExperienceEntry = {
  company: string; role: string; duration: string; location: string; bullets: string[]
}
export type EducationEntry = {
  institution: string; degree: string; field: string; duration: string; gpa: string; bullets: string[]
}
export type ProjectEntry = {
  name: string; tech_stack: string; duration: string; bullets: string[]; link: string
}
export type CertificationEntry = { name: string; issuer: string; date: string; link: string }
export type AchievementEntry   = { title: string; description: string }

export interface ResumeData {
  id: string | null
  title: string
  job_role: string
  company: string
  job_description: string
  template_key: string
  // Profile sections
  full_name: string; email: string; phone: string; location: string
  linkedin: string; github: string; leetcode: string; codeforces: string
  portfolio: string; kaggle: string; twitter: string
  professional_summary: string
  experience: ExperienceEntry[]
  education: EducationEntry[]
  projects: ProjectEntry[]
  certifications: CertificationEntry[]
  achievements: AchievementEntry[]
  skills: string[]
  languages: string[]
  // Generated
  latex_output: string
  verified: boolean
  verification_score: number
  ats_score: number
  jd_match_score: number
  has_pdf: boolean
}

export const defaultResumeData: ResumeData = {
  id: null, title: '', job_role: '', company: '', job_description: '',
  template_key: 'executive',
  full_name: '', email: '', phone: '', location: '',
  linkedin: '', github: '', leetcode: '', codeforces: '',
  portfolio: '', kaggle: '', twitter: '',
  professional_summary: '',
  experience: [], education: [], projects: [],
  certifications: [], achievements: [],
  skills: [], languages: [],
  latex_output: '', verified: false,
  verification_score: 0, ats_score: 0, jd_match_score: 0, has_pdf: false,
}

interface AgentSuggestion {
  id: string
  type: 'bullet' | 'summary' | 'skill' | 'ats_fix'
  original: string
  proposed: string
  confidence: number
  accepted: boolean | null
}

interface ResumeStore {
  resume: ResumeData
  isDirty: boolean
  activeTab: string
  activeTemplate: string
  agentRunning: boolean
  agentSteps: Array<{ step: string; status: string; message: string }>
  suggestions: AgentSuggestion[]
  showAgentPanel: boolean

  setResume: (data: Partial<ResumeData>) => void
  setField: <K extends keyof ResumeData>(key: K, value: ResumeData[K]) => void
  setActiveTab: (tab: string) => void
  setActiveTemplate: (key: string) => void
  setAgentRunning: (v: boolean) => void
  addAgentStep: (step: { step: string; status: string; message: string }) => void
  clearAgentSteps: () => void
  addSuggestion: (s: AgentSuggestion) => void
  acceptSuggestion: (id: string) => void
  rejectSuggestion: (id: string) => void
  clearSuggestions: () => void
  toggleAgentPanel: () => void
  markClean: () => void
}

export const useResumeStore = create<ResumeStore>()((set, get) => ({
  resume: { ...defaultResumeData },
  isDirty: false,
  activeTab: 'personal',
  activeTemplate: 'executive',
  agentRunning: false,
  agentSteps: [],
  suggestions: [],
  showAgentPanel: false,

  setResume: (data) =>
    set((s) => ({ resume: { ...s.resume, ...data }, isDirty: true })),

  setField: (key, value) =>
    set((s) => ({ resume: { ...s.resume, [key]: value }, isDirty: true })),

  setActiveTab: (tab) => set({ activeTab: tab }),
  setActiveTemplate: (key) =>
    set((s) => ({ activeTemplate: key, resume: { ...s.resume, template_key: key }, isDirty: true })),

  setAgentRunning: (v) => set({ agentRunning: v }),
  addAgentStep: (step) => set((s) => ({ agentSteps: [...s.agentSteps, step] })),
  clearAgentSteps: () => set({ agentSteps: [] }),

  addSuggestion: (s) => set((st) => ({ suggestions: [...st.suggestions, s] })),
  acceptSuggestion: (id) =>
    set((s) => ({
      suggestions: s.suggestions.map((sg) => sg.id === id ? { ...sg, accepted: true } : sg),
    })),
  rejectSuggestion: (id) =>
    set((s) => ({
      suggestions: s.suggestions.map((sg) => sg.id === id ? { ...sg, accepted: false } : sg),
    })),
  clearSuggestions: () => set({ suggestions: [] }),

  toggleAgentPanel: () => set((s) => ({ showAgentPanel: !s.showAgentPanel })),
  markClean: () => set({ isDirty: false }),
}))
