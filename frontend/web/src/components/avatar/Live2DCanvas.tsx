/**
 * Live2D Canvas Component - 真实Live2D渲染
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { Spin } from 'antd'
import './Live2DCanvas.css'
import './AvatarCanvas.css'
import {
  preloadLive2DLibraries,
  getCachedLive2DModel,
  loadLive2DModel,
} from './live2dPreloader'

// 表情映射 - 扩展版
export const EXPRESSION_PARAMS: Record<string, string> = {
  neutral: 'f01',
  happy: 'f02',
  sad: 'f03',
  angry: 'f04',
  surprised: 'f03',
  blush: 'f02',
  laugh: 'f02',
  thinking: 'f01',
  sleepy: 'f03',
  smile: 'f02',
  excited: 'f02',
  grateful: 'f02',
  hopeful: 'f01',
  proud: 'f02',
  amused: 'f02',
  content: 'f02',
  love: 'f02',
  frustrated: 'f04',
  anxious: 'f03',
  fearful: 'f03',
  guilty: 'f03',
  ashamed: 'f02',
  lonely: 'f03',
  curious: 'f01',
  confused: 'f01',
  bored: 'f03',
  tired: 'f03',
  relieved: 'f02',
}

// 增强版动作映射 - 基于情绪强度选择不同的动作
// 策略: 情绪 + 强度 -> 选择不同的动作文件
export const MOTION_GROUPS: Record<string, string> = {
  // 空闲状态
  idle: 'Idle',
  idle_2: 'Idle',
  idle_3: 'Idle',
  idle_4: 'Idle',
  blink: 'Idle',
  
  // 积极情绪 - 使用TapBody中的多个动作随机播放
  happy: 'TapBody',
  excited: 'TapBody',
  grateful: 'TapBody',
  hopeful: 'TapBody',
  proud: 'TapBody',
  amused: 'TapBody',
  content: 'TapBody',
  love: 'TapBody',
  wave: 'TapBody',
  clap: 'TapBody',
  jump: 'TapBody',
  spin: 'TapBody',
  nod: 'TapBody',
  
  // 消极情绪 - 使用TapBody中的动作
  sad: 'TapBody',
  cry: 'TapBody',
  slump: 'TapBody',
  angry: 'TapBody',
  frustrated: 'TapBody',
  anxious: 'TapBody',
  fearful: 'TapBody',
  guilty: 'TapBody',
  ashamed: 'TapBody',
  lonely: 'TapBody',
  shake_head: 'TapBody',
  
  // 中性/其他情绪
  speak: 'TapBody',
  thinking: 'TapBody',
  touch_chin: 'TapBody',
  curious: 'TapBody',
  surprised: 'TapBody',
  confused: 'TapBody',
  bored: 'TapBody',
  tired: 'TapBody',
  relieved: 'TapBody',
  frown: 'TapBody',
  clench_fist: 'TapBody',
  stamp_foot: 'TapBody',
  jump_small: 'TapBody',
}

// CSS模式的表情配置 - 扩展版
const EXPRESSIONS: Record<string, { emoji: string; color: string }> = {
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
  excited: { emoji: '🤩', color: '#fa8c16' },
  grateful: { emoji: '🙏', color: '#13c2c2' },
  hopeful: { emoji: '🌟', color: '#52c41a' },
  proud: { emoji: '😎', color: '#722ed1' },
  amused: { emoji: '😄', color: '#52c41a' },
  content: { emoji: '😌', color: '#52c41a' },
  love: { emoji: '🥰', color: '#eb2f96' },
  frustrated: { emoji: '😤', color: '#fa8c16' },
  anxious: { emoji: '😰', color: '#1890ff' },
  fearful: { emoji: '😨', color: '#1890ff' },
  guilty: { emoji: '😔', color: '#8c8c8c' },
  ashamed: { emoji: '😳', color: '#eb2f96' },
  lonely: { emoji: '😔', color: '#8c8c8c' },
  curious: { emoji: '🧐', color: '#722ed1' },
  confused: { emoji: '😕', color: '#8c8c8c' },
  bored: { emoji: '😑', color: '#8c8c8c' },
  tired: { emoji: '😫', color: '#8c8c8c' },
  relieved: { emoji: '😅', color: '#52c41a' },
}

export interface Live2DCanvasProps {
  modelPath?: string
  name?: string
  expression?: string
  motion?: string
  isSpeaking?: boolean
  loading?: boolean
  scale?: number
  preferLive2D?: boolean
  onClick?: () => void
  onLoad?: () => void
  className?: string
}

// 全局状态防止多个实例同时初始化
let isAnyInstanceInitializing = false

export default function Live2DCanvas({
  modelPath = '/live2d/all/shizuku/shizuku.model.json',
  name = 'AI助手',
  expression = 'neutral',
  motion = 'idle',
  isSpeaking = false,
  loading = false,
  scale = 1,
  preferLive2D = true,
  onClick,
  onLoad,
  className = '',
}: Live2DCanvasProps) {
  const containerElementRef = useRef<HTMLDivElement | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const appRef = useRef<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const modelRef = useRef<any>(null)
  const initializedRef = useRef(false)
  const currentModelPathRef = useRef<string>(modelPath)
  const resizeObserverRef = useRef<ResizeObserver | null>(null)
  const modelNaturalSizeRef = useRef<{ width: number; height: number }>({ width: 400, height: 500 })
  const motionSequenceTimerRef = useRef<NodeJS.Timeout | null>(null)

  const [currentExpression, setCurrentExpression] = useState(expression)
  const [currentMotion, setCurrentMotion] = useState(motion)
  const [isTalking, setIsTalking] = useState(isSpeaking)
  const [modelLoaded, setModelLoaded] = useState(false)
  const [loadError, setLoadError] = useState(false)
  const [isInitializing, setIsInitializing] = useState(false)
  const [initError, setInitError] = useState<string>('')
  const motionLoopTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastAppliedExpressionRef = useRef<string>('neutral')
  const lastAppliedMotionRef = useRef<string>('idle')

  const getContainer = () => containerElementRef.current

  // 回调ref设置
  const setContainerRef = useCallback((node: HTMLDivElement | null) => {
    containerElementRef.current = node
  }, [])

  // 清理PIXI资源
  const cleanupApp = useCallback(() => {
    if (modelRef.current) {
      try {
        if (appRef.current?.stage) {
          appRef.current.stage.removeChild(modelRef.current)
        }
        if (modelRef.current.destroy) {
          modelRef.current.destroy({ children: true, texture: true })
        }
      } catch (e) {
        console.warn('清理模型时出错:', e)
      }
      modelRef.current = null
    }

    if (appRef.current) {
      try {
        if (appRef.current.view && containerElementRef.current) {
          try {
            containerElementRef.current.removeChild(appRef.current.view)
          } catch (e) {
            // ignore
          }
        }
        appRef.current.destroy(true, {
          children: true,
          texture: true,
          framework: true,
        })
      } catch (e) {
        console.warn('清理应用时出错:', e)
      }
      appRef.current = null
    }

    if (resizeObserverRef.current) {
      resizeObserverRef.current.disconnect()
      resizeObserverRef.current = null
    }

    setModelLoaded(false)
    initializedRef.current = false
    isAnyInstanceInitializing = false
  }, [])

  // 调整模型大小和位置以适应容器
  const adjustModelSize = useCallback(() => {
    const container = getContainer()
    const app = appRef.current
    const model = modelRef.current

    if (!container || !app || !model || !model.scale || !initializedRef.current) {
      return
    }

    const rect = container.getBoundingClientRect()
    const containerWidth = rect.width || 320
    const containerHeight = rect.height || 400

    app.renderer.resize(containerWidth, containerHeight)

    const { width: modelWidth, height: modelHeight } = modelNaturalSizeRef.current
    if (!modelWidth || !modelHeight || modelWidth <= 0 || modelHeight <= 0) {
      return
    }
    const scaleByWidth = containerWidth / modelWidth
    const scaleByHeight = containerHeight / modelHeight
    const fitScale = Math.min(scaleByWidth, scaleByHeight)
    const finalScale = Math.max(0.1, fitScale * 0.9)

    model.anchor.set(0.5, 0.5)
    model.position.set(containerWidth / 2, containerHeight / 2)
    model.scale.set(finalScale)
  }, [])

  // 初始化PIXI应用和Live2D
  const initApp = useCallback(async () => {
    const container = getContainer()

    console.log('🔧 Live2D initApp called, preferLive2D:', preferLive2D, 'container:', !!container)

    if (isAnyInstanceInitializing) {
      console.log('🔧 Live2D 已在初始化中，跳过')
      return
    }

    if (!container) {
      console.log('🔧 container不存在，等待')
      return
    }

    isAnyInstanceInitializing = true
    setIsInitializing(true)
    setInitError('')

    try {
      console.log('🔧 开始加载Live2D库...')
      const { PIXI, Live2DModel } = await preloadLive2DLibraries()
      // @ts-ignore
      window.PIXI = PIXI
      console.log('🔧 Live2D库加载成功')

      await new Promise(resolve => setTimeout(resolve, 30))

      if (!getContainer()) {
        console.log('🔧 container已消失，放弃初始化')
        setIsInitializing(false)
        isAnyInstanceInitializing = false
        return
      }

      const rect = container.getBoundingClientRect()
      let containerWidth = rect.width || 320
      let containerHeight = rect.height || 400

      if (containerWidth < 100) containerWidth = 320
      if (containerHeight < 100) containerHeight = 400

      let app = appRef.current
      if (!app) {
        console.log('🔧 创建PIXI Application')
        app = new PIXI.Application({
          width: containerWidth,
          height: containerHeight,
          backgroundAlpha: 0,
          resolution: window.devicePixelRatio || 1,
          autoDensity: true,
          antialias: true,
        })
        container.appendChild(app.view as HTMLCanvasElement)
        appRef.current = app

        const canvas = app.view as HTMLCanvasElement
        if (canvas) {
          canvas.style.position = 'absolute'
          canvas.style.top = '0'
          canvas.style.left = '0'
          canvas.style.width = '100%'
          canvas.style.height = '100%'
        }

        const resizeObserver = new ResizeObserver(() => {
          adjustModelSize()
        })
        resizeObserver.observe(container)
        resizeObserverRef.current = resizeObserver
      } else {
        app.renderer.resize(containerWidth, containerHeight)
      }

      const cachedModel = getCachedLive2DModel(currentModelPathRef.current)
      let model = null
      
      if (cachedModel && 
          cachedModel.anchor && 
          cachedModel.scale && 
          cachedModel.position &&
          cachedModel.width > 0 && 
          cachedModel.height > 0) {
        model = cachedModel
      } else {
        if (cachedModel) {
          console.log('Live2D 缓存无效，重新加载')
        }
        model = await loadLive2DModel(currentModelPathRef.current, Live2DModel, {
          autoInteract: false,
        })
      }

      if (!appRef.current) {
        if (model && model.destroy) {
          model.destroy({ children: true, texture: true })
        }
        setIsInitializing(false)
        isAnyInstanceInitializing = false
        return
      }

      if (!model || !model.anchor || !model.scale || !model.width || !model.height) {
        console.error('Live2D 模型无效', { width: model?.width, height: model?.height })
        setLoadError(true)
        setIsInitializing(false)
        isAnyInstanceInitializing = false
        return
      }

      const modelWidth = model.width || 400
      const modelHeight = model.height || 500
      modelNaturalSizeRef.current = { width: modelWidth, height: modelHeight }

      const scaleByWidth = containerWidth / modelWidth
      const scaleByHeight = containerHeight / modelHeight
      const fitScale = Math.min(scaleByWidth, scaleByHeight)
      const finalScale = Math.max(0.1, fitScale * 0.9)

      model.anchor.set(0.5, 0.5)
      model.position.set(containerWidth / 2, containerHeight / 2)
      model.scale.set(finalScale)

      if (modelRef.current && modelRef.current.parent === app.stage) {
        try {
          app.stage.removeChild(modelRef.current)
        } catch (e) {
          console.warn('移除旧模型出错:', e)
        }
      }

      model.on('hit', (hitAreas: string[]) => {
        if (hitAreas.includes('body') || hitAreas.includes('head')) {
          if (onClick) onClick()
        }
      })

      if (model.parent !== app.stage) {
        app.stage.addChild(model)
      }
      modelRef.current = model
      initializedRef.current = true
      setModelLoaded(true)
      console.log('✅ Live2D 模型加载成功!')

      if (onLoad) onLoad()
    } catch (error) {
      console.error('❌ Live2D 初始化失败:', error)
      setInitError(String(error))
      setLoadError(true)
    } finally {
      setIsInitializing(false)
      isAnyInstanceInitializing = false
    }
  }, [preferLive2D, onClick, onLoad, adjustModelSize])

  // 初始化 - 等待容器可用
  useEffect(() => {
    if (loading || isInitializing) return

    if (initializedRef.current && modelLoaded) {
      return
    }

    let retryCount = 0
    const maxRetries = 20

    const tryInit = () => {
      const container = getContainer()

      if (container && !initializedRef.current) {
        initApp()
      } else if (!container && retryCount < maxRetries) {
        retryCount++
        setTimeout(tryInit, 150)
      }
    }

    const timer = setTimeout(tryInit, 300)

    return () => {
      clearTimeout(timer)
    }
  }, [loading, preferLive2D, initApp, isInitializing, modelLoaded])

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      cleanupApp()
      if (motionSequenceTimerRef.current) {
        clearTimeout(motionSequenceTimerRef.current)
      }
      if (motionLoopTimerRef.current) {
        clearInterval(motionLoopTimerRef.current)
      }
    }
  }, [cleanupApp])

  // 监听props变化
  useEffect(() => {
    setCurrentExpression(expression)
  }, [expression])

  useEffect(() => {
    setCurrentMotion(motion)
  }, [motion])

  useEffect(() => {
    setIsTalking(isSpeaking)
  }, [isSpeaking])

  // 说话时触发动作
  useEffect(() => {
    if (!initializedRef.current || !modelRef.current || loadError) {
      return
    }

    const model = modelRef.current
    if (isTalking && model.motion) {
      try {
        model.motion('TapBody')
        console.log('🎤 说话时播放动作: TapBody')
      } catch (e) {
        console.warn('说话时动作播放失败:', e)
      }
    }
  }, [isTalking, loadError])

  // 应用表情并保持
  const applyExpressionPersistent = useCallback(() => {
    if (!initializedRef.current || !modelRef.current || loadError) {
      return
    }

    const model = modelRef.current
    const expressionParam = EXPRESSION_PARAMS[currentExpression]

    // 只有表情变化时才重新应用
    if (lastAppliedExpressionRef.current !== currentExpression) {
      if (expressionParam && typeof model.expression === 'function') {
        try {
          console.log('🎭 Live2D 设置表情:', currentExpression, '->', expressionParam)
          model.expression(expressionParam)
          lastAppliedExpressionRef.current = currentExpression
        } catch (e) {
          console.warn('Live2D 表情设置失败:', e)
        }
      } else if (expressionParam) {
        try {
          console.log('🎭 Live2D 设置表情(直接):', currentExpression, '->', expressionParam)
          model.expression = expressionParam
          lastAppliedExpressionRef.current = currentExpression
        } catch (e) {
          console.warn('Live2D 表情设置失败(直接):', e)
        }
      }
    }
  }, [currentExpression, loadError])

  // 应用动作并循环保持
  const applyMotionPersistent = useCallback(() => {
    if (!initializedRef.current || !modelRef.current || loadError) {
      return
    }

    const model = modelRef.current
    const motionGroup = MOTION_GROUPS[currentMotion] || currentMotion

    // 只有动作变化时才重新开始循环
    if (lastAppliedMotionRef.current !== currentMotion) {
      console.log('🎭 Live2D 动作变化，重新开始循环:', currentMotion, '->', motionGroup)
      
      // 清除之前的循环
      if (motionLoopTimerRef.current) {
        clearInterval(motionLoopTimerRef.current)
        motionLoopTimerRef.current = null
      }

      lastAppliedMotionRef.current = currentMotion

      // 如果是 idle，就不循环，保持静止
      if (motionGroup && motionGroup !== 'Idle' && currentMotion !== 'idle') {
        const playMotionWithOptions = (group: string) => {
          if (model.motion && typeof model.motion === 'function') {
            try {
              model.motion(group)
              console.log('✅ Live2D 动作播放成功:', group)
            } catch (e) {
              console.warn('❌ Live2D 动作播放失败:', e)
            }
          }
        }
        
        // 首次播放
        playMotionWithOptions(motionGroup)

        // 缩短循环间隔到1.5秒，让动画更频繁出现，增强动态感
        // 同时混合idle动作，让角色在情绪动作和微动之间切换
        motionLoopTimerRef.current = setInterval(() => {
          if (modelRef.current) {
            playMotionWithOptions(motionGroup)
          }
        }, 1500)
      }
    }
  }, [currentMotion, loadError])

  // 当Live2D模式且模型已加载时，应用表情到模型
  useEffect(() => {
    applyExpressionPersistent()
  }, [applyExpressionPersistent])

  // 当Live2D模式且模型已加载时，应用动作到模型
  useEffect(() => {
    applyMotionPersistent()
  }, [applyMotionPersistent])

  // 监听模型路径变化
  useEffect(() => {
    const newPath = modelPath
    const currentPath = currentModelPathRef.current

    if (newPath !== currentPath) {
      console.log('Live2D 模型路径变化:', currentPath, '->', newPath)
      currentModelPathRef.current = newPath

      // 当模型路径变化时，需要标记需要重新加载
      if (initializedRef.current && appRef.current) {
        // 通过重置 modelLoaded 状态来触发重新加载
        setModelLoaded(false)
      }
    }
  }, [modelPath])

  // 根据情绪获取CSS动画类名
  const getAnimationClass = () => {
    switch (currentMotion) {
      // 开心/兴奋
      case 'happy':
      case 'excited':
        return 'avatar-motion-excited'
      // 拍手
      case 'clap':
        return 'avatar-motion-clap'
      // 跳跃
      case 'jump':
        return 'avatar-motion-jump'
      // 挥手
      case 'wave':
        return 'avatar-motion-wave'
      // 点头
      case 'nod':
        return 'avatar-motion-nod'
      // 悲伤/哭泣
      case 'sad':
      case 'cry':
      case 'slump':
        return 'avatar-motion-sad'
      // 愤怒
      case 'angry':
      case 'shake_head':
      case 'frustrated':
        return 'avatar-motion-angry'
      // 思考
      case 'thinking':
      case 'touch_chin':
      case 'curious':
        return 'avatar-motion-thinking'
      // 说话
      case 'speak':
        return 'avatar-motion-speak'
      // 焦虑
      case 'anxious':
        return 'avatar-motion-anxious'
      // 惊讶
      case 'surprised':
        return 'avatar-motion-surprised'
      // 旋转
      case 'spin':
        return 'avatar-motion-spin'
      // 跺脚
      case 'stamp_foot':
        return 'avatar-motion-stamp'
      // 握拳
      case 'clench_fist':
        return 'avatar-motion-clench'
      // 哭泣
      case 'cry':
        return 'avatar-motion-cry'
      // idle
      case 'idle':
      default:
        return 'avatar-motion-idle'
    }
  }

  // 根据情绪获取头部倾斜样式
  const getHeadTransform = () => {
    switch (currentMotion) {
      case 'shake_head':
        return 'rotate(-5deg)'
      case 'nod':
        return 'rotate(3deg)'
      case 'tilt_head':
        return 'rotate(-8deg)'
      default:
        return 'rotate(0deg)'
    }
  }

  // 加载中或初始化失败时显示
  if (loading || !modelLoaded) {
    return (
      <div ref={setContainerRef} className={`live2d-canvas live2d-loading ${className}`}>
        <Spin size="large" />
        <p className="live2d-loading-text">
          加载虚拟形象中... {initError && <span style={{color: 'red', fontSize: 10}}>失败</span>}
        </p>
      </div>
    )
  }

  // Live2D 渲染 - 应用情绪动画CSS类
  const animationClass = getAnimationClass()
  return (
    <div
      ref={setContainerRef}
      className={`live2d-canvas ${animationClass} ${className}`}
      onClick={onClick}
    />
  )
}
