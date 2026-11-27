import { fireEvent, render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Landing from '@/pages/Landing'

describe('Landing page', () => {
  it('renders the redesigned hero heading', () => {
    render(<BrowserRouter><Landing /></BrowserRouter>)
    expect(screen.getByRole('heading', { name: /impossible to miss/i })).toBeTruthy()
  })

  it('has CTA button', () => {
    render(<BrowserRouter><Landing /></BrowserRouter>)
    const cta = document.getElementById('cta-get-started')
    expect(cta).toBeTruthy()
  })

  it('shows feature cards', () => {
    render(<BrowserRouter><Landing /></BrowserRouter>)
    expect(screen.getByText(/Multi-Agent AI Pipeline/i)).toBeTruthy()
    expect(screen.getByText(/ATS Score Auditor/i)).toBeTruthy()
  })

  it('links to GitHub and lets visitors switch themes', () => {
    window.localStorage.removeItem('app-theme')
    render(<BrowserRouter><Landing /></BrowserRouter>)

    expect(screen.getByRole('link', { name: 'Open ResumeBuilder on GitHub' }).getAttribute('href'))
      .toBe('https://github.com/rahulkate173/resume-builder')

    const themeButton = screen.getByRole('button', { name: 'Switch to dark mode' })
    fireEvent.click(themeButton)
    expect(screen.getByRole('button', { name: 'Switch to light mode' })).toBeTruthy()
    expect(window.localStorage.getItem('app-theme')).toBe('dark')
  })
})
