/**
 * 情绪趋势分享图片生成组件
 * 生成可分享的情绪趋势图片，用户可以保存到相册分享
 */
import { useEffect, useRef, useState } from 'react'
import { Button, Card, Spin, message, Space } from 'antd'
import { DownloadOutlined, ShareAltOutlined } from '@ant-design/icons'
import { apiClient } from '../../utils/api'
import './index.css'

interface ShareImageProps {
  timeRange?: 'week' | 'month' | 'quarter' | 'year'
  onClose?: () => void
}

interface ShareData {
  username: string
  time_range: string
  avg_score: number
  trend_data: any[]
  emotion_distribution: Record<string, number>
  mood_distribution: Record<string, number>
  generated_at: string
}

export default function EmotionShareImage({ timeRange = 'week', onClose }: ShareImageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<ShareData | null>(null)

  useEffect(() => {
    fetchShareData()
  }, [timeRange])

  const fetchShareData = async () => {
    try {
      const res = await apiClient.get(`/diary/trend/share-image?time_range=${timeRange}`)
      setData(res.data)
      drawImage()
    } catch (error) {
      console.error('获取分享数据失败', error)
      message.error('获取分享数据失败')
    } finally {
      setLoading(false)
    }
  }

  const drawImage = () => {
    if (!canvasRef.current || !data) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 设置canvas尺寸 (推荐分享尺寸 1080x1920)
    canvas.width = 1080
    canvas.height = 1920

    // 背景渐变
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
    gradient.addColorStop(0, '#667eea')
    gradient.addColorStop(1, '#764ba2')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // 绘制内容
    drawHeader(ctx, data)
    drawStats(ctx, data, canvas)
    drawFooter(ctx, canvas)
  }

  const drawHeader = (ctx: CanvasRenderingContext2D, data: ShareData) => {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 64px sans-serif'
    ctx.fillText('我的情绪月报', 80, 120)
    
    ctx.font = '32px sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)'
    ctx.fillText(`${data.username} · ${formatTimeRange(data.time_range)}`, 80, 180)
  }

  const drawStats = (ctx: CanvasRenderingContext2D, data: ShareData, canvas: HTMLCanvasElement) => {
    // 平均分卡片
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
    roundRect(ctx, 60, 220, canvas.width - 120, 200, 16)
    ctx.fill()

    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 48px sans-serif'
    ctx.fillText('平均情绪分', 100, 300)
    
    const score = Math.round(data.avg_score * 10) / 10
    ctx.font = 'bold 80px sans-serif'
    ctx.fillText(`${score}`, 100, 380)

    // 情绪分布
    let y = 480
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 48px sans-serif'
    ctx.fillText('情绪分布', 80, y)
    y += 60

    Object.entries(data.emotion_distribution).forEach(([emotion, count]) => {
      const barWidth = 860
      const maxCount = Math.max(...Object.values(data.emotion_distribution))
      const ratio = count / maxCount
      const currentWidth = barWidth * ratio

      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
      roundRect(ctx, 80, y - 30, barWidth, 40, 8)
      ctx.fill()

      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
      ctx.fillRect(80, y - 30, currentWidth, 40)

      ctx.font = '28px sans-serif'
      ctx.fillText(`${emotion} (${count})`, 100, y)
      y += 60
    })
  }

  const drawFooter = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.font = '32px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('生成于情感AI助手', canvas.width / 2, canvas.height - 80)
    ctx.font = '24px sans-serif'
    ctx.fillText('记录每一天，成为更好的自己', canvas.width / 2, canvas.height - 40)
  }

  // 绘制圆角矩形
  const roundRect = (
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    radius: number
  ) => {
    ctx.beginPath()
    ctx.moveTo(x + radius, y)
    ctx.lineTo(x + width - radius, y)
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
    ctx.lineTo(x + width, y + height - radius)
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
    ctx.lineTo(x + radius, y + height)
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
    ctx.lineTo(x, y + radius)
    ctx.quadraticCurveTo(x, y, x + radius, y)
    ctx.closePath()
  }

  const formatTimeRange = (range: string) => {
    const map: Record<string, string> = {
      week: '本周',
      month: '本月',
      quarter: '本季度',
      year: '本年度',
    }
    return map[range] || range
  }

  const downloadImage = () => {
    if (!canvasRef.current) return

    canvasRef.current.toBlob((blob) => {
      if (!blob) {
        message.error('生成图片失败')
        return
      }

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `emotion-mood-${timeRange}-${Date.now()}.png`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      message.success('图片已保存')
    }, 'image/png')
  }

  const shareImage = async () => {
    if (!canvasRef.current) return

    canvasRef.current.toBlob(async (blob) => {
      if (!blob) {
        message.error('生成图片失败')
        return
      }

      const file = new File([blob], `emotion-mood-${timeRange}.png`, { type: 'image/png' })

      if (navigator.share) {
        try {
          await navigator.share({
            files: [file],
            title: '我的情绪变化',
            text: '来情感AI助手记录你的情绪变化'
          })
        } catch (error) {
          console.log('分享取消', error)
        }
      } else {
        downloadImage()
      }
    }, 'image/png')
  }

  return (
    <div className="share-image-container">
      <Card title="情绪趋势分享" extra={onClose && <Button onClick={onClose}>关闭</Button>}>
        <div className="canvas-wrapper">
          {loading && (
            <div className="loading-wrapper">
              <Spin size="large" />
              <div>正在生成分享图片...</div>
            </div>
          )}
          <canvas
            ref={canvasRef}
            className="share-canvas"
            style={{ display: loading ? 'none' : 'block' }}
          />
        </div>
        {!loading && (
          <div className="share-actions">
            <Space>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={downloadImage}
              >
                保存图片
              </Button>
              {navigator.share && (
                <Button icon={<ShareAltOutlined />} onClick={shareImage}>
                  分享
                </Button>
              )}
            </Space>
          </div>
        )}
      </Card>
    </div>
  )
}
