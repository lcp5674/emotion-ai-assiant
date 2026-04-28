/**
 * 情绪-动作控制器
 * 管理前端情绪状态、动作序列、过渡效果
 */
import { useState, useCallback, useRef, useEffect } from 'react'

// 动作帧接口
export interface MotionFrame {
  motion: string
  expression: string
  duration: number
  transitionIn?: number
  transitionOut?: number
}

// 情绪状态接口
export interface EmotionState {
  currentEmotion: string
  currentIntensity: number
  targetEmotion: string
  targetIntensity: number
  isTransitioning: boolean
  lastUpdateTime: number
  emotionHistory: Array<{ emotion: string; intensity: number; timestamp: number }>
}

// 控制器配置
export interface EmotionMotionControllerConfig {
  transitionDuration: number  // 过渡时长（秒）
  idleTimeout: number  // 待机超时（秒）
  maxHistoryLength: number  // 历史记录最大长度
  enableMicroExpressions: boolean  // 启用微表情
  mbtiType?: string  // MBTI类型
}

// 默认配置
const DEFAULT_CONFIG: EmotionMotionControllerConfig = {
  transitionDuration: 0.5,
  idleTimeout: 30,
  maxHistoryLength: 20,
  enableMicroExpressions: true,
}

// 情绪-动作预设配置
const EMOTION_MOTION_PRESETS: Record<string, {
  expressions: string[]
  motions: string[]
  motionSequence?: string[]
  intensityMultiplier: number
}> = {
  // 积极情绪
  joy: {
    expressions: ['happy', 'smile'],
    motions: ['happy', 'clap', 'jump'],
    motionSequence: ['smile_small', 'happy', 'clap'],
    intensityMultiplier: 1.2,
  },
  excited: {
    expressions: ['excited', 'happy', 'laugh'],
    motions: ['wave', 'happy', 'clap', 'jump', 'spin'],
    motionSequence: ['wave', 'happy', 'clap', 'jump'],
    intensityMultiplier: 1.5,
  },
  grateful: {
    expressions: ['grateful', 'smile'],
    motions: ['nod', 'bow', 'hand_on_heart'],
    motionSequence: ['smile_small', 'nod', 'bow'],
    intensityMultiplier: 0.8,
  },
  hopeful: {
    expressions: ['hopeful', 'smile'],
    motions: ['look_up', 'touch_chin', 'clench_fist'],
    motionSequence: ['thinking', 'look_up', 'clench_fist'],
    intensityMultiplier: 0.9,
  },
  proud: {
    expressions: ['proud', 'happy'],
    motions: ['stand_tall', 'puff_chest', 'victory'],
    motionSequence: ['stand_tall', 'puff_chest', 'victory'],
    intensityMultiplier: 1.3,
  },
  amused: {
    expressions: ['amused', 'laugh', 'smile'],
    motions: ['smile', 'laugh', 'clap'],
    motionSequence: ['smile', 'laugh', 'clap'],
    intensityMultiplier: 1.1,
  },
  content: {
    expressions: ['content', 'smile'],
    motions: ['relax', 'sigh_content', 'lean_back'],
    motionSequence: ['relax', 'sigh_content', 'lean_back'],
    intensityMultiplier: 0.7,
  },
  love: {
    expressions: ['love', 'happy', 'smile'],
    motions: ['smile', 'hand_on_heart', 'wave', 'hug_air'],
    motionSequence: ['smile', 'hand_on_heart', 'hug_air'],
    intensityMultiplier: 1.4,
  },
  // 消极情绪
  sad: {
    expressions: ['sad'],
    motions: ['sad', 'slump', 'cry'],
    motionSequence: ['sad', 'slump', 'cry'],
    intensityMultiplier: 1.2,
  },
  angry: {
    expressions: ['angry'],
    motions: ['frown', 'shake_head', 'clench_fist', 'stamp_foot'],
    motionSequence: ['frown', 'shake_head', 'clench_fist'],
    intensityMultiplier: 1.4,
  },
  frustrated: {
    expressions: ['frustrated', 'angry'],
    motions: ['sigh', 'shake_head', 'run_hand', 'throw_arms'],
    motionSequence: ['sigh', 'shake_head', 'throw_arms'],
    intensityMultiplier: 1.1,
  },
  anxious: {
    expressions: ['anxious', 'fearful'],
    motions: ['fidget', 'pace', 'bite_lip', 'wring_hands'],
    motionSequence: ['fidget', 'pace', 'wring_hands'],
    intensityMultiplier: 1.3,
  },
  fearful: {
    expressions: ['fearful', 'surprised'],
    motions: ['tremble', 'cower', 'cover_face', 'back_away'],
    motionSequence: ['tremble', 'cower', 'back_away'],
    intensityMultiplier: 1.5,
  },
  guilty: {
    expressions: ['guilty', 'sad'],
    motions: ['look_down', 'shift_feet', 'hang_head'],
    motionSequence: ['look_down', 'shift_feet', 'hang_head'],
    intensityMultiplier: 0.9,
  },
  ashamed: {
    expressions: ['ashamed', 'blush'],
    motions: ['look_away', 'blush', 'cover_face', 'hide'],
    motionSequence: ['look_away', 'blush', 'hide'],
    intensityMultiplier: 1.0,
  },
  lonely: {
    expressions: ['lonely', 'sad'],
    motions: ['hug_self', 'look_around', 'reach_out', 'curl_up'],
    motionSequence: ['hug_self', 'look_around', 'curl_up'],
    intensityMultiplier: 1.1,
  },
  // 中性情绪
  neutral: {
    expressions: ['neutral'],
    motions: ['idle', 'idle_2', 'idle_3', 'blink'],
    intensityMultiplier: 0.5,
  },
  thinking: {
    expressions: ['thinking'],
    motions: ['thinking', 'touch_chin', 'look_up', 'pace_slow'],
    motionSequence: ['thinking', 'touch_chin', 'look_up'],
    intensityMultiplier: 0.8,
  },
  curious: {
    expressions: ['curious', 'surprised'],
    motions: ['tilt_head', 'lean_forward', 'look_closer', 'raise_eyebrow'],
    motionSequence: ['tilt_head', 'lean_forward', 'look_closer'],
    intensityMultiplier: 0.9,
  },
  surprised: {
    expressions: ['surprised'],
    motions: ['eyes_wide', 'jump_small', 'gasp', 'cover_mouth'],
    motionSequence: ['eyes_wide', 'jump_small', 'gasp'],
    intensityMultiplier: 1.3,
  },
  confused: {
    expressions: ['confused', 'thinking'],
    motions: ['tilt_head', 'scratch_head', 'shrug', 'look_around'],
    motionSequence: ['tilt_head', 'scratch_head', 'shrug'],
    intensityMultiplier: 0.8,
  },
  bored: {
    expressions: ['bored', 'sleepy'],
    motions: ['yawn', 'stretch', 'look_away', 'tap_foot'],
    motionSequence: ['yawn', 'stretch', 'look_away'],
    intensityMultiplier: 0.6,
  },
  tired: {
    expressions: ['tired', 'sleepy'],
    motions: ['stretch', 'yawn', 'slump', 'rub_eyes'],
    motionSequence: ['stretch', 'yawn', 'slump'],
    intensityMultiplier: 0.7,
  },
  relieved: {
    expressions: ['relieved', 'smile'],
    motions: ['sigh_relief', 'shoulders_drop', 'smile_small', 'lean_back'],
    motionSequence: ['sigh_relief', 'shoulders_drop', 'smile_small'],
    intensityMultiplier: 0.9,
  },
}

