import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Register from '../views/register'
import { api } from '../api/request'
import { useAuthStore } from '../stores'

// 模拟 api
vi.mock('../api/request', () => ({
  api: {
    auth: {
      sendCode: vi.fn(),
      register: vi.fn()
    }
  }
}))

// 模拟 useAuthStore
vi.mock('../stores', () => ({
  useAuthStore: vi.fn()
}))

// 模拟 useNavigate
vi.mock('react-router-dom', async (importOriginal) => {
  const original = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...original,
    useNavigate: vi.fn()
  }
})

describe('Register Page', () => {
  const mockNavigate = vi.fn()
  const mockSetAuth = vi.fn()
  const mockMessage = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
    
    // 模拟 useNavigate
    const { useNavigate } = require('react-router-dom')
    useNavigate.mockReturnValue(mockNavigate)
    
    // 模拟 useAuthStore
    useAuthStore.mockReturnValue({
      setAuth: mockSetAuth
    })
    
    // 模拟 App.useApp
    const { App } = require('antd')
    App.useApp = vi.fn(() => ({
      message: mockMessage
    }))
  })

  it('renders register page title', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    expect(screen.getByText('注册')).toBeTruthy()
    expect(screen.getByText('加入心灵伴侣AI')).toBeTruthy()
  })

  it('has phone input field with validation', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const phoneInput = screen.getByPlaceholderText('手机号')
    expect(phoneInput).toBeTruthy()
  })

  it('has password input field with validation', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const passwordInput = screen.getByPlaceholderText('密码')
    expect(passwordInput).toBeTruthy()
  })

  it('has code input field with validation', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const codeInput = screen.getByPlaceholderText('验证码')
    expect(codeInput).toBeTruthy()
  })

  it('has nickname input field (optional)', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const nicknameInput = screen.getByPlaceholderText('昵称（可选）')
    expect(nicknameInput).toBeTruthy()
  })

  it('has register button', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const registerButton = screen.getByText('注册')
    expect(registerButton).toBeTruthy()
  })

  it('has link to login page', () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    const loginLink = screen.getByText('立即登录')
    expect(loginLink).toBeTruthy()
  })

  it('sends verification code when get code button is clicked with valid phone', async () => {
    const { api } = require('../api/request')
    api.auth.sendCode.mockResolvedValue({})
    
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    // 输入手机号
    const phoneInput = screen.getByPlaceholderText('手机号')
    fireEvent.change(phoneInput, { target: { value: '13800138000' } })
    
    // 点击获取验证码按钮
    const getCodeButton = screen.getByText('获取验证码')
    fireEvent.click(getCodeButton)
    
    expect(api.auth.sendCode).toHaveBeenCalledWith('13800138000')
    expect(mockMessage.success).toHaveBeenCalledWith('验证码已发送')
  })

  it('shows warning when get code button is clicked with invalid phone', async () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    // 输入无效手机号
    const phoneInput = screen.getByPlaceholderText('手机号')
    fireEvent.change(phoneInput, { target: { value: '123456789' } })
    
    // 点击获取验证码按钮
    const getCodeButton = screen.getByText('获取验证码')
    fireEvent.click(getCodeButton)
    
    expect(mockMessage.warning).toHaveBeenCalledWith('请先输入正确的手机号')
  })

  it('registers successfully with valid credentials', async () => {
    const { api } = require('../api/request')
    api.auth.register.mockResolvedValue({
      user: { id: 1, phone: '13800138000' },
      access_token: 'test-token',
      refresh_token: 'test-refresh-token'
    })
    
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    // 输入表单数据
    const phoneInput = screen.getByPlaceholderText('手机号')
    const codeInput = screen.getByPlaceholderText('验证码')
    const passwordInput = screen.getByPlaceholderText('密码')
    const nicknameInput = screen.getByPlaceholderText('昵称（可选）')
    
    fireEvent.change(phoneInput, { target: { value: '13800138000' } })
    fireEvent.change(codeInput, { target: { value: '123456' } })
    fireEvent.change(passwordInput, { target: { value: '123456' } })
    fireEvent.change(nicknameInput, { target: { value: '测试用户' } })
    
    // 点击注册按钮
    const registerButton = screen.getByText('注册')
    fireEvent.click(registerButton)
    
    expect(api.auth.register).toHaveBeenCalledWith({
      phone: '13800138000',
      code: '123456',
      password: '123456',
      nickname: '测试用户'
    })
    expect(mockSetAuth).toHaveBeenCalledWith(
      { id: 1, phone: '13800138000' },
      'test-token',
      'test-refresh-token'
    )
    expect(mockMessage.success).toHaveBeenCalledWith('注册成功')
    expect(mockNavigate).toHaveBeenCalledWith('/mbti')
  })

  it('shows error when registration fails', async () => {
    const { api } = require('../api/request')
    api.auth.register.mockRejectedValue({
      response: {
        data: {
          detail: '注册失败'
        }
      }
    })
    
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
    
    // 输入表单数据
    const phoneInput = screen.getByPlaceholderText('手机号')
    const codeInput = screen.getByPlaceholderText('验证码')
    const passwordInput = screen.getByPlaceholderText('密码')
    
    fireEvent.change(phoneInput, { target: { value: '13800138000' } })
    fireEvent.change(codeInput, { target: { value: '123456' } })
    fireEvent.change(passwordInput, { target: { value: '123456' } })
    
    // 点击注册按钮
    const registerButton = screen.getByText('注册')
    fireEvent.click(registerButton)
    
    expect(mockMessage.error).toHaveBeenCalledWith('注册失败')
  })
})
