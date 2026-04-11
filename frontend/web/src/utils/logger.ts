/**
 * 简单的日志工具
 * 生产环境可替换为专业的日志服务
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

const currentLevel = import.meta.env.DEV ? 'debug' : 'warn'

function shouldLog(level: LogLevel): boolean {
  return LOG_LEVELS[level] >= LOG_LEVELS[currentLevel as LogLevel]
}

function formatMessage(level: LogLevel, ...args: unknown[]): string {
  const timestamp = new Date().toISOString()
  return `[${timestamp}] [${level.toUpperCase()}] ${args.map(a =>
    typeof a === 'object' ? JSON.stringify(a) : String(a)
  ).join(' ')}`
}

export default {
  debug(...args: unknown[]) {
    if (shouldLog('debug')) {
      console.debug(formatMessage('debug', ...args))
    }
  },

  info(...args: unknown[]) {
    if (shouldLog('info')) {
      console.info(formatMessage('info', ...args))
    }
  },

  warn(...args: unknown[]) {
    if (shouldLog('warn')) {
      console.warn(formatMessage('warn', ...args))
    }
  },

  error(...args: unknown[]) {
    if (shouldLog('error')) {
      console.error(formatMessage('error', ...args))
    }
  },
}