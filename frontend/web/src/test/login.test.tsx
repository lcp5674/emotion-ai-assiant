import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Login from '../views/login'

describe('Login Page', () => {
  beforeEach(() => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
  })

  it('renders login page title', () => {
    const title = screen.getByText(/登录/i)
    expect(title).toBeTruthy()
  })

  it('has phone input field', () => {
    const phoneInput = screen.getByPlaceholderText(/手机号/i)
    expect(phoneInput).toBeTruthy()
  })

  it('has password input field', () => {
    const passwordInput = screen.getByPlaceholderText(/密码/i)
    expect(passwordInput).toBeTruthy()
  })

  it('has login button', () => {
    const loginButton = screen.getByRole('button', { name: /登录/i })
    expect(loginButton).toBeTruthy()
  })
})
