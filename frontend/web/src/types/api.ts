/**
 * API 响应类型定义
 * 使用索引签名允许额外字段
 */

// 通用响应
export interface ApiResponse<T = unknown> {
  code?: number
  message?: string
  data?: T
  [key: string]: unknown
}

// 分页响应 - 使用更灵活的定义
export interface PaginatedResponse<T> {
  list: T[]
  total: number
  page?: number
  page_size?: number
  data?: T[]
  [key: string]: unknown
}

// 用户相关
export interface User {
  id: number
  phone?: string
  nickname?: string
  avatar?: string
  mbti_type?: string
  member_level: string
  member_expire_at?: string
  is_verified: boolean
  created_at?: string
  last_login_at?: string
  [key: string]: unknown
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  user: User
  [key: string]: unknown
}

export interface RefreshResponse {
  access_token: string
  token_type: string
  expires_in: number
  [key: string]: unknown
}

// MBTI相关
export interface MbtiQuestion {
  id: number
  dimension: string
  question_no: number
  question_text: string
  option_a: string
  option_b: string
  [key: string]: unknown
}

export interface MbtiAnswer {
  question_id: number
  answer: string
}

export interface MbtiResult {
  id: number
  mbti_type: string
  ei_score: number
  sn_score: number
  tf_score: number
  jp_score: number
  dimensions: Array<{
    dimension: string
    score: number
    倾向: string
  }>
  personality: string
  strengths: string[]
  weaknesses: string[]
  suitable_jobs: string[]
  relationship_tips: string
  career_advice: string
  [key: string]: unknown
}

// 对话相关
export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  message_type?: string
  emotion?: string
  sentiment_score?: number
  is_collected?: boolean
  created_at: string
  [key: string]: unknown
}

export interface Conversation {
  id: number
  session_id: string
  title?: string
  assistant_id?: number
  message_count: number
  status: string
  created_at: string
  updated_at: string
  [key: string]: unknown
}

// AI助手
export interface AiAssistant {
  id: number
  name: string
  description?: string
  avatar?: string
  mbti_type: string
  personality?: string
  speaking_style?: string
  expertise?: string
  greeting?: string
  tags?: string[]
  is_active: boolean
  is_recommended?: boolean
  created_at?: string
  [key: string]: unknown
}

// 知识库
export interface Article {
  id: number
  title: string
  summary?: string
  content?: string
  category: string
  tags?: string
  cover_image?: string
  author?: string
  view_count: number
  like_count: number
  is_collected?: boolean
  created_at: string
  updated_at?: string
  article?: Article
  related_articles?: Article[]
  [key: string]: unknown
}

export interface Banner {
  id: number
  title: string
  image_url: string
  link_url?: string
  position: string
  is_active: boolean
  [key: string]: unknown
}

export interface Announcement {
  id: number
  title: string
  content: string
  is_active: boolean
  created_at: string
  [key: string]: unknown
}

// 日记相关 - 使用更灵活的定义
export interface Diary {
  id: number
  user_id: number
  title: string
  content: string
  mood?: string
  emotions?: string[]
  tags?: string[]
  weather?: string
  location?: string
  is_public: boolean
  is_analyzed: boolean
  analysis_result?: string
  like_count: number
  comment_count: number
  created_at: string
  updated_at: string
  analysis_status?: string
  is_shared?: boolean
  share_public?: boolean
  date?: string
  mood_score?: number
  mood_level?: string
  primary_emotion?: string
  category?: string
  analysis?: string
  suggestion?: string
  [key: string]: unknown
}

export interface Mood {
  id: number
  user_id: number
  mood: string
  score: number
  note?: string
  created_at: string
  [key: string]: unknown
}

export interface Tag {
  id: number
  name: string
  color?: string
  usage_count: number
  [key: string]: unknown
}

export interface DiaryStats {
  total_count: number
  total_words: number
  current_streak: number
  longest_streak: number
  avg_mood_score: number
  top_emotions: Array<{ emotion: string; count: number }>
  max_streak?: number
  avg_mood?: number
  avg_words_per_day?: number
  categories?: string[]
  [key: string]: unknown
}

export interface DiaryTrend {
  date: string
  count: number
  avg_mood_score?: number
  time_range?: string
  start_date?: string
  end_date?: string
  avg_score?: number
  [key: string]: unknown
}

// 会员相关
export interface MemberPrice {
  level: string
  name: string
  price: number
  original_price?: number
  duration_days: number
  features: string[]
  is_popular?: boolean
  [key: string]: unknown
}

export interface MemberOrder {
  order_no: string
  level: string
  amount: number
  status: string
  created_at: string
  paid_at?: string
}

// 配置相关
export interface SystemConfig {
  llm_provider: string
  openai_api_key?: string
  openai_model?: string
  anthropic_api_key?: string
  anthropic_model?: string
  [key: string]: unknown
}

// 兼容旧类型的别名
export type MoodTrend = DiaryTrend
export type DiaryDetail = Diary