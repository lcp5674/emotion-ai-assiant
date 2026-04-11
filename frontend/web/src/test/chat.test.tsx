import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Chat from '../views/chat'
import { api } from '../api/request'
import { useAuthStore, useChatStore } from '../stores'
import { useIsMobile } from '../hooks/useIsMobile'

// 模拟 api
vi.mock('../api/request', () => ({
  api: {
    chat: {
      conversations: vi.fn(),
      history: vi.fn()
    },
    websocket: {
      connect: vi.fn()
    }
  }
}))

// 模拟 useAuthStore
vi.mock('../stores', () => ({
  useAuthStore: vi.fn(),
  useChatStore: vi.fn()
}))

// 模拟 useIsMobile
vi.mock('../hooks/useIsMobile', () => ({
  useIsMobile: vi.fn()
}))

// 模拟 useNavigate 和 useParams
vi.mock('react-router-dom', async (importOriginal) => {
  const original = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...original,
    useNavigate: vi.fn(),
    useParams: vi.fn()
  }
})

// 模拟 WebSocket
class MockWebSocket {
  constructor(url: string) {
    this.url = url
    this.readyState = 1 // OPEN
  }
  url: string
  readyState: number
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  send(data: string) {
    this.sentData = data
  }
  sentData: string | null = null
  close() {
    this.readyState = 3 // CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }
}

global.WebSocket = MockWebSocket as any

describe('Chat Page', () => {
  const mockNavigate = vi.fn()
  const mockSetMessages = vi.fn()
  const mockAddMessage = vi.fn()
  const mockSetLoading = vi.fn()
  const mockSetConversations = vi.fn()
  const mockMessage = {
    error: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
    
    // 模拟 useNavigate 和 useParams
    const { useNavigate, useParams } = require('react-router-dom')
    useNavigate.mockReturnValue(mockNavigate)
    useParams.mockReturnValue({ sessionId: 'test-session-123' })
    
    // 模拟 useAuthStore
    useAuthStore.mockReturnValue({
      user: { id: 1, nickname: '测试用户' }
    })
    
    // 模拟 useChatStore
    useChatStore.mockReturnValue({
      messages: [],
      setMessages: mockSetMessages,
      addMessage: mockAddMessage,
      loading: false,
      setLoading: mockSetLoading,
      conversations: [],
      setConversations: mockSetConversations
    })
    
    // 模拟 useIsMobile
    useIsMobile.mockReturnValue(false)
    
    // 模拟 App.useApp
    const { App } = require('antd')
    App.useApp = vi.fn(() => ({
      message: mockMessage
    }))
    
    // 模拟 api
    const { api } = require('../api/request')
    api.chat.conversations.mockResolvedValue({ list: [] })
    api.chat.history.mockResolvedValue({ list: [] })
    api.websocket.connect.mockReturnValue('ws://localhost:8000/ws')
  })

  it('renders chat page with header', () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    expect(screen.getByText('与AI助手聊天')).toBeTruthy()
    expect(screen.getByText('测试用户')).toBeTruthy()
  })

