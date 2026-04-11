import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import EmotionShareImage from './index'
import { message } from 'antd'

// 模拟 apiClient
vi.mock('../../utils/api', () => ({
  apiClient: {
    get: vi.fn()
  }
}))

// 模拟 message
vi.mock('antd', async (importOriginal) => {
  const original = await importOriginal<typeof import('antd')>()
  return {
    ...original,
    message: {
      error: vi.fn(),
      success: vi.fn()
    },
    Button: original.Button,
    Card: original.Card,
    Spin: original.Spin
  }
})

describe('EmotionShareImage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    render(<EmotionShareImage />)
    expect(screen.getByText('正在生成分享图片...')).toBeTruthy()
  })

  it('renders error message when data fetch fails', async () => {
    const { apiClient } = await import('../../utils/api')
    apiClient.get.mockRejectedValue(new Error('Network error'))

    render(<EmotionShareImage />)
    
    expect(message.error).toHaveBeenCalledWith('获取分享数据失败')
  })

  it('renders canvas when data is loaded', async () => {
    const mockData = {
      username: 'Test User',
      time_range: 'week',
      avg_score: 8.5,
      trend_data: [],
      emotion_distribution: { happy: 10, sad: 5 },
      mood_distribution: { good: 12, bad: 3 },
      generated_at: '2026-04-11'
    }

    const { apiClient } = await import('../../utils/api')
    apiClient.get.mockResolvedValue({ data: mockData })

    render(<EmotionShareImage />)
    
    // 检查 canvas 元素是否存在
    const canvas = screen.getByRole('img')
    expect(canvas).toBeTruthy()
  })

  it('renders download button when not loading', async () => {
    const mockData = {
      username: 'Test User',
      time_range: 'week',
      avg_score: 8.5,
      trend_data: [],
      emotion_distribution: { happy: 10, sad: 5 },
      mood_distribution: { good: 12, bad: 3 },
      generated_at: '2026-04-11'
    }

    const { apiClient } = await import('../../utils/api')
    apiClient.get.mockResolvedValue({ data: mockData })

    render(<EmotionShareImage />)
    
    expect(screen.getByText('保存图片')).toBeTruthy()
  })

  it('calls downloadImage when download button is clicked', async () => {
    const mockData = {
      username: 'Test User',
      time_range: 'week',
      avg_score: 8.5,
      trend_data: [],
      emotion_distribution: { happy: 10, sad: 5 },
      mood_distribution: { good: 12, bad: 3 },
      generated_at: '2026-04-11'
    }

    const { apiClient } = await import('../../utils/api')
    apiClient.get.mockResolvedValue({ data: mockData })

    // 模拟 canvas toBlob 方法
    HTMLCanvasElement.prototype.toBlob = vi.fn((callback) => {
      callback(new Blob(['test'], { type: 'image/png' }))
    })

    // 模拟 URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test-url')

    // 模拟 a 标签点击
    const originalCreateElement = document.createElement
    document.createElement = vi.fn((tag) => {
      if (tag === 'a') {
        return {
          href: '',
          download: '',
          click: vi.fn(),
          remove: vi.fn()
        }
      }
      return originalCreateElement(tag)
    })

    render(<EmotionShareImage />)
    
    const downloadButton = screen.getByText('保存图片')
    fireEvent.click(downloadButton)
    
    expect(message.success).toHaveBeenCalledWith('图片已保存')
  })

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn()
    render(<EmotionShareImage onClose={onClose} />)
    
    const closeButton = screen.getByText('关闭')
    fireEvent.click(closeButton)
    
    expect(onClose).toHaveBeenCalled()
  })
})
