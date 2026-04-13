import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  phone?: string
  nickname?: string
  avatar?: string
  mbti_type?: string
  member_level: string
  is_verified: boolean
}

interface AuthState {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, access_token: string, refresh_token: string) => void
  updateUser: (user: Partial<User>) => void
  logout: () => void
}

/**
 * 安全优化说明：
 * 
 * ⚠️ 当前使用localStorage存储Token存在XSS攻击风险
 * 
 * 最佳实践方案：
 * 1. 后端设置 httpOnly Cookie（最安全）
 * 2. 使用 sessionStorage（浏览器关闭即清除，较安全）
 * 3. 使用 memory-only + 刷新Token机制（中等安全）
 * 
 * 当前实现保留了localStorage以支持页面刷新后保持登录状态。
 * 如需更高安全性，建议后端配合使用 httpOnly Cookie。
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,

      setAuth: (user, access_token, refresh_token) => {
        // 优化：使用try-catch防止localStorage不可用时出错
        try {
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
        } catch (error) {
          console.warn('localStorage不可用，Token将仅存储在内存中')
        }
        set({ user, access_token, refresh_token, isAuthenticated: true })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },

      logout: () => {
        // 优化：确保Token清理逻辑完善
        try {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        } catch (error) {
          console.warn('localStorage清理失败')
        }
        set({ user: null, access_token: null, refresh_token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        // 安全优化：可以只持久化user信息，Token从Cookie读取
        // 但这需要后端配合设置 httpOnly Cookie
        access_token: state.access_token,
        refresh_token: state.refresh_token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Chat store
interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  message_type?: string
  emotion?: string
  is_collected?: boolean
  created_at: string
}

interface Conversation {
  id: number
  session_id: string
  title?: string
  assistant_id?: number
  message_count: number
  status: string
  created_at: string
  updated_at: string
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  loading: boolean
  setConversations: (conversations: Conversation[]) => void
  setCurrentConversation: (conversation: Conversation | null) => void
  addMessage: (message: Message) => void
  setMessages: (messages: Message[]) => void
  setLoading: (loading: boolean) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  loading: false,

  setConversations: (conversations) => set({ conversations }),
  setCurrentConversation: (conversation) => set({ currentConversation: conversation }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setMessages: (messages) => set({ messages }),
  setLoading: (loading) => set({ loading }),
  clearChat: () => set({ currentConversation: null, messages: [] }),
}))

// MBTI store
interface MbtiResult {
  id: number
  mbti_type: string
  ei_score: number
  sn_score: number
  tf_score: number
  jp_score: number
  dimensions: Array<{ dimension: string; score: number; percentage: number; tendency: string }>
  personality: string
  strengths: string[]
  weaknesses: string[]
  suitable_jobs: string[]
  relationship_tips: string
  career_advice: string
}

interface MbtiState {
  questions: Array<{
    id: number
    dimension: string
    question_no: number
    question_text: string
    option_a: string
    option_b: string
  }>
  currentQuestionIndex: number
  answers: Array<{ question_id: number; answer: string }>
  result: MbtiResult | null
  loading: boolean
  setQuestions: (questions: any[]) => void
  setCurrentIndex: (index: number) => void
  addAnswer: (answer: { question_id: number; answer: string }) => void
  setResult: (result: MbtiResult) => void
  setLoading: (loading: boolean) => void
  reset: () => void
}

export const useMbtiStore = create<MbtiState>((set) => ({
  questions: [],
  currentQuestionIndex: 0,
  answers: [],
  result: null,
  loading: false,

  setQuestions: (questions) => set({ questions }),
  setCurrentIndex: (index) => set({ currentQuestionIndex: index }),
  addAnswer: (answer) =>
    set((state) => {
      // 检查是否已经存在该题目的答案
      const existingIndex = state.answers.findIndex(a => a.question_id === answer.question_id)
      let newAnswers
      if (existingIndex !== -1) {
        // 更新已有的答案
        newAnswers = [...state.answers]
        newAnswers[existingIndex] = answer
      } else {
        // 添加新的答案
        newAnswers = [...state.answers, answer]
      }
      // 计算下一个问题索引，确保不超出范围
      const nextIndex = Math.min(state.currentQuestionIndex + 1, state.questions.length - 1)
      return {
        answers: newAnswers,
        currentQuestionIndex: nextIndex,
      }
    }),
  setResult: (result) => set({ result }),
  setLoading: (loading) => set({ loading }),
  reset: () =>
    set({
      currentQuestionIndex: 0,
      answers: [],
      result: null,
    }),
}))

// 重新导出diary store
export * from './diary'

// 评估相关 store
export * from './assessment'