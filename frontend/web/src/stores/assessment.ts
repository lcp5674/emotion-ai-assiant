import { create } from 'zustand'

// SBTI Store - 匹配后端响应格式
interface SbtiQuestion {
  id: number
  question_no: number
  statement_a: string
  theme_a: string
  statement_b: string
  theme_b: string
  domain: string
}

interface SbtiResult {
  id: number
  top5_themes: string[]
  top5_scores: number[]
  domain_scores: {
    执行力: number
    影响力: number
    关系建立: number
    战略思维: number
  }
  dominant_domain: string
  report: {
    themes?: Array<{
      name: string
      description: string
      strengths: string[]
      growth_suggestions: string[]
    }>
    relationship_insights?: {
      strengths: string[]
      communication_style: string
      growth_areas: string[]
    }
    career_suggestions?: string[]
  }
  created_at: string
}

interface SbtiState {
  questions: SbtiQuestion[]
  currentQuestionIndex: number
  answers: Array<{ question_id: number; answer: string }>
  result: SbtiResult | null
  loading: boolean
  setQuestions: (questions: SbtiQuestion[]) => void
  setCurrentIndex: (index: number) => void
  addAnswer: (answer: { question_id: number; answer: string }) => void
  setResult: (result: SbtiResult) => void
  setLoading: (loading: boolean) => void
  reset: () => void
}

export const useSbtiStore = create<SbtiState>((set) => ({
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
        answers: [...state.answers.filter(a => a.question_id !== answer.question_id), answer],
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

// Attachment Store - 匹配后端响应格式
interface AttachmentQuestion {
  id: number
  question_no: number
  question_text: string
  scale_min: number
  scale_max: number
  scale_min_label: string
  scale_max_label: string
}

interface AttachmentResult {
  id: number
  style: string
  anxiety_score: number
  avoidance_score: number
  characteristics: string[]
  relationship_tips: string
  self_growth_tips: string
  created_at: string
}

interface AttachmentState {
  questions: AttachmentQuestion[]
  currentQuestionIndex: number
  answers: Array<{ question_id: number; score: number }>
  result: AttachmentResult | null
  loading: boolean
  setQuestions: (questions: AttachmentQuestion[]) => void
  setCurrentIndex: (index: number) => void
  addAnswer: (answer: { question_id: number; score: number }) => void
  setResult: (result: AttachmentResult) => void
  setLoading: (loading: boolean) => void
  reset: () => void
}

export const useAttachmentStore = create<AttachmentState>((set) => ({
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
        answers: [...state.answers.filter(a => a.question_id !== answer.question_id), answer],
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

// Deep Profile Store
interface AiPartner {
  id: number
  name: string
  avatar?: string
  match_reason: string
  description: string
}

interface DeepProfileState {
  profile: {
    mbti?: any
    sbti?: any
    attachment?: any
    comprehensive_insights?: string[]
  } | null
  aiPartners: AiPartner[]
  loading: boolean
  setProfile: (profile: any) => void
  setAiPartners: (partners: AiPartner[]) => void
  setLoading: (loading: boolean) => void
}

export const useDeepProfileStore = create<DeepProfileState>((set) => ({
  profile: null,
  aiPartners: [],
  loading: false,

  setProfile: (profile) => set({ profile }),
  setAiPartners: (partners) => set({ aiPartners: partners }),
  setLoading: (loading) => set({ loading }),
}))
