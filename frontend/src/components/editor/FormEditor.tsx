import { useResumeStore } from '@/store/useResumeStore'
import { User, Briefcase, GraduationCap, FolderOpen, Wrench, FileText } from 'lucide-react'
import clsx from 'clsx'
import PersonalSection from './sections/PersonalSection'
import ExperienceSection from './sections/ExperienceSection'
import EducationSection from './sections/EducationSection'
import ProjectsSection from './sections/ProjectsSection'
import SkillsSection from './sections/SkillsSection'
import JobDetailsSection from './sections/JobDetailsSection'

const TABS = [
  { key: 'job',        label: 'Job Details',  icon: FileText    },
  { key: 'personal',   label: 'Personal',     icon: User        },
  { key: 'experience', label: 'Experience',   icon: Briefcase   },
  { key: 'education',  label: 'Education',    icon: GraduationCap },
  { key: 'projects',   label: 'Projects',     icon: FolderOpen  },
  { key: 'skills',     label: 'Skills',       icon: Wrench      },
]

export default function FormEditor() {
  const { activeTab, setActiveTab } = useResumeStore()

  const renderSection = () => {
    switch (activeTab) {
      case 'job':        return <JobDetailsSection />
      case 'personal':   return <PersonalSection />
      case 'experience': return <ExperienceSection />
      case 'education':  return <EducationSection />
      case 'projects':   return <ProjectsSection />
      case 'skills':     return <SkillsSection />
      default:           return <PersonalSection />
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex overflow-x-auto border-b border-[#27272A] bg-[#09090B] px-2 pt-2 gap-0.5 shrink-0">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            id={`tab-${key}`}
            onClick={() => setActiveTab(key)}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg whitespace-nowrap transition-all border-b-2',
              activeTab === key
                ? 'border-white text-white bg-white/5'
                : 'border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-white/3'
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Section content */}
      <div className="flex-1 overflow-y-auto p-4 animate-fade-in">
        {renderSection()}
      </div>
    </div>
  )
}
