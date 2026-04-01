import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { message } from 'antd'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data as any
  },
  async (error) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          // token过期，清除并跳转登录
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          message.error('登录已过期，请重新登录')
          break
        case 403:
          message.error('没有权限')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器错误')
          break
        default:
          message.error(data?.detail || '请求失败')
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default request

// API请求函数
export const api = {
  // 认证
  auth: {
    sendCode: (phone: string): Promise<any> =>
      request.post('/auth/send_code', { phone }),
    register: (data: { phone: string; password: string; code: string; nickname?: string }): Promise<any> =>
      request.post('/auth/register', data),
    login: (data: { phone: string; password: string }): Promise<any> =>
      request.post('/auth/login', data),
    refresh: (refresh_token: string): Promise<any> =>
      request.post('/auth/refresh', { refresh_token }),
    me: (): Promise<any> => request.get('/auth/me'),
  },

  // 用户
  user: {
    profile: (): Promise<any> => request.get('/user/profile'),
    updateProfile: (data: { nickname?: string; avatar?: string }): Promise<any> =>
      request.put('/user/profile', data),
    changePassword: (data: { old_password: string; new_password: string }): Promise<any> =>
      request.post('/user/password', data),
    stats: (): Promise<any> => request.get('/user/stats'),
  },

  // MBTI
  mbti: {
    questions: (dimension?: string): Promise<any> =>
      request.get('/mbti/questions', { params: { dimension } }),
    start: (): Promise<any> => request.post('/mbti/start'),
    submit: (answers: Array<{ question_id: number; answer: string }>): Promise<any> =>
      request.post('/mbti/submit', { answers }),
    result: (): Promise<any> => request.get('/mbti/result'),
    assistants: (params?: { mbti_type?: string; tags?: string; recommended?: boolean }): Promise<any> =>
      request.get('/mbti/assistants', { params }),
    assistantDetail: (id: number): Promise<any> => request.get(`/mbti/assistants/${id}`),
  },

  // 对话
  chat: {
    send: (data: { session_id?: string; assistant_id?: number; content: string }): Promise<any> =>
      request.post('/chat/send', data),
    create: (data: { assistant_id: number; title?: string }): Promise<any> =>
      request.post('/chat/create', data),
    conversations: (params?: { limit?: number; offset?: number }): Promise<any> =>
      request.get('/chat/conversations', { params }),
    history: (session_id: string, params?: { limit?: number; before_id?: number }): Promise<any> =>
      request.get(`/chat/history/${session_id}`, { params }),
    collect: (message_id: number): Promise<any> =>
      request.post('/chat/collect', { message_id }),
    close: (session_id: string): Promise<any> =>
      request.post(`/chat/close/${session_id}`),
    updateTitle: (session_id: string, title: string): Promise<any> =>
      request.put(`/chat/title/${session_id}`, { title }),
  },

  // 知识库
  knowledge: {
    articles: (params?: { category?: string; page?: number; page_size?: number }): Promise<any> =>
      request.get('/knowledge/articles', { params }),
    articleDetail: (id: number): Promise<any> => request.get(`/knowledge/articles/${id}`),
    banners: (position: string = 'home'): Promise<any> =>
      request.get('/knowledge/banners', { params: { position } }),
    announcements: (): Promise<any> => request.get('/knowledge/announcements'),
    collect: (article_id: number): Promise<any> =>
      request.post(`/knowledge/articles/${article_id}/collect`),
    collections: (params?: { page?: number; page_size?: number }): Promise<any> =>
      request.get('/knowledge/collections', { params }),
  },

  // 会员
  member: {
    prices: (): Promise<any> => request.get('/member/prices'),
    order: (level: string): Promise<any> => request.post('/member/order', { level }),
    pay: (order_no: string): Promise<any> => request.post(`/member/order/${order_no}/pay`),
    status: (): Promise<any> => request.get('/member/status'),
  },

  // 管理
  admin: {
    config: (): Promise<any> => request.get('/admin/config'),
    updateConfig: (data: any): Promise<any> => request.post('/admin/config', data),
    testConnection: (): Promise<any> => request.post('/admin/test'),
    assistants: (): Promise<any> => request.get('/admin/assistants'),
    createAssistant: (data: any): Promise<any> => request.post('/admin/assistants', data),
    updateAssistant: (id: number, data: any): Promise<any> => request.put(`/admin/assistants/${id}`, data),
    deleteAssistant: (id: number): Promise<any> => request.delete(`/admin/assistants/${id}`),
  },

  // 情感日记
  diary: {
    create: (data: any): Promise<any> => request.post('/diary/create', data),
    get: (id: number): Promise<any> => request.get(`/diary/${id}`),
    getByDate: (date: string): Promise<any> => request.get(`/diary/date/${date}`),
    list: (params?: any): Promise<any> => request.get('/diary/list', { params }),
    update: (id: number, data: any): Promise<any> => request.put(`/diary/${id}`, data),
    delete: (id: number): Promise<any> => request.delete(`/diary/${id}`),

    // 心情记录
    createMood: (data: any): Promise<any> => request.post('/diary/mood', data),
    listMoods: (params?: any): Promise<any> => request.get('/diary/mood/list', { params }),

    // 标签
    createTag: (data: any): Promise<any> => request.post('/diary/tags', data),
    listTags: (): Promise<any> => request.get('/diary/tags'),
    updateTag: (id: number, data: any): Promise<any> => request.put(`/diary/tags/${id}`, data),
    deleteTag: (id: number): Promise<any> => request.delete(`/diary/tags/${id}`),

    // 统计和分析
    stats: (): Promise<any> => request.get('/diary/stats'),
    trend: (time_range: string = 'week'): Promise<any> => request.get('/diary/trend', { params: { time_range } }),
    analyze: (id: number): Promise<any> => request.post(`/diary/analyze/${id}`),

    // 配置
    getEmotionConfig: (): Promise<any> => request.get('/diary/emotion-config'),
    getMoodConfig: (): Promise<any> => request.get('/diary/mood-config'),
  },

  // WebSocket
  websocket: {
    connect: (sessionId?: string, assistantId?: number): string => {
      const token = localStorage.getItem('access_token')
      const params = new URLSearchParams()
      if (token) params.append('token', token)
      if (sessionId) params.append('session_id', sessionId)
      if (assistantId) params.append('assistant_id', assistantId.toString())
      return `ws://localhost:8000/ws/chat?${params.toString()}`
    },
  },

  // 支付
  payment: {
    wechat: {
      createOrder: (level: string): Promise<any> => 
        request.post('/payment/wechat/native', { level }),
      query: (orderNo: string): Promise<any> => 
        request.get(`/payment/wechat/query/${orderNo}`),
    },
    stripe: {
      createCheckout: (level: string): Promise<any> => 
        request.post('/payment/stripe/checkout', { level }),
    },
    mock: {
      complete: (orderNo: string): Promise<any> => 
        request.post(`/payment/mock/${orderNo}/complete`),
    },
  },
}
