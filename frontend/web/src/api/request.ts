import axios, { AxiosInstance, AxiosResponse } from 'axios'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 用于存储 navigate 函数，避免循环依赖
let navigateFn: ((to: string) => void) | null = null

// 导出设置 navigate 的函数
export const setNavigate = (navigate: (to: string) => void) => {
  navigateFn = navigate
}

/**
 * Token获取和安全说明
 * 
 * ⚠️ 安全警告：
 * 1. 当前从localStorage读取Token存在XSS风险
 * 2. WebSocket Token通过URL参数传递，会被记录在日志中
 * 
 * 推荐迁移方案：
 * 1. 后端设置 httpOnly Cookie（推荐）- Token自动随请求发送
 * 2. WebSocket使用子协议进行认证 - 连接建立后发送认证消息
 * 
 * 当前保留localStorage以兼容现有架构，生产环境应尽快迁移
 */

// 当前方案：使用 localStorage + URL参数（存在安全风险，待迁移）
// 迁移后方案：httpOnly Cookie + WebSocket子协议认证
// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    // 优化：添加try-catch防止localStorage不可用
    let token: string | null = null
    try {
      token = localStorage.getItem('access_token')
    } catch (error) {
      console.warn('无法从localStorage读取Token')
    }
    
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
    const { response, config } = error

    if (response) {
      const { status, data } = response

      // 检查是否是认证相关的接口（登录、注册、发送验证码等）
      const isAuthEndpoint = config?.url && (
        config.url.includes('/auth/login') ||
        config.url.includes('/auth/register') ||
        config.url.includes('/auth/send_code') ||
        config.url.includes('/auth/reset_password')
      )

      switch (status) {
        case 401:
          // 401错误 - 直接跳转到登录页面
          // 登录接口的 401 是密码错误，不跳转
          // 其他接口的 401 说明未登录或token过期，需要跳转
          if (!isAuthEndpoint) {
            // 清理 token
            try {
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              localStorage.removeItem('auth-storage')
            } catch (e) {
              console.warn('清理token失败')
            }

            // 跳转到登录页面
            if (navigateFn) {
              navigateFn('/login')
            } else {
              window.location.href = '/login'
            }
            // 返回 rejected promise 阻止后续处理
            return Promise.reject(new Error('Unauthorized: Token expired or invalid'))
          }

          // 登录接口返回密码错误提示
          if (data?.detail) {
            return Promise.reject(new Error(data.detail))
          }
          return Promise.reject(new Error('登录失败，请检查账号密码'))
        case 404:
          // 404错误不抛出，而是返回null，让调用方优雅处理"未测评"等情况
          return null as any
        case 500:
          // 服务器错误
          return Promise.reject(new Error('Server Error: 服务器内部错误'))
        default:
          // 其他错误，返回错误对象
          const errorMessage = response.data?.message || '请求失败'
          return Promise.reject(new Error(errorMessage))
      }
    }

    // 网络错误，返回错误对象
    return Promise.reject(new Error('Network Error: 网络连接失败，请检查网络'))
  }
)

export default request

