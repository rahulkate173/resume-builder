import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Landing from '@/pages/Landing'

describe('Landing page', () => {
  it('renders hero heading', () => {
    render(<BrowserRouter><Landing /></BrowserRouter>)
    expect(screen.getByText(/actually get read/i)).toBeTruthy()
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
})
