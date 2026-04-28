import { useEffect, useState, useRef, useCallback, memo } from 'react'
import { useNavigate, useParams, Link, useSearchParams, useLocation } from 'react-router-dom'
import { Input, Button, List, Spin, Empty, Drawer, App, Avatar, Tag, Modal, Select, Dropdown } from 'antd'
import { SendOutlined, ArrowLeftOutlined, UserOutlined, MenuOutlined, DeleteOutlined, ReloadOutlined, HeartOutlined, TeamOutlined, BookOutlined, SmileOutlined, RocketOutlined, StarOutlined, AppstoreOutlined, SwapOutlined, SettingOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../api/request'
import { useAuthStore, useChatStore } from '../stores'
import { useIsMobile } from '../hooks/useIsMobile'
import { useTheme } from '../hooks/useTheme'
import { Live2DCanvas } from '../components/avatar'
import { startBackgroundPreload, preloadModelsInBackground } from '../components/avatar/live2dPreloader'
import { analyzeEmotion, getEmotionAnimationClass } from '../components/avatar/emotionEngine'
import { analyzeSentiment, warmupModel, isModelLoaded } from '../components/avatar/sentimentAnalyzer'
import '../components/avatar/Live2DCanvas.css'

// MBTI 类型到 Live2D 模型的映射 - 使用兼容的模型
const MBTI_MODEL_MAP: Record<string, string> = {
  'INFP': '/live2d/all/shizuku/shizuku.model.json',
  'INFJ': '/live2d/all/shizuku/shizuku.model.json',
  'INTP': '/live2d/all/shizuku/shizuku.model.json',
  'INTJ': '/live2d/all/shizuku/shizuku.model.json',
  'ISFP': '/live2d/all/rem/model.json',
  'ISFJ': '/live2d/all/rem/model.json',
  'ISTP': '/live2d/all/chino/model.json',
  'ISTJ': '/live2d/all/chino/model.json',
  'ENFP': '/live2d/all/umaru/model.json',
  'ENFJ': '/live2d/all/umaru/model.json',
  'ENTP': '/live2d/all/shizuku/shizuku.model.json',
  'ENTJ': '/live2d/all/shizuku/shizuku.model.json',
  'ESFP': '/live2d/all/rem/model.json',
  'ESFJ': '/live2d/all/umaru/model.json',
  'ESTP': '/live2d/all/HK416-1-normal/model.json',
  'ESTJ': '/live2d/all/chino/model.json',
}

// 默认模型
const DEFAULT_MODEL = '/live2d/all/shizuku/shizuku.model.json'

// 可选的 Live2D 模型列表 - 已经过验证可用的模型
// 只保留已知能正常加载的模型，避免加载失败影响用户体验
export const LIVE2D_MODELS = [
  { name: 'Shizuku', path: '/live2d/all/shizuku/shizuku.model.json', description: '文静的少女' },
  { name: 'Rem', path: '/live2d/all/rem/model.json', description: '鬼族少女' },
  { name: 'Umaru', path: '/live2d/all/umaru/model.json', description: '家里蹲女孩' },
  { name: 'HK416', path: '/live2d/all/HK416-1-normal/model.json', description: '军装少女' },
  { name: 'Chino', path: '/live2d/all/chino/model.json', description: '咖啡店少女' },
  { name: 'Hibiki', path: '/live2d/all/hibiki/hibiki.model.json', description: '音乐少女' },
  { name: 'Mai', path: '/live2d/all/mai/model.json', description: '运动的少女' },
  { name: 'Pio', path: '/live2d/all/Pio/model.json', description: '可爱女孩' },
  { name: 'Tia', path: '/live2d/all/tia/model.json', description: '龙族少女' },
  { name: 'Z16', path: '/live2d/all/z16/z16.model.json', description: '机械少女' },
  { name: 'Koharu', path: '/live2d/all/koharu/model.json', description: '可爱少女' },
  { name: 'Murakumo', path: '/live2d/all/murakumo/model.json', description: '舰娘' },
  { name: 'Hallo', path: '/live2d/all/hallo/model.json', description: '万圣少女' },
  { name: 'Histoire', path: '/live2d/all/histoire/model.json', description: '历史老师' },
  { name: 'Terisa', path: '/live2d/all/terisa/model.json', description: '魔法少女' },
  { name: 'Kate', path: '/live2d/all/cat-white/model.json', description: '白猫' },
  { name: 'Kuro', path: '/live2d/all/cat-black/model.json', description: '黑猫' },
  { name: 'LiveUu', path: '/live2d/all/live_uu/model.json', description: '虚拟主播' },
  { name: 'Xisitina', path: '/live2d/all/xisitina/model.json', description: 'xisi少女' },
  { name: 'Date', path: '/live2d/all/date/model.json', description: '约会少女' },
  { name: 'KP31', path: '/live2d/all/kp31/model.json', description: '机枪兵' },
  { name: 'Platelet', path: '/live2d/all/platelet/model.json', description: '血小板' },
  { name: 'Platelet2', path: '/live2d/all/platelet_2/model.json', description: '血小板2' },
]

// 获取助手对应的 Live2D 模型路径
const getLive2DModelPath = (assistant: any, userSelectedModel?: string | null): string => {
  // 优先使用用户选择的模型
  if (userSelectedModel) {
    return userSelectedModel
  }

  if (!assistant) return DEFAULT_MODEL

  // 优先使用助手自定义配置的模型
  if (assistant.avatar_info?.live2d_model_url) {
    return assistant.avatar_info.live2d_model_url
  }

  // 根据 MBTI 类型选择
  if (assistant.mbti_type && MBTI_MODEL_MAP[assistant.mbti_type]) {
    return MBTI_MODEL_MAP[assistant.mbti_type]
  }

  // 默认回退
  return DEFAULT_MODEL
}

const { TextArea } = Input

// Markdown渲染组件
const MarkdownContent = memo(({ content }: { content: string }) => (
  <ReactMarkdown remarkPlugins={[remarkGfm]}>
    {content}
  </ReactMarkdown>
))

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

// 气泡颜色配置
const BUBBLE_COLORS = {
  user: { gradient: ['#722ed1', '#eb2f96'], text: '#ffffff' },
  assistant: { gradient: ['#f5f5f5', '#ffffff'], text: '#262626', dark: ['#2d2d2d', '#262626'], darkText: 'rgba(255,255,255,0.95)' },
}

export default function Chat() {
  const navigate = useNavigate()
  const location = useLocation()
  const { message: antMessage } = App.useApp()
  const { sessionId } = useParams()
  const [searchParams] = useSearchParams()
  const { user } = useAuthStore()
  const { messages, setMessages, addMessage, loading, setLoading, conversations, setConversations } = useChatStore()
  const { theme, themeColors, themeColor } = useTheme()
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
  const [showAvatarControls, setShowAvatarControls] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(280) // 对话历史列表宽度 px
  const [avatarWidth, setAvatarWidth] = useState(350) // 虚拟形象展示区域宽度 px
  const [isDragging, setIsDragging] = useState<'sidebar' | 'avatar' | null>(null)
  const dragStartXRef = useRef<number>(0)
  const dragStartWidthsRef = useRef({ sidebar: 280, avatar: 350 })
  const streamingMessageRef = useRef('') // 用于WebSocket闭包中跟踪streamingMessage

  // 动画状态
  const [avatarExpression, setAvatarExpression] = useState('neutral')
  const [avatarMotion, setAvatarMotion] = useState('idle')
  const [avatarIsSpeaking, setAvatarIsSpeaking] = useState(false)
  const [selectedLive2DModel, setSelectedLive2DModel] = useState<string | null>(null)

  const themeGradient = themeColors[themeColor]
  const isMobile = useIsMobile()

  useEffect(() => {
    startBackgroundPreload()
  }, [])

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

        if (!mbtiCompleted || !sbtiCompleted || !attachmentCompleted) {
          antMessage.warning('请先完成三位一体测评后再使用聊天功能')
          navigate('/comprehensive')
        }
      } catch (error) {
        console.error('检查测评状态失败:', error)
        antMessage.error('检查测评状态失败')
        navigate('/comprehensive')
      }
    }
    checkAssessments()
  }, [navigate, antMessage])

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

  const loadAllConversations = async () => {
    try {
      const res = await api.chat.conversations()
      setConversations(res.list || [])
    } catch (error) {
      console.error(error)
    }
  }

  const loadConversationsByAssistant = async (assistantId: number) => {
    try {
      const res = await api.chat.conversations()
      const assistantConversations = (res.list || []).filter((c: any) => c.assistant_id === assistantId)
      setConversations(assistantConversations)
      if (assistantConversations.length > 0) {
        const latestSession = assistantConversations[0]
        setCurrentSessionId(latestSession.session_id)
        loadHistory(latestSession.session_id)
      } else {
        setCurrentSessionId(undefined)
        setMessages([])
      }
    } catch (error) {
      console.error(error)
    }
  }

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
    { icon: <HeartOutlined />, label: '倾诉心情', prompt: '今天我有一些心情想和你分享...', color: '#ec4899' },
    { icon: <TeamOutlined />, label: '人际关系', prompt: '我想聊聊关于人际关系的问题...', color: '#6366f1' },
    { icon: <BookOutlined />, label: '自我成长', prompt: '我想聊一聊关于个人成长的话题...', color: '#10b981' },
    { icon: <SmileOutlined />, label: '日常分享', prompt: '今天发生了一件小事...', color: '#f59e0b' },
    { icon: <RocketOutlined />, label: '职业发展', prompt: '我想聊聊职业发展的问题...', color: '#8b5cf6' },
  ]

  // ============================================
  // 智能情绪分析系统
  // ============================================

  // 情感词典：词 -> {分数, 类别, 强度}
  // 分数范围: -1(最消极) ~ 0(中性) ~ 1(最积极)
  // 类别: positive, negative, angry, surprised, fearful, sad
  const EMOTION_DICT = {
    // 积极情绪词
    '开心': { score: 0.9, category: 'positive' },
    '高兴': { score: 0.85, category: 'positive' },
    '快乐': { score: 0.85, category: 'positive' },
    '愉快': { score: 0.8, category: 'positive' },
    '幸福': { score: 0.9, category: 'positive' },
    '满足': { score: 0.7, category: 'positive' },
    '兴奋': { score: 0.95, category: 'positive' },
    '激动': { score: 0.9, category: 'positive' },
    '棒': { score: 0.8, category: 'positive' },
    '赞': { score: 0.75, category: 'positive' },
    '完美': { score: 0.9, category: 'positive' },
    '喜欢': { score: 0.8, category: 'positive' },
    '爱': { score: 0.9, category: 'positive' },
    '感谢': { score: 0.7, category: 'positive' },
    '谢谢': { score: 0.6, category: 'positive' },
    '哈哈': { score: 0.7, category: 'positive' },
    '嘻嘻': { score: 0.65, category: 'positive' },
    '嘿嘿': { score: 0.65, category: 'positive' },
    '得意': { score: 0.6, category: 'positive' },
    '太好了': { score: 0.9, category: 'positive' },
    '真好': { score: 0.8, category: 'positive' },
    '不错': { score: 0.5, category: 'positive' },
    '好': { score: 0.5, category: 'positive' },

    // 消极情绪词
    '难过': { score: -0.8, category: 'sad' },
    '伤心': { score: -0.85, category: 'sad' },
    '悲伤': { score: -0.9, category: 'sad' },
    '痛苦': { score: -0.9, category: 'sad' },
    '难受': { score: -0.75, category: 'sad' },
    '不爽': { score: -0.5, category: 'sad' },
    '不好': { score: -0.6, category: 'sad' },
    '失落': { score: -0.7, category: 'sad' },
    '沮丧': { score: -0.8, category: 'sad' },
    '绝望': { score: -0.95, category: 'sad' },
    '无奈': { score: -0.7, category: 'sad' },
    '郁闷': { score: -0.7, category: 'sad' },
    '烦恼': { score: -0.6, category: 'sad' },
    '烦': { score: -0.5, category: 'sad' },
    '累': { score: -0.4, category: 'sad' },
    '疲惫': { score: -0.5, category: 'sad' },
    '哭': { score: -0.8, category: 'sad' },
    '流泪': { score: -0.7, category: 'sad' },

    // 愤怒情绪词
    '生气': { score: -0.85, category: 'angry' },
    '愤怒': { score: -0.95, category: 'angry' },
    '恼火': { score: -0.85, category: 'angry' },
    '讨厌': { score: -0.7, category: 'angry' },
    '恨': { score: -0.9, category: 'angry' },
    '可恶': { score: -0.75, category: 'angry' },
    '过分': { score: -0.7, category: 'angry' },
    '火大': { score: -0.9, category: 'angry' },
    '气': { score: -0.6, category: 'angry' },

    // 惊讶情绪词
    '惊讶': { score: 0.3, category: 'surprised' },
    '震惊': { score: 0.4, category: 'surprised' },
    '意外': { score: 0.2, category: 'surprised' },
    '哇': { score: 0.5, category: 'surprised' },
    '天哪': { score: 0.4, category: 'surprised' },
    '不会吧': { score: 0.2, category: 'surprised' },
    '厉害': { score: 0.5, category: 'surprised' },
    '哇塞': { score: 0.5, category: 'surprised' },

    // 恐惧情绪词
    '害怕': { score: -0.7, category: 'fearful' },
    '恐惧': { score: -0.8, category: 'fearful' },
    '担心': { score: -0.5, category: 'fearful' },
    '紧张': { score: -0.4, category: 'fearful' },
    '焦虑': { score: -0.6, category: 'fearful' },
  }

  // 否定词及反转强度
  const NEGATION_WORDS = [
    { word: '不', strength: -1.0 },
    { word: '没', strength: -0.8 },
    { word: '不是', strength: -1.0 },
    { word: '不会', strength: -0.9 },
    { word: '不太', strength: -0.5 },
    { word: '没太', strength: -0.4 },
    { word: '并非', strength: -1.0 },
    { word: '并非', strength: -1.0 },
    { word: '一点都', strength: -1.0 },
    { word: '根本没', strength: -1.0 },
    { word: '哪有', strength: -0.7 },
  ]

  // 程度词及增强系数
  const DEGREE_WORDS = [
    { word: '非常', multiplier: 1.5 },
    { word: '特别', multiplier: 1.5 },
    { word: '极其', multiplier: 1.8 },
    { word: '十分', multiplier: 1.4 },
    { word: '很', multiplier: 1.2 },
    { word: '挺', multiplier: 1.1 },
    { word: '太', multiplier: 1.5 },
    { word: '好', multiplier: 1.3 },
    { word: '有点', multiplier: 0.6 },
    { word: '有点', multiplier: 0.6 },
    { word: '稍微', multiplier: 0.5 },
    { word: '略微', multiplier: 0.5 },
    { word: '一点', multiplier: 0.4 },
    { word: '有点', multiplier: 0.6 },
  ]

  // 分析否定词对文本的影响范围
  const getNegationEffect = (text: string, emotionWord: string): number => {
    const emotionIndex = text.indexOf(emotionWord)
    if (emotionIndex === -1) return 1.0

    // 在情感词前面查找否定词
    const beforeText = text.substring(0, emotionIndex)

    // 查找最近的否定词
    let minDistance = Infinity
    let negationStrength = 1.0

    for (const neg of NEGATION_WORDS) {
      const negIndex = beforeText.lastIndexOf(neg.word)
      if (negIndex !== -1) {
        const distance = emotionIndex - negIndex
        if (distance < minDistance && distance < 6) { // 否定词在情感词前5个字符内
          minDistance = distance
          negationStrength = neg.strength
        }
      }
    }

    return negationStrength
  }

  // 获取程度词增强系数
  const getDegreeEffect = (text: string, emotionWord: string): number => {
    const emotionIndex = text.indexOf(emotionWord)
    if (emotionIndex === -1) return 1.0

    const beforeText = text.substring(0, emotionIndex)

    let maxMultiplier = 1.0
    for (const deg of DEGREE_WORDS) {
      const degIndex = beforeText.lastIndexOf(deg.word)
      if (degIndex !== -1) {
        const distance = emotionIndex - degIndex
        if (distance < 6 && deg.multiplier > maxMultiplier) {
          maxMultiplier = deg.multiplier
        }
      }
    }

    return maxMultiplier
  }

  // 检测标点符号影响
  const getPunctuationEffect = (text: string): { intensity: number; isQuestion: boolean } => {
    let intensity = 1.0
    const isQuestion = text.includes('？') || text.includes('?')

    // 感叹号增强
    const exclamationCount = (text.match(/！/g) || []).length
    if (exclamationCount >= 3) intensity = 1.5
    else if (exclamationCount >= 1) intensity = 1.2

    // 问号降低（疑问句通常情绪较弱）
    if (isQuestion && exclamationCount === 0) intensity = 0.8

    // 省略号可能表示情绪延续或减弱
    if (text.includes('...') || text.includes('。。。')) {
      intensity *= 0.9
    }

    return { intensity, isQuestion }
  }

  // 检测反问句（情感反转）
  const isRhetoricalQuestion = (text: string): boolean => {
    // 反问句模式："难道...吗？"、"不是...吗？"
    const rhetoricalPatterns = [
      /难道.*吗/,
      /不是.*吗/,
      /怎么.*呢/,
      /怎么会/,
      /不是.*吧/
    ]
    return rhetoricalPatterns.some(p => p.test(text))
  }

  // 核心情绪分析函数
  const analyzeEmotion = (content: string): { expression: string; motion: string; confidence: number } => {
    const text = content.trim()

    // 计算每个情感词的影响
    let totalScore = 0
    let emotionCategory = 'neutral'
    let maxWeightedScore = 0
    let confidence = 0.3 // 基础置信度

    // 检测反问句（反转情绪）
    const isRhetorical = isRhetoricalQuestion(text)

    // 获取标点影响
    const punctEffect = getPunctuationEffect(text)

    // 遍历情感词典
    for (const [word, info] of Object.entries(EMOTION_DICT)) {
      if (text.includes(word)) {
        // 获取否定词影响
        const negEffect = getNegationEffect(text, word)
        // 获取程度词影响
        const degEffect = getDegreeEffect(text, word)

        // 计算加权分数
        let wordScore = info.score * degEffect * negEffect * punctEffect.intensity

        // 反问句反转情绪
        if (isRhetorical) {
          wordScore *= -0.8
        }

        totalScore += wordScore

        // 追踪主要情绪类别（取绝对值最大的）
        if (Math.abs(wordScore) > Math.abs(maxWeightedScore)) {
          maxWeightedScore = wordScore
          emotionCategory = info.category
        }

        // 增加置信度
        confidence = Math.min(0.95, confidence + 0.15)
      }
    }

    // 纯否定句检测（如"不好"、"不对"）
    const pureNegation = /不[好对是应该能想要]/g.test(text) && totalScore === 0
    if (pureNegation) {
      totalScore = -0.5
      emotionCategory = 'sad'
      confidence = 0.5
    }

    // 置信度阈值
    const CONFIDENCE_THRESHOLD = 0.35

    // ===== 增强版：根据分数和类别确定最终情绪 =====
    let expression = 'neutral'
    let motion = 'idle'

    // 只有在有明确情感词或置信度足够时才应用情绪
    if (Math.abs(totalScore) > CONFIDENCE_THRESHOLD || confidence > CONFIDENCE_THRESHOLD) {
      if (totalScore > 0.2) {
        // 积极情绪 - 使用更明显的动作
        if (totalScore > 0.6) {
          expression = 'excited'
          motion = 'jump'  // 更强烈的动作
        } else if (totalScore > 0.4) {
          expression = 'happy'
          motion = 'clap'  // 拍手
        } else {
          expression = 'smile'
          motion = 'happy'
        }
      } else if (totalScore < -0.2) {
        switch (emotionCategory) {
          case 'angry':
            expression = 'angry'
            motion = 'shake_head'  // 摇头表示生气，更明显
            break
          case 'fearful':
            expression = 'surprised'
            motion = 'tremble'  // 颤抖
            break
          case 'sad':
          default:
            expression = 'sad'
            motion = totalScore < -0.5 ? 'cry' : 'slump'  // 哭泣或垂头丧气
        }
      } else if (punctEffect.isQuestion && totalScore > -0.1) {
        expression = 'thinking'
        motion = 'touch_chin'  // 摸下巴思考
      }
    }

    // 如果置信度很低，使用中性
    if (confidence < CONFIDENCE_THRESHOLD && Math.abs(totalScore) < 0.2) {
      expression = 'smile'
      motion = 'idle'
    }

    console.log('🎯 情绪分析结果:', { totalScore, emotionCategory, expression, motion, confidence })
    return { expression, motion, confidence }
  }

  // 强调词检测：根据标点符号调整情绪强度
  const detectEmphasis = (content: string): { isStrong: boolean; isQuestion: boolean } => {
    return {
      isStrong: content.includes('!') || content.includes('！') || content.includes('!!!') || content.includes('!!'),
      isQuestion: content.includes('?') || content.includes('？') || content.includes('??')
    }
  }

  // ===== 增强版：应用情绪到模型 =====
  const applyEmotion = (emotion: { expression: string; motion: string }, isStrong: boolean = false) => {
    console.log('🎭 应用情绪到模型:', emotion, 'isStrong:', isStrong)
    
    // 设置表情和动作
    setAvatarExpression(emotion.expression)
    setAvatarMotion(emotion.motion)
    
    // 不自动重置，让用户情绪保持直到下一条消息或WebSocket更新
  }

  const triggerAnimation = (expression: string, motion: string) => {
    setAvatarExpression(expression)
    setAvatarMotion(motion)
  }

  const handleQuickReply = (prompt: string) => {
    setInputValue(prompt)
    setShowQuickReplies(false)
    handleSend()
  }