// MBTI 动作偏好权重
const MBTI_MOTION_WEIGHTS: Record<string, {
  gentle: number
  expressive: number
  energetic: number
}> = {
  INFJ: { gentle: 0.9, expressive: 0.3, energetic: 0.2 },
  INTJ: { gentle: 0.5, expressive: 0.4, energetic: 0.3 },
  ENFP: { gentle: 0.3, expressive: 0.9, energetic: 0.8 },
  ENFJ: { gentle: 0.7, expressive: 0.7, energetic: 0.5 },
  ISTP: { gentle: 0.4, expressive: 0.3, energetic: 0.4 },
  ISFJ: { gentle: 0.8, expressive: 0.5, energetic: 0.3 },
  INFP: { gentle: 0.7, expressive: 0.6, energetic: 0.4 },
  ENTJ: { gentle: 0.3, expressive: 0.5, energetic: 0.6 },
}

// 动作类型分类
const MOTION_TYPE_MAP: Record<string, 'gentle' | 'expressive' | 'energetic'> = {
  idle: 'gentle',
  idle_2: 'gentle',
  idle_3: 'gentle',
  idle_4: 'gentle',
  blink: 'gentle',
  smile_small: 'gentle',
  nod: 'gentle',
  relax: 'gentle',
  sigh_content: 'gentle',
  lean_back: 'gentle',
  touch_chin: 'gentle',
  tilt_head: 'gentle',
  look_up: 'gentle',
  wave: 'expressive',
  clap: 'expressive',
  laugh: 'expressive',
  happy: 'expressive',
  shrug: 'expressive',
  throw_arms: 'expressive',
  gasp: 'expressive',
  jump: 'energetic',
  spin: 'energetic',
  victory: 'energetic',
  stamp_foot: 'energetic',
  pace: 'energetic',
}