// API请求函数
export const api = {
  // 认证
  auth: {
    sendCode: (phone: string): Promise<any> =>
      request.post('/auth/send_code', { phone }),
    // 注册 - 支持手机号、邮箱、用户名
    register: (data: {
      phone?: string;
      email?: string;
      username?: string;
      password: string;
      code?: string;
      nickname?: string;
    }): Promise<any> =>
      request.post('/auth/register', data),
    // 登录 - 支持用户名、手机号、邮箱
    login: (data: { identifier: string; password: string }): Promise<any> =>
      request.post('/auth/login', data),
    refresh: (refresh_token: string): Promise<any> =>
      request.post('/auth/refresh', { refresh_token }),
    me: (): Promise<any> => request.get('/auth/me'),
    logout: (): Promise<any> => request.post('/auth/logout'),
    resetPassword: (data: { phone: string; code: string; new_password: string }): Promise<any> =>
      request.post('/auth/reset_password', data),
    crisisResources: (): Promise<any> => request.get('/auth/crisis-resources'),
  },

  // 用户
  user: {
    profile: (): Promise<any> => request.get('/user/profile'),
    updateProfile: (data: { nickname?: string; avatar?: string }): Promise<any> =>
      request.put('/user/profile', data),
    changePassword: (data: { old_password: string; new_password: string }): Promise<any> =>
      request.post('/user/password', data),
    stats: (): Promise<any> => request.get('/user/stats'),
    onboardingStatus: (): Promise<any> => request.get('/user/onboarding-status'),
    markOnboardingStep: (data: { step: string }): Promise<any> => 
      request.post('/user/mark-onboarding-step', data),
    privacyInfo: (): Promise<any> => request.get('/user/privacy-info'),
    exportData: (): Promise<any> => request.get('/user/export-data'),
    deleteAccount: (password: string): Promise<any> => 
      request.post('/user/delete-account', { password }),
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
    recommendedAssistants: (): Promise<any> =>
      request.get('/mbti/assistants/recommended'),
    assistantDetail: (id: number): Promise<any> => request.get(`/mbti/assistants/${id}`),
    toggleFavorite: (assistant_id: number): Promise<{ is_favorited: boolean; message: string }> =>
      request.post(`/mbti/assistants/${assistant_id}/favorite`),
    favorites: (): Promise<any> => request.get('/mbti/assistants/favorites'),
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
    delete: (session_id: string): Promise<any> =>
      request.delete(`/chat/conversations/${session_id}`),
    updateTitle: (session_id: string, title: string): Promise<any> =>
      request.put(`/chat/title/${session_id}`, { title }),
  },

  // 知识库
  knowledge: {
    articles: (params?: { category?: string; tags?: string; page?: number; page_size?: number }): Promise<any> =>
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
    testProvider: (provider: string): Promise<any> => request.post('/admin/test_provider', null, { params: { provider } }),
    providerStatus: (): Promise<any> => request.get('/admin/provider_status'),
    assistants: (): Promise<any> => request.get('/admin/assistants'),
    createAssistant: (data: any): Promise<any> => request.post('/admin/assistants', data),
    updateAssistant: (id: number, data: any): Promise<any> => request.put(`/admin/assistants/${id}`, data),
    deleteAssistant: (id: number): Promise<any> => request.delete(`/admin/assistants/${id}`),
    // 知识库同步
    knowledgeSyncConfig: (): Promise<any> => request.get('/admin/knowledge-sync/config'),
    updateKnowledgeSyncConfig: (data: any): Promise<any> => request.put('/admin/knowledge-sync/config', data),
    triggerKnowledgeSync: (): Promise<any> => request.post('/admin/knowledge-sync/trigger'),
    knowledgeSyncStatus: (): Promise<any> => request.get('/admin/knowledge-sync/status'),
    // 知识库Embedding和分块配置
    knowledgeBaseConfig: (): Promise<any> => request.get('/admin/knowledge-base/config'),
    updateKnowledgeBaseConfig: (data: any): Promise<any> => request.put('/admin/knowledge-base/config', data),
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
    stats: (time_range: string = 'month'): Promise<any> => request.get('/diary/stats', { params: { time_range } }),
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
      
      // 优化WebSocket URL配置
      // 1. 优先使用环境变量
      // 2. 智能检测当前页面协议（http/https）并选择对应WebSocket协议（ws/wss）
      // 3. 使用当前域名作为默认值
      let wsBaseUrl = import.meta.env.VITE_WS_BASE_URL
      
      if (!wsBaseUrl) {
        // 检测当前页面协议
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        wsBaseUrl = `${protocol}//${host}`
      } else if (!wsBaseUrl.startsWith('ws')) {
        // 确保协议正确
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        wsBaseUrl = `${protocol}//${wsBaseUrl.replace(/^(https?:)?\/\//, '')}`
      }
      
      return `${wsBaseUrl}/api/v1/ws/chat?${params.toString()}`
    },
  },

  // 支付
  payment: {
    plans: (): Promise<any> => request.get('/payment/plans'),
    currentMembership: (): Promise<any> => request.get('/payment/current-membership'),
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





  // SBTI
  sbti: {
    questions: (): Promise<any> => request.get('/sbti/questions'),
    submit: (answers: Array<{ question_id: number; answer: string }>): Promise<any> =>
      request.post('/sbti/submit', { answers }),
    result: (): Promise<any> => request.get('/sbti/result'),
    themeDetail: (theme: string): Promise<any> => request.get(`/sbti/themes/${theme}`),
  },

  // 依恋风格
  attachment: {
    questions: (): Promise<any> => request.get('/attachment/questions'),
    submit: (answers: Array<{ question_id: number; score: number }>): Promise<any> =>
      request.post('/attachment/submit', { answers }),
    result: (): Promise<any> => request.get('/attachment/result'),
  },

  // 深度画像
  profile: {
    deep: (): Promise<any> => request.get('/profile/deep'),
    aiPartners: (): Promise<any> => request.get('/profile/ai-partners'),
  },

  // 虚拟形象
  avatar: {
    config: (): Promise<any> => request.get('/avatar/config'),
    get: (assistantId: number): Promise<any> => request.get(`/avatar/${assistantId}`),
    animate: (data: {
      assistant_id?: number
      message?: string
      response?: string
      emotion?: string
      force_expression?: string
      force_motion?: string
    }): Promise<any> => request.post('/avatar/animate', data),
    animateForAssistant: (assistantId: number, data: {
      message?: string
      response?: string
      emotion?: string
      force_expression?: string
      force_motion?: string
    }): Promise<any> => request.post(`/avatar/animate/${assistantId}`, data),
  },

  // 每日打卡
  checkin: {
    daily: (note?: string): Promise<any> => request.post('/checkin', { note }),
    todayStatus: (): Promise<any> => request.get('/checkin/today'),
    records: (limit?: number): Promise<any> => request.get('/checkin/records', { params: { limit } }),
    stats: (): Promise<any> => request.get('/checkin/stats'),
    sharePoster: (): Promise<any> => request.get('/checkin/share/poster'),
    // 提醒
    createReminder: (data: any): Promise<any> => request.post('/checkin/reminders', data),
    reminders: (): Promise<any> => request.get('/checkin/reminders'),
    cancelReminder: (id: number): Promise<any> => request.delete(`/checkin/reminders/${id}`),
  },
}

// 导出apiClient，同时包含axios实例的方法和api对象的方法
export const apiClient = {
  ...api,
  get: request.get.bind(request),
  post: request.post.bind(request),
  put: request.put.bind(request),
  delete: request.delete.bind(request),
  patch: request.patch.bind(request),
}
