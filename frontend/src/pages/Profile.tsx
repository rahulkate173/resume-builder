import { useEffect, useState } from 'react'
import { ArrowLeft, Check, ExternalLink, Github, Loader2, Save, Search, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { profileApi } from '@/api/client'
import type { ProjectEntry } from '@/store/useResumeStore'

interface GitHubRepository {
  name: string
  description: string
  url: string
  language: string
  topics: string[]
  stars: number
  fork: boolean
}

interface SavedProfile {
  github?: string
  github_username?: string
  linkedin?: string
  linkedin_username?: string
  projects?: ProjectEntry[]
}

function extractUsername(value: string | undefined, platform: 'github' | 'linkedin') {
  if (!value) return ''
  const trimmed = value.trim().replace(/^@/, '')
  try {
    const url = new URL(trimmed.startsWith('http') ? trimmed : `https://${trimmed}`)
    if (platform === 'github' && url.hostname.endsWith('github.com')) {
      return url.pathname.split('/').filter(Boolean)[0] || ''
    }
    if (platform === 'linkedin' && url.hostname.endsWith('linkedin.com')) {
      const parts = url.pathname.split('/').filter(Boolean)
      const inIndex = parts.indexOf('in')
      return inIndex >= 0 ? parts[inIndex + 1] || '' : ''
    }
  } catch {
    return trimmed
  }
  return trimmed
}

function profileUrl(platform: 'github' | 'linkedin', username: string) {
  const cleanUsername = username.trim().replace(/^@/, '')
  if (!cleanUsername) return ''
  const baseUrl = platform === 'github' ? 'https://github.com/' : 'https://www.linkedin.com/in/'
  return `${baseUrl}${encodeURIComponent(cleanUsername)}`
}

function toProject(repo: GitHubRepository): ProjectEntry {
  const techStack = [repo.language, ...repo.topics].filter(Boolean).join(', ')
  return {
    name: repo.name,
    tech_stack: techStack,
    duration: '',
    bullets: repo.description ? [repo.description] : [],
    link: repo.url,
  }
}

export default function Profile() {
  const [githubUsername, setGithubUsername] = useState('')
  const [linkedinUsername, setLinkedinUsername] = useState('')
  const [projects, setProjects] = useState<ProjectEntry[]>([])
  const [repositories, setRepositories] = useState<GitHubRepository[]>([])
  const [selectedUrls, setSelectedUrls] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const { data } = await profileApi.get()
        const profile = data as SavedProfile
        setGithubUsername(extractUsername(profile.github_username || profile.github, 'github'))
        setLinkedinUsername(extractUsername(profile.linkedin_username || profile.linkedin, 'linkedin'))
        setProjects(profile.projects || [])
      } catch {
        toast.error('Failed to load your profile.')
      } finally {
        setLoading(false)
      }
    }
    loadProfile()
  }, [])

  const saveProfile = async (profileProjects = projects) => {
    const github = githubUsername.trim().replace(/^@/, '')
    const linkedin = linkedinUsername.trim().replace(/^@/, '')
    await profileApi.update({
      github_username: github,
      github: profileUrl('github', github),
      linkedin_username: linkedin,
      linkedin: profileUrl('linkedin', linkedin),
      projects: profileProjects,
    })
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await saveProfile()
      toast.success('Profile saved. Your links and projects are ready for resume generation.')
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to save your profile.')
    } finally {
      setSaving(false)
    }
  }

  const handleFetchRepositories = async () => {
    const username = githubUsername.trim().replace(/^@/, '')
    if (!username) {
      toast.error('Enter your GitHub username first.')
      return
    }
    setFetching(true)
    setRepositories([])
    setSelectedUrls([])
    try {
      const { data } = await profileApi.githubRepos(username)
      setRepositories(data.repositories)
      if (data.repositories.length === 0) toast('No public repositories found.')
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Could not fetch GitHub repositories.')
    } finally {
      setFetching(false)
    }
  }

  const handleImportRepositories = async () => {
    const selected = repositories.filter((repo) => selectedUrls.includes(repo.url))
    const existingUrls = new Set(projects.map((project) => project.link).filter(Boolean))
    const newProjects = [...projects, ...selected.filter((repo) => !existingUrls.has(repo.url)).map(toProject)]
    setSaving(true)
    try {
      await saveProfile(newProjects)
      setProjects(newProjects)
      setSelectedUrls([])
      toast.success(`${newProjects.length - projects.length} GitHub project${newProjects.length - projects.length === 1 ? '' : 's'} added to your profile.`)
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to import projects into your profile.')
    } finally {
      setSaving(false)
    }
  }

  const toggleRepository = (url: string) => {
    setSelectedUrls((selected) => selected.includes(url)
      ? selected.filter((item) => item !== url)
      : [...selected, url])
  }

  if (loading) {
    return (
      <div className="app-page flex items-center justify-center">
        <Loader2 className="w-7 h-7 animate-spin text-zinc-500" />
      </div>
    )
  }

  return (
    <main className="app-page px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <Link to="/dashboard" className="btn-ghost text-xs mb-6 inline-flex">
          <ArrowLeft className="w-3.5 h-3.5" /> Dashboard
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Profile &amp; social accounts</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Connect your accounts and bring public GitHub projects into your resume profile.
          </p>
        </div>

        <section className="card p-5 space-y-5">
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="github-username" className="label flex items-center gap-2">
                <Github className="w-3.5 h-3.5" /> GitHub username
              </label>
              <input
                id="github-username"
                className="input"
                placeholder="octocat"
                value={githubUsername}
                onChange={(event) => setGithubUsername(event.target.value)}
              />
            </div>
            <div>
              <label htmlFor="linkedin-username" className="label flex items-center gap-2">
                <UserRound className="w-3.5 h-3.5" /> LinkedIn username
              </label>
              <input
                id="linkedin-username"
                className="input"
                placeholder="jane-doe"
                value={linkedinUsername}
                onChange={(event) => setLinkedinUsername(event.target.value)}
              />
            </div>
          </div>
          <p className="text-xs text-zinc-600">
            Public GitHub repositories can be imported below. LinkedIn profile links are saved to your resume;
            importing profile data requires LinkedIn OAuth/API access.
          </p>
          <div className="flex flex-wrap gap-2">
            <button onClick={handleSave} disabled={saving} className="btn-primary text-xs">
              {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
              Save Profile
            </button>
            <button
              onClick={handleFetchRepositories}
              disabled={fetching || !githubUsername.trim()}
              className="btn-secondary text-xs"
            >
              {fetching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              Fetch GitHub Repositories
            </button>
          </div>
        </section>

        {repositories.length > 0 && (
          <section className="mt-6">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div>
                <h2 className="font-semibold text-white text-sm">Public repositories</h2>
                <p className="text-xs text-zinc-600 mt-1">Select projects to add to your resume profile.</p>
              </div>
              <button
                onClick={handleImportRepositories}
                disabled={!selectedUrls.length || saving}
                className="btn-primary text-xs"
              >
                {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                Import selected ({selectedUrls.length})
              </button>
            </div>
            <div className="space-y-2">
              {repositories.map((repo) => {
                const selected = selectedUrls.includes(repo.url)
                const alreadyAdded = projects.some((project) => project.link === repo.url)
                return (
                  <div
                    key={repo.url}
                    role="checkbox"
                    aria-checked={selected}
                    tabIndex={0}
                    onClick={() => toggleRepository(repo.url)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        toggleRepository(repo.url)
                      }
                    }}
                    className={`card w-full p-4 text-left flex items-start gap-3 transition-colors ${
                      selected ? 'border-violet-500/50 bg-violet-500/5' : 'hover:border-zinc-600'
                    }`}
                  >
                    <span className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${
                      selected ? 'bg-violet-500 border-violet-500 text-white' : 'border-zinc-600'
                    }`}>
                      {selected && <Check className="w-3 h-3" />}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white truncate">{repo.name}</span>
                        {repo.fork && <span className="text-[10px] text-zinc-600">fork</span>}
                        {alreadyAdded && <span className="text-[10px] text-emerald-500">in profile</span>}
                      </span>
                      {repo.description && <span className="block text-xs text-zinc-500 mt-1">{repo.description}</span>}
                      <span className="flex flex-wrap items-center gap-3 mt-2 text-[11px] text-zinc-600">
                        {repo.language && <span>{repo.language}</span>}
                        {repo.topics.slice(0, 4).map((topic) => <span key={topic}>{topic}</span>)}
                        <span>★ {repo.stars}</span>
                      </span>
                    </span>
                    <a
                      href={repo.url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(event) => event.stopPropagation()}
                      className="text-zinc-600 hover:text-white"
                      aria-label={`Open ${repo.name} on GitHub`}
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                )
              })}
            </div>
          </section>
        )}

        <p className="text-xs text-zinc-600 mt-6">
          {projects.length} project{projects.length === 1 ? '' : 's'} currently saved in your profile and available to resume generation.
        </p>
      </div>
    </main>
  )
}
