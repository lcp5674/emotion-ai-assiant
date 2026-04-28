/**
 * 情绪驱动动画引擎
 * 提供基于情绪分析的自适应动画系统
 */

import { analyzeSentiment } from './sentimentAnalyzer'

// 情绪强度级别
export type EmotionIntensity = 'low' | 'medium' | 'high' | 'strong'

// 情绪状态接口
export interface EmotionState {
  expression: string
  motion: string
  intensity: number // 0-1
  label: string
  timestamp: number
}

// 表情映射
export const EXPRESSION_MAP: Record<string, string> = {
  neutral: 'f01',
  happy: 'f02',
  sad: 'f03',
  angry: 'f04',
  surprised: 'f03',
  smile: 'f02',
  excited: 'f02',
  thinking: 'f01',
  anxious: 'f03',
  fearful: 'f03',
  love: 'f02',
  grateful: 'f02',
  proud: 'f02',
  amused: 'f02',
  confused: 'f01',
  bored: 'f03',
  tired: 'f03',
  relieved: 'f02',
}

// 动作分组映射
export const MOTION_GROUP_MAP: Record<string, string> = {
  idle: 'Idle',
  happy: 'TapBody',
  excited: 'TapBody',
  sad: 'TapBody',
  cry: 'TapBody',
  angry: 'TapBody',
  surprised: 'TapBody',
  thinking: 'TapBody',
  anxious: 'TapBody',
  fearful: 'TapBody',
  love: 'TapBody',
  grateful: 'TapBody',
  wave: 'TapBody',
  clap: 'TapBody',
  jump: 'TapBody',
  nod: 'TapBody',
  shake_head: 'TapBody',
  speak: 'TapBody',
}

// 情绪分析结果
export interface EmotionResult {
  expression: string
  motion: string
  intensity: number
  confidence: number
  label: string
  source: 'api' | 'rule'
}

// 规则基础情绪分析
const EMOTION_DICT: Record<string, { score: number; category: string }> = {
  // 积极情绪
  '开心': { score: 0.9, category: 'happy' },
  '高兴': { score: 0.85, category: 'happy' },
  '快乐': { score: 0.85, category: 'happy' },
  '幸福': { score: 0.9, category: 'happy' },
  '兴奋': { score: 0.95, category: 'excited' },
  '激动': { score: 0.9, category: 'excited' },
  '棒': { score: 0.8, category: 'happy' },
  '完美': { score: 0.9, category: 'excited' },
  '喜欢': { score: 0.8, category: 'love' },
  '爱': { score: 0.9, category: 'love' },
  '感谢': { score: 0.7, category: 'grateful' },
  '谢谢': { score: 0.6, category: 'happy' },
  '哈哈': { score: 0.7, category: 'happy' },
  '太好了': { score: 0.9, category: 'excited' },
  '真棒': { score: 0.85, category: 'excited' },

  // 消极情绪
  '难过': { score: -0.8, category: 'sad' },
  '伤心': { score: -0.85, category: 'sad' },
  '悲伤': { score: -0.9, category: 'sad' },
  '痛苦': { score: -0.9, category: 'sad' },
  '难受': { score: -0.75, category: 'sad' },
  '失落': { score: -0.7, category: 'sad' },
  '沮丧': { score: -0.8, category: 'sad' },
  '绝望': { score: -0.95, category: 'sad' },
  '无奈': { score: -0.7, category: 'sad' },
  '郁闷': { score: -0.7, category: 'sad' },
  '烦恼': { score: -0.6, category: 'anxious' },
  '焦虑': { score: -0.6, category: 'anxious' },
  '担心': { score: -0.5, category: 'anxious' },
  '害怕': { score: -0.7, category: 'fearful' },
  '恐惧': { score: -0.8, category: 'fearful' },

  // 愤怒
  '生气': { score: -0.85, category: 'angry' },
  '愤怒': { score: -0.95, category: 'angry' },
  '恼火': { score: -0.85, category: 'angry' },
  '讨厌': { score: -0.7, category: 'angry' },
  '恨': { score: -0.9, category: 'angry' },
  '可恶': { score: -0.75, category: 'angry' },

  // 惊讶
  '惊讶': { score: 0.3, category: 'surprised' },
  '震惊': { score: 0.4, category: 'surprised' },
  '意外': { score: 0.2, category: 'surprised' },
  '哇': { score: 0.5, category: 'excited' },
  '厉害': { score: 0.5, category: 'surprised' },

  // 中性/思考
  '思考': { score: 0, category: 'thinking' },
  '想': { score: 0, category: 'thinking' },
  '觉得': { score: 0, category: 'thinking' },
}

// 程度词
const DEGREE_WORDS: Record<string, number> = {
  '非常': 1.5,
  '特别': 1.5,
  '极其': 1.8,
  '十分': 1.4,
  '很': 1.2,
  '挺': 1.1,
  '太': 1.5,
  '好': 1.3,
  '有点': 0.6,
  '稍微': 0.5,
  '略微': 0.5,
  '一点': 0.4,
}

// 否定词
const NEGATION_WORDS: string[] = ['不', '没', '不是', '不会', '不太', '没太', '并非', '一点都', '根本没', '哪有']

// 获取程度词影响
function getDegreeMultiplier(text: string, wordIdx: number): number {
  const beforeText = text.substring(0, wordIdx)
  let maxMul = 1.0
  for (const [word, mul] of Object.entries(DEGREE_WORDS)) {
    const idx = beforeText.lastIndexOf(word)
    if (idx !== -1 && wordIdx - idx < 6) {
      maxMul = Math.max(maxMul, mul)
    }
  }
  return maxMul
}

