/**
 * Avatar Controller - 虚拟形象控制器
 * 负责与后端WebSocket通信，管理动画状态
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { message } from 'antd'
import { apiClient } from '../../api/request'
import { useAuthStore } from '../../stores'
import AvatarCanvas, { EXPRESSIONS, MOTIONS } from './AvatarCanvas'

export interface AvatarControllerProps {
  /** 助手ID */
  assistantId: number
  /** 助手名称 */
  assistantName?: string
  /** 位置 */
  position?: { x: number; y: number }
  /** 缩放 */
  scale?: number
  /** 是否显示在左侧 */
  showOnLeft?: boolean
  /** 用户消息回调 */
  onUserMessage?: (message: string) => void
  /** AI回复回调 */
  onAiResponse?: (response: string) => void
  /** className */
  className?: string
}

export interface AnimationState {
  expression: string
  motion: string
  isSpeaking: boolean
}

const DEFAULT_STATE: AnimationState = {
  expression: 'neutral',
  motion: 'idle',
  isSpeaking: false,
}

export default function AvatarController({
  assistantId,
  assistantName = 'AI助手',
  position = { x: 0, y: 0 },
  scale = 1,
  showOnLeft = true,
  onUserMessage,
  onAiResponse,
  className = '',
}: AvatarControllerProps) {
  const { user, access_token } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [avatarConfig, setAvatarConfig] = useState<any>(null)
  const [animationState, setAnimationState] = useState<AnimationState>(DEFAULT_STATE)
  const [currentEmotion, setCurrentEmotion] = useState<string>('neutral')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  // 连接WebSocket
  const connectWebSocket = useCallback(() => {
    if (!access_token) return

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/avatar/${assistantId}?token=${access_token}`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('Avatar WebSocket connected')
        setLoading(false)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)

          if (msg.type === 'message_sent' && msg.emotion) {
            const emotion = msg.emotion
            setAnimationState({
              expression: emotion.expression || 'neutral',
              motion: emotion.motion || 'idle',
              isSpeaking: false,
            })
            setCurrentEmotion(emotion.emotion || emotion.expression || 'neutral')
            return
          }

          if (msg.type === 'animation' && msg.data) {
            const data = msg.data
            setAnimationState({
              expression: data.expressions?.[0] || 'neutral',
              motion: data.motions?.[0] || 'idle',
              isSpeaking: false,
            })
            setCurrentEmotion(data.emotion || data.expressions?.[0] || 'neutral')
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('Avatar WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('Avatar WebSocket disconnected')
        // 尝试重连
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket()
        }, 3000)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setLoading(false)
    }
  }, [access_token, assistantId])

  // 加载虚拟形象配置 (HTTP)
  const loadAvatarConfig = useCallback(async () => {
    try {
      setLoading(true)
      const data = await apiClient.get(`/avatar/${assistantId}`)
      setAvatarConfig(data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load avatar config:', error)
      // 使用默认配置
      setAvatarConfig({
        name: assistantName,
        preset: true,
      })
      setLoading(false)
    }
  }, [assistantId, assistantName])

  // 获取动画指令 (HTTP备选)
  const fetchAnimation = useCallback(async (
    messageText?: string,
    responseText?: string,
    emotion?: string
  ) => {
    try {
      const data = await apiClient.post(`/avatar/animate/${assistantId}`, {
        message: messageText,
        response: responseText,
        emotion: emotion,
      })

      if (data && data.expressions && data.expressions.length > 0) {
        const newExpression = data.expressions[0]
        const newMotion = data.motions && data.motions.length > 0 ? data.motions[0] : 'idle'

        setAnimationState({
          expression: newExpression,
          motion: newMotion,
          isSpeaking: false,
        })

        setCurrentEmotion(data.emotion || newExpression)
      }
    } catch (error) {
      console.error('Failed to fetch animation:', error)
    }
  }, [assistantId])

  // 开始说话动画
  const startSpeaking = useCallback(() => {
    setAnimationState(prev => ({
      ...prev,
      isSpeaking: true,
    }))
  }, [])

  // 停止说话动画
  const stopSpeaking = useCallback(async () => {
    setAnimationState(prev => ({
      ...prev,
      isSpeaking: false,
    }))

    // 通过WebSocket获取回复后的动画
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'animate',
        emotion: currentEmotion,
      }))
    } else {
      await fetchAnimation()
    }
  }, [currentEmotion, fetchAnimation])

  // 发送消息时的动画
  const onUserSendMessage = useCallback(async (text: string) => {
    onUserMessage?.(text)

    // 显示思考中
    setAnimationState({
      expression: 'thinking',
      motion: 'idle',
      isSpeaking: false,
    })

    // 通过WebSocket发送
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'animate',
        message: text,
      }))
    }
  }, [onUserMessage])

  // AI回复时的动画
  const onAiResponseReceived = useCallback(async (response: string, emotion?: string) => {
    onAiResponse?.(response)

    // 开始说话动画
    startSpeaking()

    // 通过WebSocket获取动画指令
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'animate',
        response: response,
        emotion: emotion,
      }))
    } else {
      await fetchAnimation(undefined, response, emotion)
    }
  }, [onAiResponse, startSpeaking, fetchAnimation])

  // 初始化连接
  useEffect(() => {
    // 先加载配置
    loadAvatarConfig()

    // 然后建立WebSocket连接
    if (access_token) {
      connectWebSocket()
    }

    return () => {
      // 清理WebSocket
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [loadAvatarConfig, connectWebSocket, access_token])

  // 定时恢复待机动画
  useEffect(() => {
    if (animationState.motion !== 'idle' && !animationState.isSpeaking) {
      const timer = setTimeout(() => {
        setAnimationState(prev => ({
          ...prev,
          motion: 'idle',
        }))
      }, 3000)

      return () => clearTimeout(timer)
    }
  }, [animationState.motion, animationState.isSpeaking])

  return (
    <div
      className={`avatar-controller ${showOnLeft ? 'avatar-left' : 'avatar-right'} ${className}`}
      style={{
        position: 'absolute',
        [showOnLeft ? 'left' : 'right']: '20px',
        top: '50%',
        transform: 'translateY(-50%)',
        zIndex: 100,
      }}
    >
      <AvatarCanvas
        name={avatarConfig?.name || assistantName}
        expression={animationState.expression}
        motion={animationState.motion}
        isSpeaking={animationState.isSpeaking}
        loading={loading}
        scale={scale}
        position={position}
        onClick={() => {
          message.info(`你好，我是${assistantName}！`)
        }}
      />

      {/* 情感状态指示器 */}
      {currentEmotion && currentEmotion !== 'neutral' && (
        <div className="avatar-emotion-badge">
          {currentEmotion}
        </div>
      )}
    </div>
  )
}

// 导出用于直接调用的函数
export const useAvatarAnimation = (assistantId: number) => {
  const { user, access_token } = useAuthStore()
  const [animation, setAnimation] = useState<AnimationState>(DEFAULT_STATE)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!access_token) return

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/avatar/${assistantId}?token=${access_token}`

    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'animation' && msg.data) {
          setAnimation({
            expression: msg.data.expressions?.[0] || 'neutral',
            motion: msg.data.motions?.[0] || 'idle',
            isSpeaking: false,
          })
        }
      } catch (e) {
        console.error('Failed to parse message:', e)
      }
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [access_token, assistantId])

  const getAnimation = async (text?: string, emotion?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'animate',
        message: text,
        emotion: emotion,
      }))
    } else {
      // HTTP备选
      try {
        const data = await apiClient.post(`/avatar/animate/${assistantId}`, {
          message: text,
          emotion: emotion,
        })
        if (data) {
          setAnimation({
            expression: data.expressions?.[0] || 'neutral',
            motion: data.motions?.[0] || 'idle',
            isSpeaking: false,
          })
        }
      } catch (error) {
        console.error('Failed to get animation:', error)
      }
    }
  }

  return {
    animation,
    getAnimation,
  }
}