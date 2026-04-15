/**
 * 用户行为埋点工具
 * 用于记录用户行为数据
 */
import { apiClient } from '../api/request'

export interface TrackEventParams {
  event_type: string
  event_properties?: Record<string, any>
  user_properties?: Record<string, any>
}

export interface PageViewParams {
  page_name: string
  referrer?: string
}

/**
 * 埋点事件
 */
export async function trackEvent(params: TrackEventParams): Promise<boolean> {
  try {
    await apiClient.post('/analytics/track', params)
    return true
  } catch (error) {
    console.error('埋点失败:', error)
    return false
  }
}

/**
 * 页面浏览埋点
 */
export async function trackPageView(params: PageViewParams): Promise<boolean> {
  try {
    await apiClient.post('/analytics/page_view', params)
    return true
  } catch (error) {
    console.error('页面埋点失败:', error)
    return false
  }
}

/**
 * 获取支持的事件类型
 */
export async function getEventTypes(): Promise<Record<string, string>> {
  try {
    const res = await apiClient.get('/analytics/events')
    return res.data.events
  } catch (error) {
    console.error('获取事件类型失败:', error)
    return {}
  }
}

// 预定义事件常量
export const EVENTS = {
  // 用户行为
  USER_REGISTER: 'user_register',
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  
  // MBTI测试
  MBTI_START: 'mbti_start',
  MBTI_COMPLETE: 'mbti_complete',
  MBTI_QUICK_START: 'mbti_quick_start',
  MBTI_QUICK_COMPLETE: 'mbti_quick_complete',
  
  // AI对话
  CHAT_START: 'chat_start',
  CHAT_SEND: 'chat_send',
  CHAT_RECEIVE: 'chat_receive',
  
  // 页面浏览
  PAGE_VIEW_HOME: 'page_view_home',
  PAGE_VIEW_PROFILE: 'page_view_profile',
  PAGE_VIEW_ASSISTANT: 'page_view_assistant',
  PAGE_VIEW_DIARY: 'page_view_diary',
  PAGE_VIEW_PAYMENT: 'page_view_payment',
  
  // 支付
  PAYMENT_CLICK: 'payment_click',
  PAYMENT_SUCCESS: 'payment_success',
}

// 页面名称常量
export const PAGES = {
  HOME: 'home',
  PROFILE: 'profile',
  ASSISTANT: 'assistant',
  DIARY: 'diary',
  PAYMENT: 'payment',
}