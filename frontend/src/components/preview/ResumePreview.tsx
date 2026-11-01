import { useResumeStore } from '@/store/useResumeStore'
import ExecutiveMonochrome from '@/components/templates/ExecutiveMonochrome'
import ModernTechMinimal from '@/components/templates/ModernTechMinimal'
import ClassicSerifAcademic from '@/components/templates/ClassicSerifAcademic'
import CompactTwoColumn from '@/components/templates/CompactTwoColumn'

const TEMPLATE_MAP: Record<string, React.ComponentType> = {
  executive: ExecutiveMonochrome,
  modern:    ModernTechMinimal,
  classic:   ClassicSerifAcademic,
  compact:   CompactTwoColumn,
}

export default function ResumePreview() {
  const { activeTemplate } = useResumeStore()
  const Template = TEMPLATE_MAP[activeTemplate] ?? ExecutiveMonochrome

  return (
    <div
      className="a4-preview shadow-2xl font-serif"
      style={{ fontFamily: "'Merriweather', Georgia, serif" }}
    >
      <Template />
    </div>
  )
}