  it('renders empty state when no messages', () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    expect(screen.getByText('开始一段新对话吧')).toBeTruthy()
  })

  it('renders loading state when loading', () => {
    // 模拟 loading 状态
    useChatStore.mockReturnValue({
      messages: [],
      setMessages: mockSetMessages,
      addMessage: mockAddMessage,
      loading: true,
      setLoading: mockSetLoading,
      conversations: [],
      setConversations: mockSetConversations
    })
    
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    expect(screen.getByRole('status')).toBeTruthy()
  })

  it('renders messages when messages exist', () => {
    const mockMessages = [
      {
        id: 1,
        role: 'user' as const,
        content: '你好',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        role: 'assistant' as const,
        content: '你好，我是AI助手',
        created_at: new Date().toISOString()
      }
    ]
    
    // 模拟 messages
    useChatStore.mockReturnValue({
      messages: mockMessages,
      setMessages: mockSetMessages,
      addMessage: mockAddMessage,
      loading: false,
      setLoading: mockSetLoading,
      conversations: [],
      setConversations: mockSetConversations
    })
    
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    expect(screen.getByText('你好')).toBeTruthy()
    expect(screen.getByText('你好，我是AI助手')).toBeTruthy()
  })

  it('sends message when send button is clicked', async () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 输入消息
    const input = screen.getByPlaceholderText('输入你想说的话...（Enter发送，Shift+Enter换行）')
    fireEvent.change(input, { target: { value: '测试消息' } })
    
    // 点击发送按钮
    const sendButton = screen.getByRole('button', { name: /发送/i })
    fireEvent.click(sendButton)
    
    // 检查是否添加了用户消息
    expect(mockAddMessage).toHaveBeenCalledWith(expect.objectContaining({
      role: 'user',
      content: '测试消息'
    }))
  })

  it('sends message when Enter key is pressed', async () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 输入消息
    const input = screen.getByPlaceholderText('输入你想说的话...（Enter发送，Shift+Enter换行）')
    fireEvent.change(input, { target: { value: '测试消息' } })
    
    // 按 Enter 键
    fireEvent.keyPress(input, { key: 'Enter', shiftKey: false })
    
    // 检查是否添加了用户消息
    expect(mockAddMessage).toHaveBeenCalledWith(expect.objectContaining({
      role: 'user',
      content: '测试消息'
    }))
  })

  it('does not send message when Shift+Enter is pressed', async () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 输入消息
    const input = screen.getByPlaceholderText('输入你想说的话...（Enter发送，Shift+Enter换行）')
    fireEvent.change(input, { target: { value: '测试消息' } })
    
    // 按 Shift+Enter 键
    fireEvent.keyPress(input, { key: 'Enter', shiftKey: true })
    
    // 检查是否没有添加消息
    expect(mockAddMessage).not.toHaveBeenCalled()
  })

  it('handles WebSocket error', async () => {
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 输入消息
    const input = screen.getByPlaceholderText('输入你想说的话...（Enter发送，Shift+Enter换行）')
    fireEvent.change(input, { target: { value: '测试消息' } })
    
    // 点击发送按钮
    const sendButton = screen.getByRole('button', { name: /发送/i })
    fireEvent.click(sendButton)
    
    // 模拟 WebSocket 错误
    const ws = (global.WebSocket as any).instances?.[0]
    if (ws && ws.onerror) {
      ws.onerror(new Event('error'))
    }
    
    // 检查是否显示错误消息
    expect(mockMessage.error).toHaveBeenCalledWith('连接失败，请重试')
  })

  it('renders sidebar with conversations', async () => {
    const mockConversations = [
      {
        session_id: 'test-session-123',
        title: '测试对话1',
        message_count: 5
      },
      {
        session_id: 'test-session-456',
        title: '测试对话2',
        message_count: 3
      }
    ]
    
    // 模拟 conversations
    useChatStore.mockReturnValue({
      messages: [],
      setMessages: mockSetMessages,
      addMessage: mockAddMessage,
      loading: false,
      setLoading: mockSetLoading,
      conversations: mockConversations,
      setConversations: mockSetConversations
    })
    
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    expect(screen.getByText('对话列表')).toBeTruthy()
    expect(screen.getByText('测试对话1')).toBeTruthy()
    expect(screen.getByText('测试对话2')).toBeTruthy()
  })

  it('renders mobile drawer when isMobile is true', () => {
    // 模拟 isMobile
    useIsMobile.mockReturnValue(true)
    
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 检查菜单按钮是否存在
    const menuButton = screen.getByRole('button', { name: /菜单/i })
    expect(menuButton).toBeTruthy()
  })

  it('handles regenerate message', async () => {
    const mockMessages = [
      {
        id: 1,
        role: 'user' as const,
        content: '你好',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        role: 'assistant' as const,
        content: '你好，我是AI助手',
        created_at: new Date().toISOString()
      }
    ]
    
    // 模拟 messages
    useChatStore.mockReturnValue({
      messages: mockMessages,
      setMessages: mockSetMessages,
      addMessage: mockAddMessage,
      loading: false,
      setLoading: mockSetLoading,
      conversations: [],
      setConversations: mockSetConversations
    })
    
    render(
      <BrowserRouter>
        <Chat />
      </BrowserRouter>
    )
    
    // 点击重新生成按钮
    const regenerateButton = screen.getByRole('button', { name: /重新生成/i })
    fireEvent.click(regenerateButton)
    
    // 检查是否设置了输入值
    const input = screen.getByPlaceholderText('输入你想说的话...（Enter发送，Shift+Enter换行）')
    expect(input).toHaveValue('你好')
    
    // 检查是否更新了消息列表
    expect(mockSetMessages).toHaveBeenCalledWith([mockMessages[0]])
  })
})
