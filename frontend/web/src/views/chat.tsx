import { useEffect, useState, useRef } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { Input, Button, List, Spin, Empty, Drawer, App } from 'antd'
import { SendOutlined, ArrowLeftOutlined, UserOutlined, MenuOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore, useChatStore } from '../stores'
import { useIsMobile } from '../hooks/useIsMobile'

const { TextArea } = Input

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  message_type?: string
  is_collected?: boolean
  emotion?: string
  sentiment_score?: number
}

export default function Chat() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { sessionId } = useParams()
  const { user } = useAuthStore()
  const { messages, setMessages, addMessage, loading, setLoading, conversations, setConversations } = useChatStore()

  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState(sessionId)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()

  useEffect(() => {
    if (sessionId) {
      setCurrentSessionId(sessionId)
      loadHistory(sessionId)
    }
    loadConversations()
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadConversations = async () => {
    try {
      const res = await api.chat.conversations()
      setConversations(res.list || [])
    } catch (error) {
      console.error(error)
    }
  }

  const loadHistory = async (sid: string) => {
    setLoading(true)
    try {
      const res = await api.chat.history(sid)
      setMessages(res.list || [])
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || sending) return

    const content = inputValue.trim()
    setInputValue('')
    setSending(true)

    const tempId = Date.now()
    addMessage({
      id: tempId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    } as any)

    try {
      const res = await api.chat.send({
        session_id: currentSessionId,
        content,
      })

      if (!currentSessionId && res.session_id) {
        setCurrentSessionId(res.session_id)
        navigate(`/chat/${res.session_id}`, { replace: true })
      }

      addMessage({
        id: res.assistant_message.id,
        role: 'assistant',
        content: res.assistant_message.content,
        created_at: res.assistant_message.created_at,
        message_type: 'text',
        is_collected: false,
      } as Message)

      loadConversations()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '发送失败')
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const sidebarContent = (
    <>
      <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
        <Link to="/">
          <Button icon={<ArrowLeftOutlined />} type="text">
            返回首页
          </Button>
        </Link>
        <h2 style={{ marginTop: 16 }}>对话列表</h2>
      </div>
      <div style={{ flex: 1, overflow: 'auto' }}>
        {conversations.length === 0 ? (
          <Empty description="暂无对话" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <List
            dataSource={conversations}
            renderItem={(item: any) => (
              <List.Item
                onClick={() => {
                  navigate(`/chat/${item.session_id}`)
                  setSidebarOpen(false)
                }}
                style={{
                  cursor: 'pointer',
                  padding: '12px 16px',
                  background: currentSessionId === item.session_id ? '#f0f5ff' : 'transparent',
                }}
              >
                <List.Item.Meta
                  avatar={<UserOutlined style={{ fontSize: 24, color: '#722ed1' }} />}
                  title={item.title || '新对话'}
                  description={`${item.message_count} 条消息`}
                />
              </List.Item>
            )}
          />
        )}
      </div>
      <div style={{ padding: 16, borderTop: '1px solid #f0f0f0' }}>
        <Link to="/assistants">
          <Button type="primary" block style={{ background: '#722ed1' }}>
            选择助手
          </Button>
        </Link>
      </div>
    </>
  )

  const chatHeader = (
    <div style={{
      padding: '12px 16px',
      background: '#fff',
      borderBottom: '1px solid #f0f0f0',
      display: 'flex',
      alignItems: 'center',
      gap: 8,
    }}>
      {isMobile && (
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={() => setSidebarOpen(true)}
        />
      )}
      <h3 style={{ flex: 1, margin: 0 }}>与AI助手聊天</h3>
      <Link to="/profile">
        <Button type="text" icon={<UserOutlined />}>
          {user?.nickname || '我的'}
        </Button>
      </Link>
    </div>
  )

  const chatInput = (
    <div style={{
      padding: 12,
      background: '#fff',
      borderTop: '1px solid #f0f0f0',
      position: 'sticky',
      bottom: 0,
    }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你想说的话..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={sending}
          style={{ background: '#722ed1', height: 'auto' }}
        />
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f5f5f5' }}>
      {!isMobile && (
        <div style={{
          width: 280,
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
          display: 'flex',
          flexDirection: 'column',
        }}>
          {sidebarContent}
        </div>
      )}

      {isMobile && (
        <Drawer
          title="对话列表"
          placement="left"
          onClose={() => setSidebarOpen(false)}
          open={sidebarOpen}
          width={280}
        >
          {sidebarContent}
        </Drawer>
      )}

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {chatHeader}

        <div style={{ flex: 1, overflow: 'auto', padding: isMobile ? 16 : 24 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <Spin />
            </div>
          ) : messages.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Empty description="开始一段新对话吧" />
            </div>
          ) : (
            <div>
              {messages.map((msg: any) => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    marginBottom: 24,
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div style={{
                    maxWidth: isMobile ? '85%' : '70%',
                    padding: '12px 16px',
                    borderRadius: 8,
                    background: msg.role === 'user' ? '#722ed1' : '#fff',
                    color: msg.role === 'user' ? '#fff' : '#262626',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    wordBreak: 'break-word',
                  }}>
                    {msg.content}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
              
              {sending && (
                <div style={{
                  display: 'flex',
                  marginBottom: 24,
                  justifyContent: 'flex-start',
                }}>
                  <div style={{
                    maxWidth: isMobile ? '85%' : '70%',
                    padding: '12px 16px',
                    borderRadius: 8,
                    background: '#fff',
                    color: '#262626',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}>
                    <span style={{
                      display: 'inline-block',
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: '#722ed1',
                      animation: 'typing 1.4s infinite ease-in-out',
                    }} />
                    <span style={{
                      display: 'inline-block',
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: '#722ed1',
                      animation: 'typing 1.4s infinite ease-in-out 0.2s',
                    }} />
                    <span style={{
                      display: 'inline-block',
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: '#722ed1',
                      animation: 'typing 1.4s infinite ease-in-out 0.4s',
                    }} />
                    <style>{`
                      @keyframes typing {
                        0%, 60%, 100% { transform: translateY(0); }
                        30% { transform: translateY(-10px); }
                      }
                    `}</style>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {chatInput}
      </div>
    </div>
  )
}