export class EmotionMotionController {
  private state: EmotionState
  private config: EmotionMotionControllerConfig
  private listeners: Array<(state: EmotionState) => void> = []
  private idleTimerRef: NodeJS.Timeout | null = null

  constructor(config?: Partial<EmotionMotionControllerConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.state = {
      currentEmotion: 'neutral',
      currentIntensity: 1,
      targetEmotion: 'neutral',
      targetIntensity: 1,
      isTransitioning: false,
      lastUpdateTime: Date.now(),
      emotionHistory: [],
    }
    this.startIdleTimer()
  }

  // 获取当前状态
  getState(): EmotionState {
    return { ...this.state }
  }

  // 设置配置
  setConfig(config: Partial<EmotionMotionControllerConfig>): void {
    this.config = { ...this.config, ...config }
  }

  // 添加状态监听器
  addListener(listener: (state: EmotionState) => void): () => void {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  // 通知监听器
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.getState()))
  }

  // 设置情绪
  setEmotion(emotion: string, intensity: number = 1, immediate: boolean = false): void {
    // 验证强度范围
    intensity = Math.max(1, Math.min(5, intensity))
    
    // 更新目标状态
    this.state.targetEmotion = emotion
    this.state.targetIntensity = intensity
    
    // 添加到历史
    this.state.emotionHistory.push({
      emotion,
      intensity,
      timestamp: Date.now(),
    })
    
    // 限制历史长度
    if (this.state.emotionHistory.length > this.config.maxHistoryLength) {
      this.state.emotionHistory = this.state.emotionHistory.slice(-this.config.maxHistoryLength)
    }
    
    if (immediate) {
      // 立即切换
      this.state.currentEmotion = emotion
      this.state.currentIntensity = intensity
      this.state.isTransitioning = false
      this.state.lastUpdateTime = Date.now()
      this.notifyListeners()
    } else {
      // 平滑过渡
      this.startTransition()
    }
    
    // 重置待机计时器
    this.resetIdleTimer()
  }

  // 开始过渡
  private startTransition(): void {
    if (this.state.isTransitioning) return
    
    this.state.isTransitioning = true
    this.notifyListeners()
    
    // 模拟过渡过程
    setTimeout(() => {
      this.state.currentEmotion = this.state.targetEmotion
      this.state.currentIntensity = this.state.targetIntensity
      this.state.isTransitioning = false
      this.state.lastUpdateTime = Date.now()
      this.notifyListeners()
    }, this.config.transitionDuration * 1000)
  }

  // 获取当前表情
  getCurrentExpression(): string {
    const preset = EMOTION_MOTION_PRESETS[this.state.currentEmotion]
    if (!preset) return 'neutral'
    
    const expressions = preset.expressions
    return expressions[Math.floor(Math.random() * expressions.length)]
  }

  // 获取当前动作
  getCurrentMotion(): string {
    const preset = EMOTION_MOTION_PRESETS[this.state.currentEmotion]
    if (!preset) return 'idle'
    
    let motions = preset.motions
    
    // 根据MBTI类型过滤
    if (this.config.mbtiType) {
      motions = this.filterMotionsByMBTI(motions, this.config.mbtiType)
    }
    
    return motions[Math.floor(Math.random() * motions.length)]
  }

  // 获取动作序列
  getMotionSequence(duration: number = 3.0): MotionFrame[] {
    const preset = EMOTION_MOTION_PRESETS[this.state.currentEmotion]
    if (!preset || !preset.motionSequence) {
      return [{ motion: this.getCurrentMotion(), expression: this.getCurrentExpression(), duration }]
    }
    
    const sequence = preset.motionSequence
    const frameDuration = duration / sequence.length
    
    return sequence.map((motion, index) => ({
      motion,
      expression: preset.expressions[index % preset.expressions.length],
      duration: frameDuration,
      transitionIn: index === 0 ? 0.2 : 0.1,
      transitionOut: index === sequence.length - 1 ? 0.3 : 0.1,
    }))
  }

  // 根据MBTI过滤动作
  private filterMotionsByMBTI(motions: string[], mbtiType: string): string[] {
    const weights = MBTI_MOTION_WEIGHTS[mbtiType]
    if (!weights) return motions
    
    // 为每个动作打分
    const scoredMotions = motions.map(motion => {
      const type = MOTION_TYPE_MAP[motion] || 'gentle'
      const weight = weights[type]
      const randomFactor = 0.7 + Math.random() * 0.6  // 0.7-1.3
      return { motion, score: weight * randomFactor }
    })
    
    // 按分数排序
    scoredMotions.sort((a, b) => b.score - a.score)
    
    // 返回前3个动作
    return scoredMotions.slice(0, 3).map(m => m.motion)
  }

  // 获取微表情
  getMicroExpressions(): string[] {
    if (!this.config.enableMicroExpressions) return []
    
    const preset = EMOTION_MOTION_PRESETS[this.state.currentEmotion]
    if (!preset) return []
    
    // 返回前2个表情作为微表情
    return preset.expressions.slice(0, 2)
  }

  // 获取待机动画
  getIdleAnimation(): MotionFrame[] {
    const idlePreset = EMOTION_MOTION_PRESETS['neutral']
    const timeSinceActive = (Date.now() - this.state.lastUpdateTime) / 1000
    
    let idleMotions = [...idlePreset.motions]
    
    // 根据时间增加变化
    if (timeSinceActive > 30) {
      idleMotions.push('stretch', 'look_around', 'shift_feet')
    }
    if (timeSinceActive > 60) {
      idleMotions.push('yawn', 'smile_small', 'sigh_content')
    }
    
    // 根据MBTI过滤
    if (this.config.mbtiType) {
      idleMotions = this.filterMotionsByMBTI(idleMotions, this.config.mbtiType)
    }
    
    // 生成3-5个待机动画帧
    const numFrames = Math.min(3 + Math.floor(Math.random() * 3), idleMotions.length)
    const frames: MotionFrame[] = []
    
    for (let i = 0; i < numFrames; i++) {
      const motion = idleMotions[i % idleMotions.length]
      frames.push({
        motion,
        expression: 'neutral',
        duration: 1.0 + Math.random() * 1.5,
        transitionIn: 0.1,
        transitionOut: 0.1,
      })
    }
    
    return frames
  }

  // 启动待机计时器
  private startIdleTimer(): void {
    this.idleTimerRef = setTimeout(() => {
      // 进入待机状态
      if (this.state.currentEmotion !== 'neutral') {
        console.log('进入待机状态')
        this.setEmotion('neutral', 1, false)
      }
    }, this.config.idleTimeout * 1000)
  }

  // 重置待机计时器
  private resetIdleTimer(): void {
    if (this.idleTimerRef) {
      clearTimeout(this.idleTimerRef)
    }
    this.startIdleTimer()
  }

  // 销毁控制器
  destroy(): void {
    if (this.idleTimerRef) {
      clearTimeout(this.idleTimerRef)
    }
    this.listeners = []
  }
}

