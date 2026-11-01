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

export default api
