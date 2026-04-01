import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../views/home'

describe('Home Page', () => {
  beforeEach(() => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
  })

  it('renders home page without crashing', () => {
    const element = screen.getByText(/心灵伴侣/i)
    expect(element).toBeTruthy()
  })
})