// React Hook 版本
export function useEmotionMotionController(config?: Partial<EmotionMotionControllerConfig>) {
  const controllerRef = useRef<EmotionMotionController | null>(null)
  const [state, setState] = useState<EmotionState>({
    currentEmotion: 'neutral',
    currentIntensity: 1,
    targetEmotion: 'neutral',
    targetIntensity: 1,
    isTransitioning: false,
    lastUpdateTime: Date.now(),
    emotionHistory: [],
  })

  // 初始化控制器
  useEffect(() => {
    controllerRef.current = new EmotionMotionController(config)
    
    const unsubscribe = controllerRef.current.addListener(newState => {
      setState(newState)
    })
    
    setState(controllerRef.current.getState())
    
    return () => {
      unsubscribe()
      if (controllerRef.current) {
        controllerRef.current.destroy()
      }
    }
  }, [])

  // 更新配置
  useEffect(() => {
    if (controllerRef.current && config) {
      controllerRef.current.setConfig(config)
    }
  }, [config])

  // 设置情绪
  const setEmotion = useCallback((emotion: string, intensity?: number, immediate?: boolean) => {
    controllerRef.current?.setEmotion(emotion, intensity, immediate)
  }, [])

  // 获取当前表情
  const getCurrentExpression = useCallback(() => {
    return controllerRef.current?.getCurrentExpression() || 'neutral'
  }, [])

  // 获取当前动作
  const getCurrentMotion = useCallback(() => {
    return controllerRef.current?.getCurrentMotion() || 'idle'
  }, [])

  // 获取动作序列
  const getMotionSequence = useCallback((duration?: number) => {
    return controllerRef.current?.getMotionSequence(duration) || []
  }, [])

  // 获取微表情
  const getMicroExpressions = useCallback(() => {
    return controllerRef.current?.getMicroExpressions() || []
  }, [])

  // 获取待机动画
  const getIdleAnimation = useCallback(() => {
    return controllerRef.current?.getIdleAnimation() || []
  }, [])

  return {
    state,
    setEmotion,
    getCurrentExpression,
    getCurrentMotion,
    getMotionSequence,
    getMicroExpressions,
    getIdleAnimation,
  }
}
