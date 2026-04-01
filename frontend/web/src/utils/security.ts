/**
 * 前端安全工具
 */

/**
 * XSS防护 - 使用简单的HTML转义
 */
export function sanitizeHtml(html: string): string {
  return html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * 验证密码强度
 * 返回密码强度等级和提示信息
 */
export function validatePassword(password: string): {
  strength: 'weak' | 'medium' | 'strong'
  valid: boolean
  message: string
} {
  if (password.length < 8) {
    return {
      strength: 'weak',
      valid: false,
      message: '密码长度至少8位',
    }
  }

  let score = 0
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumbers = /[0-9]/.test(password)
  const hasSpecialChars = /[!@#$%^&*()_+{}[\]:;<>,.?~\\-]/.test(password)

  if (hasUpperCase) score++
  if (hasLowerCase) score++
  if (hasNumbers) score++
  if (hasSpecialChars) score++
  if (password.length >= 12) score++
  if (password.length >= 16) score++

  const valid = hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChars

  if (!hasUpperCase) {
    return {
      strength: 'weak',
      valid: false,
      message: '密码必须包含大写字母',
    }
  }
  if (!hasLowerCase) {
    return {
      strength: 'weak',
      valid: false,
      message: '密码必须包含小写字母',
    }
  }
  if (!hasNumbers) {
    return {
      strength: 'weak',
      valid: false,
      message: '密码必须包含数字',
    }
  }
  if (!hasSpecialChars) {
    return {
      strength: 'weak',
      valid: false,
      message: '密码必须包含特殊字符',
    }
  }

  if (score <= 2) {
    return {
      strength: 'weak',
      valid: true,
      message: '密码强度较弱，建议使用更长更复杂的密码',
    }
  } else if (score <= 4) {
    return {
      strength: 'medium',
      valid: true,
      message: '密码强度中等',
    }
  } else {
    return {
      strength: 'strong',
      valid: true,
      message: '密码强度很高',
    }
  }
}

/**
 * 验证手机号格式
 */
export function validatePhone(phone: string): boolean {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证邮箱格式
 */
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 验证昵称格式
 */
export function validateNickname(nickname: string): { valid: boolean; message?: string } {
  if (nickname.length < 2) {
    return { valid: false, message: '昵称至少2个字符' }
  }
  if (nickname.length > 50) {
    return { valid: false, message: '昵称最多50个字符' }
  }
  if (/[<>]/.test(nickname)) {
    return { valid: false, message: '昵称不能包含特殊字符' }
  }
  return { valid: true }
}

/**
 * 转义用户输入，防止XSS
 */
export function escapeUserInput(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * 安全地解析JSON，防止原型污染
 */
export function safeJsonParse<T>(json: string, defaultValue: T): T {
  try {
    const obj = JSON.parse(json)
    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
      Object.setPrototypeOf(obj, null)
    }
    return obj as T
  } catch {
    return defaultValue
  }
}

/**
 * 生成安全的随机字符串
 */
export function generateSecureRandom(length: number = 32): string {
  const array = new Uint8Array(length)
  crypto.getRandomValues(array)
  return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * 防抖函数 - 防止重复请求
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number = 300
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 检查输入内容是否包含敏感词
 */
export function containsSensitiveWords(text: string, sensitiveWords: string[]): boolean {
  const lowerText = text.toLowerCase()
  return sensitiveWords.some((word) => lowerText.includes(word.toLowerCase()))
}