// 获取否定词影响
function getNegationMultiplier(text: string, wordIdx: number): number {
  const beforeText = text.substring(0, wordIdx)
  for (const neg of NEGATION_WORDS) {
    const idx = beforeText.lastIndexOf(neg)
    if (idx !== -1 && wordIdx - idx < 5) {
      return -1.0
    }
  }
  return 1.0
}

// 检测标点影响
function getPunctuationEffect(text: string): { intensity: number; isQuestion: boolean } {
  let intensity = 1.0
  const isQuestion = text.includes('？') || text.includes('?')

  const exclamationCount = (text.match(/！/g) || []).length
  if (exclamationCount >= 3) intensity = 1.5
  else if (exclamationCount >= 1) intensity = 1.2

  if (isQuestion && exclamationCount === 0) intensity = 0.8

  return { intensity, isQuestion }
}

// 规则基础情绪分析
function ruleBasedAnalysis(content: string): EmotionResult {
  const text = content.trim()

  let totalScore = 0
  let emotionCategory = 'neutral'
  let maxWeightedScore = 0
  let confidence = 0.3

  const { intensity: punctIntensity, isQuestion } = getPunctuationEffect(text)

  // 检测反问句
  const isRhetorical = /难道.*吗|不是.*吗|怎么.*呢|怎么会/.test(text)

  for (const [word, info] of Object.entries(EMOTION_DICT)) {
    const wordIdx = text.indexOf(word)
    if (wordIdx === -1) continue

    const degMul = getDegreeMultiplier(text, wordIdx)
    const negMul = getNegationMultiplier(text, wordIdx)
    let wordScore = info.score * degMul * negMul * punctIntensity

    if (isRhetorical) {
      wordScore *= -0.8
    }

    totalScore += wordScore

    if (Math.abs(wordScore) > Math.abs(maxWeightedScore)) {
      maxWeightedScore = wordScore
      emotionCategory = info.category
    }

    confidence = Math.min(0.95, confidence + 0.15)
  }

  // 纯否定句检测
  if (/不[好对是应该能想要]/.test(text) && totalScore === 0) {
    totalScore = -0.5
    emotionCategory = 'sad'
    confidence = 0.5
  }

  // 确定最终表情和动作
  let expression = 'neutral'
  let motion = 'idle'

  const CONFIDENCE_THRESHOLD = 0.35

  if (Math.abs(totalScore) > CONFIDENCE_THRESHOLD || confidence > CONFIDENCE_THRESHOLD) {
    if (totalScore > 0.3) {
      if (totalScore > 0.6) {
        expression = 'excited'
        motion = 'jump'
      } else if (totalScore > 0.4) {
        expression = 'happy'
        motion = 'clap'
      } else {
        expression = 'smile'
        motion = 'happy'
      }
    } else if (totalScore < -0.3) {
      switch (emotionCategory) {
        case 'angry':
          expression = 'angry'
          motion = 'shake_head'
          break
        case 'fearful':
          expression = 'surprised'
          motion = 'nod'
          break
        default:
          expression = 'sad'
          motion = totalScore < -0.5 ? 'cry' : 'slump'
      }
    } else if (isQuestion) {
      expression = 'thinking'
      motion = 'thinking'
    }
  }

  // 强度计算
  const intensity = Math.min(1.0, Math.abs(totalScore))

  return {
    expression,
    motion,
    intensity,
    confidence,
    label: emotionCategory,
    source: 'rule'
  }
}

// 分析文本情绪（主入口）
export async function analyzeEmotion(content: string): Promise<EmotionResult> {
  if (!content || !content.trim()) {
    return {
      expression: 'neutral',
      motion: 'idle',
      intensity: 0,
      confidence: 0,
      label: 'neutral',
      source: 'rule'
    }
  }

  try {
    // 优先使用API分析
    const apiResult = await analyzeSentiment(content)
    if (apiResult) {
      return {
        expression: apiResult.expression || 'neutral',
        motion: apiResult.motion || 'idle',
        intensity: apiResult.confidence || 0.5,
        confidence: apiResult.confidence || 0.5,
        label: apiResult.label || 'neutral',
        source: 'api'
      }
    }
  } catch (error) {
    console.warn('API情绪分析失败，使用规则匹配:', error)
  }

  // 回退到规则基础分析
  return ruleBasedAnalysis(content)
}

// 获取情绪对应的CSS动画类名
export function getEmotionAnimationClass(motion: string): string {
  switch (motion) {
    case 'happy':
    case 'excited':
      return 'emotion-excited'
    case 'clap':
      return 'emotion-clap'
    case 'jump':
      return 'emotion-jump'
    case 'wave':
      return 'emotion-wave'
    case 'nod':
      return 'emotion-nod'
    case 'sad':
    case 'cry':
    case 'slump':
      return 'emotion-sad'
    case 'angry':
    case 'shake_head':
    case 'frustrated':
      return 'emotion-angry'
    case 'thinking':
    case 'touch_chin':
    case 'curious':
      return 'emotion-thinking'
    case 'speak':
      return 'emotion-speak'
    default:
      return 'emotion-idle'
  }
}

// 情绪强度到动作时间的映射
export function getMotionDuration(intensity: number, motion: string): number {
  if (motion === 'idle') return 0

  // 高强度情绪动作持续更长时间
  const baseDuration = 1500 // 1.5秒基础
  const intensityMultiplier = 0.5 + (intensity * 0.5) // 0.5-1.0

  if (motion === 'jump' || motion === 'cry') {
    return baseDuration * intensityMultiplier * 1.5 // 情绪动作延长
  }

  return baseDuration * intensityMultiplier
}
