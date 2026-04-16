import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate, useParams, Link, useSearchParams } from 'react-router-dom'
import { Input, Button, List, Spin, Empty, Drawer, App, Avatar, Tag } from 'antd'
import { SendOutlined, ArrowLeftOutlined, UserOutlined, MenuOutlined, DeleteOutlined, ReloadOutlined, HeartOutlined, TeamOutlined, BookOutlined, SmileOutlined, RocketOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore, useChatStore } from '../stores'
import { useIsMobile } from '../hooks/useIsMobile'
import { useTheme } from '../hooks/useTheme'

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
  const [searchParams] = useSearchParams()
  const { user } = useAuthStore()
  const { messages, setMessages, addMessage, loading, setLoading, conversations, setConversations } = useChatStore()
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState(sessionId)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const [tempMessageId, setTempMessageId] = useState<number | null>(null)
  const [showQuickReplies, setShowQuickReplies] = useState(true)
  const [currentAssistant, setCurrentAssistant] = useState<any>(null)
  const [assessmentStatus, setAssessmentStatus] = useState<{mbti: boolean, sbti: boolean, attachment: boolean} | null>(null)

  // 检查三位一体测评是否全部完成
  useEffect(() => {
    const checkAssessments = async () => {
      try {
        const [mbtiRes, sbtiRes, attachmentRes] = await Promise.allSettled([
          api.mbti.result(),
          api.sbti.result(),
          api.attachment.result()
        ])
        const mbtiCompleted = mbtiRes.status === 'fulfilled' && !!mbtiRes.value
        const sbtiCompleted = sbtiRes.status === 'fulfilled' && !!sbtiRes.value
        const attachmentCompleted = attachmentRes.status === 'fulfilled' && !!attachmentRes.value
        setAssessmentStatus({ mbti: mbtiCompleted, sbti: sbtiCompleted, attachment: attachmentCompleted })
        
        // 如果没有全部完成，重定向到综合测评页
        if (!mbtiCompleted || !sbtiCompleted || !attachmentCompleted) {
          message.warning('请先完成三位一体测评后再使用聊天功能')
          navigate('/comprehensive')
        }
      } catch (error) {
        console.error('检查测评状态失败:', error)
        message.error('检查测评状态失败')
        navigate('/comprehensive')
      }
    }
    checkAssessments()
  }, [navigate, message])

  // 从URL获取assistant_id并加载助手信息
  useEffect(() => {
    const assistantId = searchParams.get('assistant_id')
    if (assistantId) {
      const id = parseInt(assistantId, 10)
      api.mbti.assistantDetail(id).then((res: any) => {
        setCurrentAssistant(res)
      }).catch(console.error)
    } else {
      setCurrentAssistant(null)
    }
  }, [searchParams])

  // 加载所有会话（不按助手过滤）
  const loadAllConversations = async () => {
    try {
      const res = await api.chat.conversations()
      setConversations(res.list || [])
    } catch (error) {
      console.error(error)
    }
  }

  // 根据助手ID加载该助手的历史会话
  const loadConversationsByAssistant = async (assistantId: number) => {
    try {
      const res = await api.chat.conversations()
      // 筛选出与该助手相关的会话
      const assistantConversations = (res.list || []).filter((c: any) => c.assistant_id === assistantId)
      setConversations(assistantConversations)
      // 如果有该助手的会话，加载最新一个
      if (assistantConversations.length > 0) {
        const latestSession = assistantConversations[0]
        setCurrentSessionId(latestSession.session_id)
        loadHistory(latestSession.session_id)
      } else {
        // 没有该助手的历史会话，清空消息
        setCurrentSessionId(undefined)
        setMessages([])
      }
    } catch (error) {
      console.error(error)
    }
  }

  // 根据会话加载对应的助手信息
  const loadAssistantForConversation = async (session: any) => {
    if (session.assistant_id) {
      try {
        const res = await api.mbti.assistantDetail(session.assistant_id)
        setCurrentAssistant(res)
      } catch (error) {
        console.error(error)
      }
    }
  }

  const quickReplies = [
    { icon: <HeartOutlined />, label: '倾诉心情', prompt: '今天我有一些心情想和你分享...' },
    { icon: <TeamOutlined />, label: '人际关系', prompt: '我想聊聊关于人际关系的问题...' },
    { icon: <BookOutlined />, label: '自我成长', prompt: '我想聊一聊关于个人成长的话题...' },
    { icon: <SmileOutlined />, label: '日常分享', prompt: '今天发生了一件小事...' },
    { icon: <RocketOutlined />, label: '职业发展', prompt: '我想聊聊职业发展的问题...' },
  ]

  const handleQuickReply = (prompt: string) => {
    setInputValue(prompt)
    setShowQuickReplies(false)
    handleSend()
  }
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const isMobile = useIsMobile()

  useEffect(() => {
    if (sessionId) {
      setCurrentSessionId(sessionId)
      loadHistory(sessionId)
    }
    // 加载所有会话（不按助手过滤）
    loadAllConversations()
  }, [sessionId])

  // 切换URL参数中的assistant_id时，重新加载助手信息
  useEffect(() => {
    const assistantId = searchParams.get('assistant_id')
    if (assistantId) {
      const id = parseInt(assistantId, 10)
      // 加载该助手的信息
      api.mbti.assistantDetail(id).then((res: any) => {
        setCurrentAssistant(res)
      }).catch(console.error)
      // 切换助手时清空当前消息和WebSocket连接
      setMessages([])
      setStreamingMessage('')
      closeWebSocket()
    }
  }, [searchParams])

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

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

  const closeWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  const handleSend = useCallback(() => {
    if (!inputValue.trim() || sending) return

    const content = inputValue.trim()
    setInputValue('')
    setSending(true)
    setStreamingMessage('')

    const userTempId = Date.now()
    addMessage({
      id: userTempId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    } as any)

    // Connect WebSocket
    const assistantId = currentAssistant?.id
    const wsUrl = api.websocket.connect(currentSessionId, assistantId)
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    const assistantTempId = userTempId + 1
    setTempMessageId(assistantTempId)

    ws.onopen = () => {
      // Send message
      ws.send(JSON.stringify({
        content,
        session_id: currentSessionId || null,
        assistant_id: assistantId || null,
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'start') {
          // Session started, get session_id
          if (!currentSessionId && data.session_id) {
            setCurrentSessionId(data.session_id)
            navigate(`/chat/${data.session_id}`, { replace: true })
          }
        } else if (data.type === 'chunk') {
          // Streaming chunk
          setStreamingMessage(prev => prev + data.content)
        } else if (data.type === 'done') {
          // Stream finished
          const fullMessage = data.content || streamingMessage
          addMessage({
            id: data.message_id || assistantTempId,
            role: 'assistant',
            content: fullMessage,
            created_at: new Date().toISOString(),
            message_type: 'text',
            is_collected: false,
          } as Message)
          setStreamingMessage('')
          setTempMessageId(null)
          setSending(false)
          closeWebSocket()
          loadConversations()
        } else if (data.type === 'error') {
          // Error
          message.error(data.detail || '发送失败')
          setStreamingMessage('')
          setTempMessageId(null)
          setSending(false)
          closeWebSocket()
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      message.error('连接失败，请重试')
      setSending(false)
      setStreamingMessage('')
      setTempMessageId(null)
      closeWebSocket()
    }

    ws.onclose = () => {
      // If still sending, make sure we clean up
      if (sending) {
        setSending(false)
        setStreamingMessage('')
        setTempMessageId(null)
      }
      wsRef.current = null
    }
  }, [inputValue, currentSessionId, sending, addMessage, navigate, message])

  const handleRegenerate = () => {
    if (sending || messages.length === 0) return
    
    // Find last user message
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user')
    if (!lastUserMessage) return
    
    setInputValue(lastUserMessage.content)
    // Remove last assistant message
    const newMessages = messages.slice(0, -1)
    setMessages(newMessages)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 深色模式颜色
  const darkColors = {
    chatBg: '#1a1a1a',
    sidebarBg: '#1a1a1a',
    headerBg: '#1a1a1a',
    headerBorder: '#333333',
    inputBg: isDark ? '#262626' : '#ffffff',
    inputText: isDark ? '#ffffff' : '#262626',
    bubbleBg: isDark ? '#2d2d2d' : '#f5f5f5',
    bubbleText: isDark ? 'rgba(255, 255, 255, 0.95)' : '#262626',
    userBubbleBg: '#722ed1',
    userBubbleText: '#ffffff',
    placeholder: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.25)',
    timeColor: isDark ? 'rgba(255, 255, 255, 0.5)' : '#bfbfbf',
    nameColor: isDark ? 'rgba(255, 255, 255, 0.7)' : '#8c8c8c',
    borderColor: isDark ? '#333333' : '#f0f0f0',
  }

  // 加载指定会话的助手信息
  const handleConversationClick = async (session: any) => {
    // 先加载该会话的助手信息
    if (session.assistant_id) {
      try {
        const res = await api.mbti.assistantDetail(session.assistant_id)
        setCurrentAssistant(res)
      } catch (error) {
        console.error(error)
      }
    }
    // 导航到该会话
    navigate(`/chat/${session.session_id}`)
    setSidebarOpen(false)
  }

  const sidebarContent = (
    <>
      <div style={{ padding: 16, borderBottom: `1px solid ${darkColors.borderColor}` }}>
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
                onClick={() => handleConversationClick(item)}
                style={{
                  cursor: 'pointer',
                  padding: '12px 16px',
                  background: currentSessionId === item.session_id ? (isDark ? '#262626' : '#f0f5ff') : 'transparent',
                }}
              >
                <List.Item.Meta
                  avatar={
                    item.assistant_avatar ? (
                      <Avatar src={item.assistant_avatar} size={40} style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)' }} />
                    ) : (
                      <Avatar size={40} style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)' }}>
                        {item.assistant_name?.[0] || '助'}
                      </Avatar>
                    )
                  }
                  title={item.title || '新对话'}
                  description={
                    <div>
                      <div style={{ color: isDark ? 'rgba(255,255,255,0.6)' : '#8c8c8c' }}>
                        {item.assistant_name || '未知助手'}
                      </div>
                      <div style={{ fontSize: 12, color: isDark ? 'rgba(255,255,255,0.4)' : '#bfbfbf' }}>
                        {item.message_count} 条消息
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>
      {currentAssistant ? (
        <div style={{ padding: 16, borderTop: `1px solid ${darkColors.borderColor}` }}>
          <div style={{ textAlign: 'center' }}>
            <Avatar
              src={currentAssistant.avatar}
              size={48}
              style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', marginBottom: 8 }}
            >
              {currentAssistant.name?.[0]}
            </Avatar>
            <div style={{ fontWeight: 500, marginBottom: 4 }}>{currentAssistant.name}</div>
            {currentAssistant.mbti_type && (
              <Tag color="purple" style={{ marginBottom: 8 }}>{currentAssistant.mbti_type}</Tag>
            )}
          </div>
        </div>
      ) : (
        <div style={{ padding: 16, borderTop: `1px solid ${darkColors.borderColor}` }}>
          <Link to="/assistants">
            <Button type="primary" block style={{ background: '#722ed1' }}>
              选择助手
            </Button>
          </Link>
        </div>
      )}
    </>
  )

  const chatHeader = (
    <div style={{
      padding: '12px 16px',
      background: isDark ? darkColors.headerBg : '#fff',
      borderBottom: `1px solid ${darkColors.borderColor}`,
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
      {currentAssistant ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
          <Avatar
            src={currentAssistant.avatar}
            style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)' }}
          >
            {currentAssistant.name?.[0]}
          </Avatar>
          <div>
            <div style={{ fontWeight: 500, color: isDark ? '#fff' : '#262626' }}>{currentAssistant.name}</div>
            {currentAssistant.mbti_type && (
              <div style={{ fontSize: 12, color: darkColors.nameColor }}>{currentAssistant.mbti_type}</div>
            )}
          </div>
        </div>
      ) : (
        <h3 style={{ flex: 1, margin: 0, color: isDark ? '#fff' : '#262626' }}>与AI助手聊天</h3>
      )}
      {messages.length > 0 && !sending && (
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={handleRegenerate}
          title="重新生成"
        />
      )}
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
      background: isDark ? darkColors.headerBg : '#fff',
      borderTop: `1px solid ${darkColors.borderColor}`,
      position: 'sticky',
      bottom: 0,
    }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你想说的话...（Enter发送，Shift+Enter换行）"
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ flex: 1, background: darkColors.inputBg, color: darkColors.inputText, borderColor: darkColors.borderColor }}
          className={isDark ? 'dark-input' : ''}
          disabled={sending}
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

  if (assessmentStatus === null) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!assessmentStatus?.mbti || !assessmentStatus?.sbti || !assessmentStatus?.attachment) {
    return null // 正在重定向
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: isDark ? darkColors.chatBg : '#f5f5f5' }}>
      {!isMobile && (
        <div style={{
          width: 280,
          background: isDark ? darkColors.sidebarBg : '#fff',
          borderRight: `1px solid ${darkColors.borderColor}`,
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
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div style={{ marginBottom: 32 }}>
                <Empty description="开始一段新对话吧" />
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center' }}>
                {quickReplies.map((item, idx) => (
                  <Button
                    key={idx}
                    icon={item.icon}
                    onClick={() => handleQuickReply(item.prompt)}
                    style={{
                      borderRadius: 20,
                      background: isDark ? darkColors.inputBg : '#fff',
                      border: `1px solid ${isDark ? 'rgba(114, 46, 209, 0.3)' : '#722ed130'}`,
                      color: isDark ? '#fff' : '#262626',
                    }}
                  >
                    {item.label}
                  </Button>
                ))}
              </div>
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
                    alignItems: 'flex-end',
                    gap: 8,
                  }}
                >
                  {/* 助手消息：头像在左 */}
                  {msg.role === 'assistant' && (
                    <Avatar
                      src={currentAssistant?.avatar}
                      style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', flexShrink: 0 }}
                    >
                      {currentAssistant?.name?.[0] || 'AI'}
                    </Avatar>
                  )}
                  <div style={{ maxWidth: isMobile ? '80%' : '70%', width: '100%' }}>
                    {/* 助手名称 */}
                    {msg.role === 'assistant' && currentAssistant && (
                      <div style={{ fontSize: 12, color: darkColors.nameColor, marginBottom: 4 }}>{currentAssistant.name}</div>
                    )}
                    {/* 用户名称 */}
                    {msg.role === 'user' && (
                      <div style={{ fontSize: 12, color: darkColors.nameColor, marginBottom: 4, textAlign: 'right' }}>{user?.nickname || '我'}</div>
                    )}
                    {/* 消息气泡 */}
                    <div style={{
                      width: '100%',
                      padding: '12px 16px',
                      borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                      background: msg.role === 'user' ? darkColors.userBubbleBg : darkColors.bubbleBg,
                      color: msg.role === 'user' ? darkColors.userBubbleText : darkColors.bubbleText,
                      boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      wordBreak: 'break-word',
                      whiteSpace: 'pre-wrap',
                      overflowWrap: 'break-word',
                      textAlign: 'left',
                      minHeight: 44,
                      lineHeight: 1.6,
                      fontSize: 14,
                    }}>
                      {msg.content || '...'}
                    </div>
                    {/* 时间显示 */}
                    <div style={{
                      fontSize: 11,
                      color: darkColors.timeColor,
                      marginTop: 4,
                      textAlign: msg.role === 'user' ? 'right' : 'left',
                    }}>
                      {new Date(msg.created_at).toLocaleString('zh-CN', {
                        timeZone: 'Asia/Shanghai',
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                  {/* 用户头像在右 */}
                  {msg.role === 'user' && (
                    <Avatar
                      src={user?.avatar}
                      style={{ background: '#722ed1', flexShrink: 0 }}
                    >
                      {user?.nickname?.[0] || user?.phone?.[0] || '我'}
                    </Avatar>
                  )}
                </div>
              ))}
              
              {/* Streaming message */}
              {sending && streamingMessage.length > 0 && tempMessageId && (
                <div style={{
                  display: 'flex',
                  marginBottom: 24,
                  justifyContent: 'flex-start',
                  alignItems: 'flex-end',
                  gap: 8,
                }}>
                  <Avatar
                    src={currentAssistant?.avatar}
                    style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', flexShrink: 0 }}
                  >
                    {currentAssistant?.name?.[0] || 'AI'}
                  </Avatar>
                  <div style={{ maxWidth: isMobile ? '80%' : '70%', width: '100%' }}>
                    {currentAssistant && (
                      <div style={{ fontSize: 12, color: darkColors.nameColor, marginBottom: 4 }}>{currentAssistant.name}</div>
                    )}
                    <div style={{
                      width: '100%',
                      padding: '12px 16px',
                      borderRadius: '12px 12px 12px 4px',
                      background: darkColors.bubbleBg,
                      color: darkColors.bubbleText,
                      boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      wordBreak: 'break-word',
                      whiteSpace: 'pre-wrap',
                      overflow: 'visible',
                      textAlign: 'left',
                      minHeight: 44,
                      lineHeight: 1.6,
                      fontSize: 14,
                    }}>
                      {streamingMessage}
                    </div>
                  </div>
                </div>
              )}

              {/* Typing indicator */}
              {sending && streamingMessage.length === 0 && (
                <div style={{
                  display: 'flex',
                  marginBottom: 24,
                  justifyContent: 'flex-start',
                  alignItems: 'flex-end',
                  gap: 8,
                }}>
                  <Avatar
                    src={currentAssistant?.avatar}
                    style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', flexShrink: 0 }}
                  >
                    {currentAssistant?.name?.[0] || 'AI'}
                  </Avatar>
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '12px 12px 12px 4px',
                    background: darkColors.bubbleBg,
                    color: darkColors.bubbleText,
                    boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
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
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {chatInput}
      </div>
    </div>
  )
}
