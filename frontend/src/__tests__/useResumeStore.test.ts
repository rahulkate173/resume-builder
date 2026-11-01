import { describe, it, expect, beforeEach } from 'vitest'
import { useResumeStore } from '@/store/useResumeStore'

describe('useResumeStore', () => {
  beforeEach(() => {
    useResumeStore.setState({
      resume: { ...useResumeStore.getState().resume, full_name: '', experience: [] },
      isDirty: false,
    })
  })

  it('setField marks dirty', () => {
    useResumeStore.getState().setField('full_name', 'Jane Doe')
    const s = useResumeStore.getState()
    expect(s.resume.full_name).toBe('Jane Doe')
    expect(s.isDirty).toBe(true)
  })

  it('markClean resets dirty flag', () => {
    useResumeStore.getState().setField('full_name', 'X')
    useResumeStore.getState().markClean()
    expect(useResumeStore.getState().isDirty).toBe(false)
  })

  it('addSuggestion and acceptSuggestion', () => {
    const s = { id: 'abc', type: 'bullet' as const, original: 'old', proposed: 'new', confidence: 0.9, accepted: null }
    useResumeStore.getState().addSuggestion(s)
    useResumeStore.getState().acceptSuggestion('abc')
    expect(useResumeStore.getState().suggestions[0].accepted).toBe(true)
  })

  it('setActiveTemplate updates template_key', () => {
    useResumeStore.getState().setActiveTemplate('modern')
    expect(useResumeStore.getState().activeTemplate).toBe('modern')
    expect(useResumeStore.getState().resume.template_key).toBe('modern')
  })
})