const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const lastEmotionKey = useRef<string>('')

  // 分隔栏拖动处理
  const handleDragStart = (e: React.MouseEvent, target: 'sidebar' | 'avatar') => {
    e.preventDefault()
    setIsDragging(target)
    dragStartXRef.current = e.clientX
    dragStartWidthsRef.current = { sidebar: sidebarWidth, avatar: avatarWidth }
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  const handleDrag = (e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return

    const container = containerRef.current
    const containerRect = container.getBoundingClientRect()
    const containerWidth = containerRect.width

    const deltaX = e.clientX - dragStartXRef.current

    if (isDragging === 'sidebar') {
      // 调整对话历史列表宽度
      let newWidth = dragStartWidthsRef.current.sidebar + deltaX
      newWidth = Math.max(180, Math.min(400, newWidth))
      setSidebarWidth(newWidth)
    } else if (isDragging === 'avatar') {
      // 调整虚拟形象展示区域宽度
      let newWidth = dragStartWidthsRef.current.avatar + deltaX
      newWidth = Math.max(200, Math.min(containerWidth * 0.5, newWidth))
      setAvatarWidth(newWidth)
    }
  }

  const handleDragEnd = () => {
    setIsDragging(null)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  // 添加全局鼠标事件监听
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDrag)
      document.addEventListener('mouseup', handleDragEnd)
    }
    return () => {
      document.removeEventListener('mousemove', handleDrag)
      document.removeEventListener('mouseup', handleDragEnd)
    }
  }, [isDragging])

  // WebSocket清理 - 组件卸载时关闭连接
  useEffect(() => {
    const cleanup = () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
    return cleanup
  }, [])

  useEffect(() => {
    if (sessionId) {
      setCurrentSessionId(sessionId)
      loadHistory(sessionId)
    }
    loadAllConversations()
  }, [sessionId])

  // 预热情绪分析模型
  useEffect(() => {
    warmupModel().catch(console.warn)
  }, [])

  useEffect(() => {
    const assistantId = searchParams.get('assistant_id')
    if (assistantId) {
      const id = parseInt(assistantId, 10)
      api.mbti.assistantDetail(id).then((res: any) => {
        setCurrentAssistant(res)
      }).catch(console.error)
      setMessages([])
      setStreamingMessage('')
      streamingMessageRef.current = '' // 同步ref
      closeWebSocket()
    }
  }, [searchParams])

  // 处理从推荐助手跳转过来的助手信息
  useEffect(() => {
    const state = location.state as any
    if (state?.assistantId) {
      // 根据助手 ID 获取助手信息
      const assistantInfo = {
        id: state.assistantId,
        name: state.assistant || '',
        emoji: state.assistantEmoji || '💕',
      }
      setCurrentAssistant(assistantInfo)
      setMessages([])
      setStreamingMessage('')
      streamingMessageRef.current = ''
      closeWebSocket()
      // 清除 state，避免刷新时重复加载
      navigate(location.pathname, { replace: true })
    }
  }, [location.state])

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

  // 处理发送消息（支持 AI 情绪分析）
  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || sending) return

    const content = inputValue.trim()
    setInputValue('')
    setSending(true)
    setStreamingMessage('')
    streamingMessageRef.current = '' // 同步ref

    // ===== 情绪同步：用户发送消息 =====
    // 使用 AI 模型分析情绪（带回退）
    let userEmotion = null
    try {
      userEmotion = await analyzeSentiment(content)
    } catch (error) {
      console.warn('AI情绪分析失败，使用规则匹配:', error)
      userEmotion = analyzeEmotion(content)
    }

    const emphasis = detectEmphasis(content)
    console.log('🎨 用户情绪分析结果:', userEmotion, emphasis)

    // ===== 增强版：更明显的情绪变化 =====
    if (userEmotion && userEmotion.expression) {
      // 始终应用用户情绪，哪怕是smile，也要让变化更明显
      console.log('🌈 应用用户情绪:', userEmotion)
      applyEmotion(userEmotion, emphasis.isStrong)
    }

    const userTempId = Date.now()
    addMessage({
      id: userTempId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    } as any)

    const assistantId = currentAssistant?.id
    const wsUrl = api.websocket.connect(currentSessionId, assistantId)
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    const assistantTempId = userTempId + 1
    setTempMessageId(assistantTempId)

    ws.onopen = () => {
      ws.send(JSON.stringify({
        content,
        session_id: currentSessionId || null,
        assistant_id: assistantId || null,
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'conversation_created' && data.session_id) {
          setCurrentSessionId(data.session_id)
          loadAllConversations()
        } else if (data.type === 'message_sent' && data.emotion) {
          const { expression, motion } = data.emotion

          const currentEmotionKey = `${expression}-${motion}`
          if (currentEmotionKey !== lastEmotionKey.current) {
            lastEmotionKey.current = currentEmotionKey

            setAvatarExpression(expression || 'neutral')
            setAvatarMotion(motion || 'idle')
          }
        } else if (data.type === 'start') {
          if (!currentSessionId && data.session_id) {
            setCurrentSessionId(data.session_id)
            navigate(`/chat/${data.session_id}`, { replace: true })
          }
          setAvatarIsSpeaking(true)
          setAvatarExpression('thinking')
        } else if (data.type === 'chunk') {
          setStreamingMessage(prev => prev + data.content)
          streamingMessageRef.current += data.content // 同步ref用于闭包

          if (data.emotion) {
            const { expression, motion, intensity } = data.emotion
            
            const currentEmotionKey = `${expression}-${motion}`
            
            if (currentEmotionKey !== lastEmotionKey.current) {
              lastEmotionKey.current = currentEmotionKey

              setAvatarExpression(expression || 'neutral')
              setAvatarMotion(motion || 'idle')
            }
          }
        } else if (data.type === 'done') {
          setSending(false)
          setStreamingMessage('')
          setTempMessageId(null)
          setAvatarIsSpeaking(false)

          const fullMessage = data.content || streamingMessageRef.current // 使用ref避免闭包问题
          
          if (fullMessage) {
            addMessage({
              id: data.message_id || assistantTempId,
              role: 'assistant',
              content: fullMessage,
              created_at: new Date().toISOString(),
              message_type: 'text',
              is_collected: false,
            } as Message)
          }

          console.log('🤖 AI回复完成:', fullMessage?.substring(0, 50))

          closeWebSocket()
          loadConversations()
        } else if (data.type === 'error') {
          // 先重置发送状态，防止按钮一直旋转
          setSending(false)
          setStreamingMessage('')
          streamingMessageRef.current = '' // 同步ref
          setTempMessageId(null)
          setAvatarIsSpeaking(false)
          
          antMessage.error(data.detail || '发送失败')

          // ===== 动画同步：出错时 =====
          setAvatarMotion('idle')
          setAvatarExpression('sad')

          // 2秒后恢复
          setTimeout(() => {
            setAvatarExpression('neutral')
          }, 2000)

          closeWebSocket()
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      antMessage.error('连接失败，请重试')
      setSending(false)
      setStreamingMessage('')
      streamingMessageRef.current = '' // 同步ref
      setTempMessageId(null)

      // ===== 动画同步：连接错误 =====
      setAvatarIsSpeaking(false)
      setAvatarMotion('idle')
      setAvatarExpression('sad')

      closeWebSocket()
    }

     ws.onclose = () => {
       if (sending) {
         setSending(false)
         setStreamingMessage('')
         streamingMessageRef.current = '' // 同步ref
         setTempMessageId(null)
       }
       wsRef.current = null
     }
  }, [inputValue, currentSessionId, sending, addMessage, navigate, antMessage, currentAssistant])

  const handleRegenerate = () => {
    if (sending || messages.length === 0) return
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user')
    if (!lastUserMessage) return
    setInputValue(lastUserMessage.content)
    const newMessages = messages.slice(0, -1)
    setMessages(newMessages)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const colors = {
    chatBg: isDark ? '#0f0f0f' : '#f8fafc',
    sidebarBg: isDark ? '#1a1a1a' : '#ffffff',
    headerBg: isDark ? '#1a1a1a' : '#ffffff',
    headerBorder: isDark ? '#2d2d2d' : '#f0f0f0',
    inputBg: isDark ? '#262626' : '#ffffff',
    inputText: isDark ? '#ffffff' : '#262626',
    bubbleBg: isDark ? '#262626' : '#ffffff',
    bubbleText: isDark ? 'rgba(255, 255, 255, 0.95)' : '#262626',
    borderColor: isDark ? '#333333' : '#e5e7eb',
    timeColor: isDark ? 'rgba(255,255,255,0.4)' : '#9ca3af',
    nameColor: isDark ? 'rgba(255,255,255,0.6)' : '#6b7280',
  }

  const handleConversationClick = async (session: any) => {
    if (session.assistant_id) {
      try {
        const res = await api.mbti.assistantDetail(session.assistant_id)
        setCurrentAssistant(res)
      } catch (error) {
        console.error(error)
      }
    }
    navigate(`/chat/${session.session_id}`)
    setSidebarOpen(false)
  }

  const handleDeleteConversation = async (session: any, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await api.chat.delete(session.session_id)
      antMessage.success('对话已删除')
      if (currentSessionId === session.session_id) {
        setMessages([])
        setCurrentSessionId(undefined)
      }
      loadConversations()
    } catch (error) {
      console.error(error)
      antMessage.error('删除失败')
    }
  }

  const sidebarContent = (
    <>
      <div style={{ padding: 20, borderBottom: `1px solid ${colors.borderColor}` }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          type="text"
          style={{
            color: isDark ? 'rgba(255,255,255,0.7)' : '#6b7280',
            borderRadius: 12,
          }}
        >
          返回
        </Button>
        <div style={{
          marginTop: 20,
          padding: '12px 16px',
          background: `linear-gradient(135deg, ${themeGradient}10 0%, ${themeGradient}05 100%)`,
          borderRadius: 16,
          border: `1px solid ${themeGradient}20`,
        }}>
          <div style={{ fontSize: 12, color: themeGradient, fontWeight: 600, marginBottom: 4 }}>
            当前助手
          </div>
          {currentAssistant ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Avatar
                src={currentAssistant.avatar}
                size={40}
                style={{
                  background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                }}
              >
                {currentAssistant.name?.[0]}
              </Avatar>
              <div>
                <div style={{ fontWeight: 600, color: isDark ? '#fff' : '#1f2937' }}>
                  {currentAssistant.name}
                </div>
                {currentAssistant.mbti_type && (
                  <Tag
                    color={themeGradient}
                    style={{ marginTop: 4, borderRadius: 8, fontSize: 11 }}
                  >
                    {currentAssistant.mbti_type}
                  </Tag>
                )}
              </div>
            </div>
          ) : (
            <Link to="/assistants">
              <Button
                type="primary"
                block
                style={{
                  background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                  border: 'none',
                  borderRadius: 12,
                }}
              >
                选择助手
              </Button>
            </Link>
          )}
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '8px 0' }}>
        <div style={{
          padding: '8px 20px',
          fontSize: 12,
          color: colors.nameColor,
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: 1,
        }}>
          对话历史
        </div>
        {conversations.length === 0 ? (
          <Empty
            description="暂无对话"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ marginTop: 40 }}
          />
        ) : (
          <List
            dataSource={conversations}
            renderItem={(item: any) => (
              <List.Item
                onClick={() => handleConversationClick(item)}
                style={{
                  cursor: 'pointer',
                  padding: '12px 20px',
                  background: currentSessionId === item.session_id
                    ? `linear-gradient(90deg, ${themeGradient}15 0%, transparent 100%)`
                    : 'transparent',
                  borderLeft: currentSessionId === item.session_id
                    ? `3px solid ${themeGradient}`
                    : '3px solid transparent',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (currentSessionId !== item.session_id) {
                    (e.currentTarget as HTMLElement).style.background = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (currentSessionId !== item.session_id) {
                    (e.currentTarget as HTMLElement).style.background = 'transparent'
                  }
                }}
                extra={
                  <Button
                    type="text"
                    icon={<DeleteOutlined />}
                    onClick={(e) => handleDeleteConversation(item, e as any)}
                    style={{ color: colors.nameColor, opacity: 0.6 }}
                    size="small"
                  />
                }
              >
                <List.Item.Meta
                  avatar={
                    item.assistant_avatar ? (
                      <Avatar src={item.assistant_avatar} size={40}
                        style={{ background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)` }}
                      />
                    ) : (
                      <Avatar size={40}
                        style={{ background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)` }}>
                        {item.assistant_name?.[0] || '助'}
                      </Avatar>
                    )
                  }
                  title={
                    <span style={{ color: isDark ? '#fff' : '#1f2937', fontWeight: 500 }}>
                      {item.title || '新对话'}
                    </span>
                  }
                  description={
                    <div style={{ fontSize: 12, color: colors.nameColor }}>
                      <span>{item.assistant_name || '未知助手'}</span>
                      <span style={{ margin: '0 8px' }}>·</span>
                      <span>{item.message_count} 条消息</span>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>
    </>
  )

  const chatHeader = (
    <div style={{
      padding: '16px 20px',
      background: colors.headerBg,
      borderBottom: `1px solid ${colors.borderColor}`,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      backdropFilter: 'blur(20px)',
    }}>
      {isMobile && (
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={() => setSidebarOpen(true)}
          style={{ color: isDark ? '#fff' : '#1f2937' }}
        />
      )}

      {currentAssistant ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: '14px',
            background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 4px 15px ${themeGradient}30`,
          }}>
            {currentAssistant.avatar ? (
              <Avatar src={currentAssistant.avatar} size={40} style={{ borderRadius: 12 }} />
            ) : (
              <span style={{ color: '#fff', fontSize: 18, fontWeight: 700 }}>
                {currentAssistant.name?.[0]}
              </span>
            )}
          </div>
          <div>
            <div style={{ fontWeight: 600, color: isDark ? '#fff' : '#1f2937', fontSize: 16 }}>
              {currentAssistant.name}
            </div>
            {currentAssistant.mbti_type && (
              <Tag
                style={{
                  background: `${themeGradient}15`,
                  color: themeGradient,
                  border: `1px solid ${themeGradient}30`,
                  borderRadius: 8,
                  fontSize: 11,
                  marginTop: 4,
                }}
              >
                {currentAssistant.mbti_type}
              </Tag>
            )}
          </div>
        </div>
      ) : (
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, color: isDark ? '#fff' : '#1f2937', fontSize: 16 }}>
            与AI助手聊天
          </div>
          <div style={{ fontSize: 12, color: colors.nameColor }}>
            选择一位助手开始对话
          </div>
        </div>
      )}

      {messages.length > 0 && !sending && (
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={handleRegenerate}
          style={{ color: colors.nameColor }}
        />
      )}

      <Link to="/profile">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '6px 12px',
          borderRadius: 12,
          background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
          cursor: 'pointer',
        }}>
          <UserOutlined style={{ color: themeGradient }} />
          <span style={{ color: isDark ? '#fff' : '#1f2937', fontSize: 14, fontWeight: 500 }}>
            {user?.nickname || '我的'}
          </span>
        </div>
      </Link>
    </div>
  )

  const chatInput = (
    <div style={{
      padding: '16px 20px',
      background: colors.headerBg,
      borderTop: `1px solid ${colors.borderColor}`,
      position: 'sticky',
      bottom: 0,
    }}>
      <div style={{
        display: 'flex',
        gap: 12,
        alignItems: 'flex-end',
        background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
        padding: '12px 16px',
        borderRadius: 20,
        border: `1px solid ${colors.borderColor}`,
      }}>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你想说的话..."
          autoSize={{ minRows: 1, maxRows: 6 }}
          style={{
            flex: 1,
            background: 'transparent',
            color: colors.inputText,
            border: 'none',
            resize: 'none',
            lineHeight: 1.6,
            fontSize: 15,
          }}
          disabled={sending}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={sending}
          disabled={!inputValue.trim()}
          style={{
            background: inputValue.trim()
              ? `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`
              : (isDark ? '#333' : '#e5e7eb'),
            border: 'none',
            borderRadius: 14,
            width: 44,
            height: 44,
            boxShadow: inputValue.trim() ? `0 4px 15px ${themeGradient}40` : 'none',
          }}
        />
      </div>
      <div style={{
        textAlign: 'center',
        marginTop: 12,
        fontSize: 11,
        color: colors.nameColor,
      }}>
        Enter 发送 · Shift + Enter 换行
      </div>
    </div>
  )

  if (assessmentStatus === null) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: colors.chatBg,
      }}>
        <div style={{ textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16, color: colors.nameColor }}>正在加载...</div>
        </div>
      </div>
    )
  }

  if (!assessmentStatus?.mbti || !assessmentStatus?.sbti || !assessmentStatus?.attachment) {
    return null
  }

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        height: '100vh',
        background: colors.chatBg,
        position: 'relative',
      }}
    >
      {/* 移动端 Drawer */}
      {isMobile && (
        <Drawer
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <StarOutlined style={{ color: themeGradient }} />
              <span>对话列表</span>
            </div>
          }
          placement="left"
          onClose={() => setSidebarOpen(false)}
          open={sidebarOpen}
          width={280}
          styles={{ header: { borderBottom: `1px solid ${colors.borderColor}` } }}
        >
          {sidebarContent}
        </Drawer>
      )}

      {/* 桌面端布局 */}
      {!isMobile && (
        <div style={{ display: 'flex', height: '100vh', flex: 1 }}>
          {/* 对话历史列表区域 */}
          <div
            style={{
              width: sidebarWidth,
              background: colors.sidebarBg,
              borderRight: `1px solid ${colors.borderColor}`,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              flexShrink: 0,
            }}
          >
            {sidebarContent}
          </div>

          {/* 分隔栏1：对话列表 <-> 虚拟形象 */}
          <div
            onMouseDown={(e) => handleDragStart(e, 'sidebar')}
            style={{
              width: 6,
              height: '100vh',
              cursor: 'col-resize',
              background: 'transparent',
              position: 'relative',
              zIndex: 10,
              flexShrink: 0,
            }}
          >
            <div style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              width: 3,
              height: 40,
              borderRadius: 2,
              background: isDragging === 'sidebar' ? themeGradient : colors.borderColor,
            }} />
          </div>

          {/* 虚拟形象展示区域 */}
          <div
            style={{
              width: avatarWidth,
              background: colors.sidebarBg,
              borderRight: `1px solid ${colors.borderColor}`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 16,
              overflow: 'hidden',
              flexShrink: 0,
            }}
          >
            {/* Live2D模型选择器 */}
            <div style={{
              marginBottom: 12,
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <SwapOutlined style={{ color: colors.nameColor, fontSize: 16 }} />
              <Select
                value={selectedLive2DModel || getLive2DModelPath(currentAssistant)}
                onChange={(value) => setSelectedLive2DModel(value)}
                onDropdownVisibleChange={(open) => {
                  if (open) {
                    // 预加载所有模型到缓存
                    const allPaths = LIVE2D_MODELS.map(m => m.path)
                    preloadModelsInBackground(allPaths)
                  }
                }}
                style={{ flex: 1, minWidth: 140 }}
                size="small"
                options={LIVE2D_MODELS.map(model => ({
                  value: model.path,
                  label: (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span>{model.name}</span>
                      <span style={{ color: '#8c8c8c', fontSize: 11 }}>{model.description}</span>
                    </div>
                  )
                }))}
                dropdownMatchSelectWidth={220}
              />
            </div>

            <Live2DCanvas
              key={selectedLive2DModel || getLive2DModelPath(currentAssistant)}
              modelPath={getLive2DModelPath(currentAssistant, selectedLive2DModel)}
              name=""
              expression={avatarExpression}
              motion={avatarMotion}
              isSpeaking={avatarIsSpeaking}
              scale={1.5}
              preferLive2D={true}
              onClick={() => {
                triggerAnimation('happy', 'wave')
              }}
            />
          </div>

          {/* 分隔栏2：虚拟形象 <-> 聊天区域 */}
          <div
            onMouseDown={(e) => handleDragStart(e, 'avatar')}
            style={{
              width: 6,
              height: '100vh',
              cursor: 'col-resize',
              background: 'transparent',
              position: 'relative',
              zIndex: 10,
              flexShrink: 0,
            }}
          >
            <div style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              width: 3,
              height: 40,
              borderRadius: 2,
              background: isDragging === 'avatar' ? themeGradient : colors.borderColor,
            }} />
          </div>
        </div>
      )}

      {/* 聊天区域 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {chatHeader}

        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: isMobile ? 16 : 20,
          background: colors.chatBg,
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Spin size="large" />
              <div style={{ marginTop: 16, color: colors.nameColor }}>加载历史消息...</div>
            </div>
          ) : messages.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px 20px',
              maxWidth: 500,
              margin: '0 auto',
            }}>
              {/* Welcome Card - 虚拟形象已移至左侧面板 */}
              <div style={{
                background: `linear-gradient(135deg, ${themeGradient}10 0%, ${themeGradient}05 100%)`,
                borderRadius: 24,
                padding: '40px 32px',
                marginBottom: 40,
                border: `1px solid ${themeGradient}20`,
              }}>
                <h2 style={{
                  fontSize: 24,
                  fontWeight: 700,
                  color: isDark ? '#fff' : '#1f2937',
                  marginBottom: 12,
                }}>
                  {currentAssistant
                    ? `与 ${currentAssistant.name} 的对话`
                    : '开始一段心灵对话'}
                </h2>
                <p style={{
                  color: colors.nameColor,
                  fontSize: 15,
                  lineHeight: 1.7,
                  margin: 0,
                }}>
                  {currentAssistant
                    ? currentAssistant.greeting || '今天想聊些什么呢？'
                    : '选择一位懂你的AI助手，开启专属的心灵陪伴之旅'}
                </p>
              </div>

              {/* Quick Replies */}
              {showQuickReplies && (
                <div>
                  <div style={{
                    fontSize: 13,
                    color: colors.nameColor,
                    marginBottom: 16,
                    fontWeight: 500,
                  }}>
                    快捷对话
                  </div>
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 10,
                    justifyContent: 'center',
                  }}>
                    {quickReplies.map((item, idx) => (
                      <Button
                        key={idx}
                        icon={item.icon}
                        onClick={() => handleQuickReply(item.prompt)}
                        style={{
                          borderRadius: 16,
                          padding: '8px 16px',
                          height: 'auto',
                          background: `${item.color}10`,
                          border: `1px solid ${item.color}30`,
                          color: item.color,
                          fontSize: 13,
                          fontWeight: 500,
                        }}
                      >
                        {item.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div>
              {messages.map((msg: any) => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    marginBottom: 20,
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    alignItems: 'flex-start',
                    gap: 12,
                    animation: 'fadeIn 0.3s ease',
                  }}
                >
                  {msg.role === 'assistant' && (
                    <Avatar
                      src={currentAssistant?.avatar}
                      style={{
                        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                        flexShrink: 0,
                        width: 40,
                        height: 40,
                        fontSize: 16,
                        fontWeight: 600,
                      }}
                    >
                      {currentAssistant?.name?.[0] || 'AI'}
                    </Avatar>
                  )}

                  <div style={{
                    maxWidth: isMobile ? '85%' : '60%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  }}>
                    {msg.role === 'assistant' && currentAssistant && (
                      <div style={{
                        fontSize: 12,
                        color: colors.nameColor,
                        marginBottom: 6,
                        marginLeft: 4,
                        fontWeight: 500,
                      }}>
                        {currentAssistant.name}
                      </div>
                    )}

                    <div style={{
                      padding: '14px 18px',
                      borderRadius: msg.role === 'user'
                        ? '20px 20px 6px 20px'
                        : '20px 20px 20px 6px',
                      background: msg.role === 'user'
                        ? `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`
                        : (isDark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.95)'),
                      color: msg.role === 'user' ? '#fff' : colors.bubbleText,
                      boxShadow: msg.role === 'user'
                        ? `0 8px 30px ${themeGradient}40`
                        : '0 4px 20px rgba(0,0,0,0.08)',
                      wordBreak: 'break-word',
                      textAlign: 'left',
                      lineHeight: 1.7,
                      fontSize: 15,
                      maxWidth: '100%',
                    }}>
                      {msg.role === 'assistant' ? (
                        <MarkdownContent content={msg.content || '...'} />
                      ) : (
                        <span style={{ whiteSpace: 'pre-wrap', overflowWrap: 'break-word' }}>
                          {msg.content || '...'}
                        </span>
                      )}
                    </div>

                    <div style={{
                      fontSize: 11,
                      color: colors.timeColor,
                      marginTop: 6,
                      paddingLeft: 4,
                      paddingRight: 4,
                    }}>
                      {new Date(msg.created_at).toLocaleString('zh-CN', {
                        timeZone: 'Asia/Shanghai',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>

                  {msg.role === 'user' && (
                    <Avatar
                      src={user?.avatar}
                      style={{
                        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                        flexShrink: 0,
                        width: 40,
                        height: 40,
                        fontSize: 16,
                        fontWeight: 600,
                      }}
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
                  marginBottom: 20,
                  justifyContent: 'flex-start',
                  alignItems: 'flex-start',
                  gap: 12,
                }}>
                  <Avatar
                    src={currentAssistant?.avatar}
                    style={{
                      background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                      flexShrink: 0,
                      width: 40,
                      height: 40,
                    }}
                  >
                    {currentAssistant?.name?.[0] || 'AI'}
                  </Avatar>
                  <div style={{
                    maxWidth: isMobile ? '85%' : '60%',
                    padding: '14px 18px',
                    borderRadius: '20px 20px 20px 6px',
                    background: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.95)',
                    color: colors.bubbleText,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                    lineHeight: 1.7,
                    fontSize: 15,
                  }}>
                    <MarkdownContent content={streamingMessage} />
                  </div>
                </div>
              )}

              {/* Typing indicator */}
              {sending && streamingMessage.length === 0 && (
                <div style={{
                  display: 'flex',
                  marginBottom: 20,
                  justifyContent: 'flex-start',
                  alignItems: 'flex-start',
                  gap: 12,
                }}>
                  <Avatar
                    src={currentAssistant?.avatar}
                    style={{
                      background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                      flexShrink: 0,
                      width: 40,
                      height: 40,
                    }}
                  >
                    {currentAssistant?.name?.[0] || 'AI'}
                  </Avatar>
                  <div style={{
                    padding: '14px 20px',
                    borderRadius: '20px 20px 20px 6px',
                    background: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.95)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}>
                    {[0, 1, 2].map((i) => (
                      <span key={i} style={{
                        display: 'inline-block',
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: themeGradient,
                        animation: `typing 1.4s infinite ease-in-out ${i * 0.2}s`,
                      }} />
                    ))}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {chatInput}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-8px); opacity: 1; }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
        }
        @keyframes breathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.03); }
        }
        @keyframes bounce-subtle {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  )
}
