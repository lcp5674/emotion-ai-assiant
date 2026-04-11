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

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,

      setAuth: (user, access_token, refresh_token) => {
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        set({ user, access_token, refresh_token, isAuthenticated: true })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, access_token: null, refresh_token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
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
  dimensions: Array<{ dimension: string; score: number; 倾向: string }>
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
      const isLastQuestion = state.currentQuestionIndex === state.questions.length - 1
      return {
        answers: [...state.answers, answer],
        currentQuestionIndex: isLastQuestion ? state.currentQuestionIndex : state.currentQuestionIndex + 1,
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