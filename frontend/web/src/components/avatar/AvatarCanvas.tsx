/**
 * Avatar Canvas Component - 渲染画布
 * 用于展示AI助手的Live2D/VRM虚拟形象
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { Spin } from 'antd'
import './AvatarCanvas.css'

// 表情配置
export const EXPRESSIONS = {
  neutral: { emoji: '😐', color: '#8c8c8c' },
  happy: { emoji: '😊', color: '#52c41a' },
  sad: { emoji: '😢', color: '#1890ff' },
  angry: { emoji: '😠', color: '#f5222d' },
  surprised: { emoji: '😲', color: '#faad14' },
  blush: { emoji: '😊', color: '#eb2f96' },
  laugh: { emoji: '😂', color: '#52c41a' },
  thinking: { emoji: '🤔', color: '#722ed1' },
  sleepy: { emoji: '😴', color: '#8c8c8c' },
  smile: { emoji: '🙂', color: '#52c41a' },
}

// 动作配置
export const MOTIONS = {
  idle: { animation: 'bounce', duration: 2000 },
  wave: { animation: 'wave', duration: 1000 },
  nod: { animation: 'nod', duration: 500 },
  shake_head: { animation: 'shake', duration: 500 },
  happy: { animation: 'jump', duration: 800 },
  sad: { animation: 'droop', duration: 1500 },
  speak: { animation: 'talk', duration: 500 },
}

export interface AvatarCanvasProps {
  /** 虚拟形象名称 */
  name?: string
  /** 当前表情 */
  expression?: string
  /** 当前动作 */
  motion?: string
  /** 是否正在说话 */
  isSpeaking?: boolean
  /** 是否加载中 */
  loading?: boolean
  /** 缩放比例 */
  scale?: number
  /** 位置 */
  position?: { x: number; y: number }
  /** 点击回调 */
  onClick?: () => void
  /** 加载完成回调 */
  onLoad?: () => void
  /** className */
  className?: string
}

export default function AvatarCanvas({
  name = 'AI助手',
  expression = 'neutral',
  motion = 'idle',
  isSpeaking = false,
  loading = false,
  scale = 1,
  position = { x: 0, y: 0 },
  onClick,
  onLoad,
  className = '',
}: AvatarCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [currentExpression, setCurrentExpression] = useState(expression)
  const [currentMotion, setCurrentMotion] = useState(motion)
  const [isTalking, setIsTalking] = useState(isSpeaking)

  // 更新表情
  useEffect(() => {
    setCurrentExpression(expression)
  }, [expression])

  // 更新动作
  useEffect(() => {
    setCurrentMotion(motion)
  }, [motion])

  // 更新说话状态
  useEffect(() => {
    setIsTalking(isSpeaking)
  }, [isSpeaking])

  // 加载完成
  useEffect(() => {
    if (!loading && onLoad) {
      onLoad()
    }
  }, [loading, onLoad])

  const expressionConfig = EXPRESSIONS[currentExpression as keyof typeof EXPRESSIONS] || EXPRESSIONS.neutral
  const motionConfig = MOTIONS[currentMotion as keyof typeof MOTIONS] || MOTIONS.idle

  // 计算动画类名
  const getAnimationClass = () => {
    if (isTalking || currentMotion === 'speak') {
      return 'avatar-talking'
    }

    switch (currentMotion) {
      case 'wave':
        return 'avatar-wave'
      case 'nod':
        return 'avatar-nod'
      case 'shake_head':
        return 'avatar-shake'
      case 'happy':
      case 'jump':
        return 'avatar-jump'
      case 'sad':
      case 'droop':
        return 'avatar-droop'
      default:
        return 'avatar-idle'
    }
  }

  if (loading) {
    return (
      <div
        ref={containerRef}
        className={`avatar-canvas avatar-loading ${className}`}
        style={{ transform: `scale(${scale})` }}
      >
        <Spin size="large" />
        <p className="avatar-loading-text">加载虚拟形象中...</p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={`avatar-canvas ${getAnimationClass()} ${className}`}
      style={{
        transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
      }}
      onClick={onClick}
    >
      {/* 虚拟形象主体 */}
      <div className="avatar-figure">
        {/* 头部 */}
        <div
          className="avatar-head"
          style={{ borderColor: expressionConfig.color }}
        >
          {/* 脸部/表情 */}
          <div className="avatar-face">
            <span
              className="avatar-emoji"
              style={{ color: expressionConfig.color }}
            >
              {expressionConfig.emoji}
            </span>
            {/* 眼睛（根据状态变化） */}
            <div className={`avatar-eyes ${isTalking ? 'talking' : ''}`}>
              <div className="avatar-eye" />
              <div className="avatar-eye" />
            </div>
            {/* 嘴巴（根据状态变化） */}
            <div className={`avatar-mouth ${isTalking ? 'talking' : ''}`} />
          </div>
        </div>

        {/* 身体 */}
        <div className="avatar-body">
          <div className="avatar-torso" />
        </div>

        {/* 手臂 */}
        <div className={`avatar-arm avatar-arm-left ${currentMotion === 'wave' ? 'waving' : ''}`} />
        <div className={`avatar-arm avatar-arm-right ${currentMotion === 'wave' ? 'waving' : ''}`} />

        {/* 名字标签 */}
        <div className="avatar-name-tag">{name}</div>
      </div>

      {/* 动作指示器 */}
      {currentMotion && currentMotion !== 'idle' && (
        <div className="avatar-motion-indicator" style={{ color: expressionConfig.color }}>
          {motionConfig.animation}
        </div>
      )}
    </div>
  )
}