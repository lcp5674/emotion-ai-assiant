// SBTI 相关类型定义 - 匹配后端 Schema
export interface SbtiQuestion {
  id: number
  question_no: number
  statement_a: string
  theme_a: string
  statement_b: string
  theme_b: string
  domain: string
}

export interface SbtiAnswer {
  question_id: number
  answer: string
}

export interface SbtiResult {
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

// 依恋风格相关类型定义 - 匹配后端 Schema
export interface AttachmentQuestion {
  id: number
  question_no: number
  question_text: string
  scale_min: number
  scale_max: number
  scale_min_label: string
  scale_max_label: string
}

export interface AttachmentAnswer {
  question_id: number
  score: number
}

export interface AttachmentResult {
  id: number
  style: string
  anxiety_score: number
  avoidance_score: number
  characteristics: string[]
  relationship_tips: string
  self_growth_tips: string
  created_at: string
}

// 深度画像类型定义
export interface DeepProfile {
  mbti?: {
    type: string
    personality: string
    strengths: string[]
  }
  sbti?: {
    top_themes: string[]
  }
  attachment?: {
    style: string
    description: string
  }
  comprehensive_insights: string[]
  ai_partner_recommendations: Array<{
    id: number
    name: string
    avatar?: string
    match_reason: string
    description: string
  }>
}
