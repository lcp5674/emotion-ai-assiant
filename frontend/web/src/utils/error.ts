import { message } from 'antd'
import log from './logger'

/**
 * 全局错误处理工具
 */

// 全局错误类型
interface GlobalError extends Error {
  filename?: string
  lineno?: number
  colno?: number
  error?: Error
}

/**
 * 初始化全局错误监听
 */
export function initGlobalErrorHandler() {
  // 处理未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    event.preventDefault()
    const error = event.reason

    // 记录错误日志
    log.error('未处理的Promise错误:', error)

    // 显示错误提示
    if (error?.response?.data?.detail) {
      message.error(error.response.data.detail)
    } else if (error?.message) {
      message.error(error.message)
    } else {
      message.error('发生了一些问题，请稍后重试')
    }
  })

  // 处理全局JavaScript错误
  window.addEventListener('error', (event) => {
    const error = event.error as GlobalError

    // 记录错误日志
    log.error('全局JavaScript错误:', {
      message: error.message,
      filename: error.filename,
      lineno: error.lineno,
      colno: error.colno,
      stack: error.stack,
    })

    // 对于非关键错误，不显示提示
    if (event.message?.includes('ResizeObserver') ||
        event.message?.includes('hydration')) {
      return
    }

    // 网络资源加载错误不显示提示
    if (event.target !== window) {
      return
    }
  })
}

/**
 * 安全地执行可能出错的函数
 */
export function safeExecute<T>(
  fn: () => T,
  fallback: T,
  onError?: (error: Error) => void
): T {
  try {
    return fn()
  } catch (error) {
    log.error('执行出错:', error)
    onError?.(error as Error)
    return fallback
  }
}

/**
 * 异步安全执行
 */
export async function safeAsyncExecute<T>(
  fn: () => Promise<T>,
  fallback: T,
  onError?: (error: Error) => void
): Promise<T> {
  try {
    return await fn()
  } catch (error) {
    log.error('异步执行出错:', error)
    onError?.(error as Error)
    return fallback
  }
}

/**
 * 创建错误边界fallback
 */
export function createErrorFallback(error: Error, retry?: () => void) {
  return {
    title: '页面出错了',
    subTitle: error.message || '抱歉，发生了未知错误',
    extra: retry ? '请刷新页面重试' : undefined,
  }
}

/**
 * 格式化错误信息
 */
export function formatError(error: unknown): string {
  if (!error) return '未知错误'

  if (typeof error === 'string') return error

  if (error instanceof Error) return error.message

  // 处理API错误响应
  if (typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: string } } }).response
    if (response?.data?.detail) {
      return response.data.detail
    }
  }

  return JSON.stringify(error)
}