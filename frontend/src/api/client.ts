import axios from 'axios'
import { useAuthStore } from '@/store/useAuthStore'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120_000,
  headers: { 'Content-Type': 'application/json' },
})

// Inject Bearer token automatically
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  me: () => api.get('/auth/me'),
}

// ── Profile ───────────────────────────────────────────────────────────────────
export const profileApi = {
  get: () => api.get('/profiles/me'),
  update: (data: Record<string, unknown>) => api.put('/profiles/me', data),
  parseResume: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/profiles/parse-resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60_000,
    })
  },
}

// ── Resumes ───────────────────────────────────────────────────────────────────
export const resumeApi = {
  list: (limit = 20, skip = 0) => api.get(`/resumes?limit=${limit}&skip=${skip}`),
  get: (id: string) => api.get(`/resumes/${id}`),
  create: (data: Record<string, unknown>) => api.post('/resumes', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/resumes/${id}`, data),
  delete: (id: string) => api.delete(`/resumes/${id}`),
  duplicate: (id: string) => api.post(`/resumes/${id}/duplicate`),
  exportPdf: (id: string) =>
    api.post(`/resumes/${id}/export/pdf`, {}, { responseType: 'blob' }),
}

// ── Agents ────────────────────────────────────────────────────────────────────
export const agentApi = {
  rewriteBullet: (bullet: string, jobRole: string, jobDescription: string) =>
    api.post('/agents/rewrite-bullet', { bullet, job_role: jobRole, job_description: jobDescription }),
  atsAudit: (resumeId?: string, latexSource?: string, jobDescription?: string) =>
    api.post('/agents/ats-audit', { resume_id: resumeId, latex_source: latexSource, job_description: jobDescription }),
  tailorToJd: (resumeId: string, jobDescription: string, jobRole: string, company: string) =>
    api.post('/agents/tailor-to-jd', { resume_id: resumeId, job_description: jobDescription, job_role: jobRole, company }),
  generateSummary: (jobRole: string, jobDescription: string, seniority: string, profileSnapshot?: Record<string, unknown>) =>
    api.post('/agents/generate-summary', { job_role: jobRole, job_description: jobDescription, seniority, profile_snapshot: profileSnapshot }),
  modelStatus: () => api.get('/agents/models'),
}

// ── Health ────────────────────────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get('/health'),
}

// ── JD Resume (Agentic pipeline) ──────────────────────────────────────────────
export const jdResumeApi = {
  /**
   * Generate resume with JD using 7-agent pipeline.
   * Returns an EventSource-compatible URL for SSE progress.
   * The caller should use fetch() with the auth token for SSE.
   */
  generate: (jobRole: string, company: string, jobDescription: string, templateKey = 'classic') =>
    api.post('/jd-resume/generate', {
      job_role: jobRole,
      company,
      job_description: jobDescription,
      template_key: templateKey,
    }, {
      // Stream the response
      responseType: 'stream',
      timeout: 180_000, // 3 min for full pipeline
    }),

  /**
   * Low-level fetch with SSE streaming — preferred for progress UI.
   * Returns an AbortController for cancellation + AsyncIterable of step objects.
   */
  streamGenerate: async (
    jobRole: string,
    company: string,
    jobDescription: string,
    onStep: (step: Record<string, unknown>) => void,
    signal?: AbortSignal,
  ): Promise<Record<string, unknown>> => {
    const token = useAuthStore.getState().token
    const resp = await fetch('/api/v1/jd-resume/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ job_role: jobRole, company, job_description: jobDescription }),
      signal,
    })

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }))
      throw new Error(err.detail || 'JD pipeline failed')
    }

    const reader = resp.body?.getReader()
    const decoder = new TextDecoder()
    let finalResult: Record<string, unknown> = {}

    if (!reader) throw new Error('No response body')

    try {
      let buf = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        const lines = buf.split('\n')
        buf = lines.pop() ?? ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const step = JSON.parse(line.slice(6))
              if (step.type === 'done' || step.type === 'error') {
                finalResult = step
              }
              onStep(step)
            } catch { /* ignore parse errors */ }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }

    return finalResult
  },
}

export default api

