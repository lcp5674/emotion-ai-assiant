/**
 * 情绪趋势分享图片生成组件
 * 生成可分享的情绪趋势图片，用户可以保存到相册分享
 */
import { useEffect, useRef, useState } from 'react'
import { Button, Card, Spin, message, Space } from 'antd'
import { DownloadOutlined, ShareAltOutlined } from '@ant-design/icons'
import { apiClient } from '../../api/request'
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

  // 数据更新后绘制图片
  useEffect(() => {
    if (data) {
      drawImage()
    }
  }, [data])

  const fetchShareData = async () => {
    try {
      setLoading(true)
      const res = await apiClient.get(`/diary/trend/share-image?time_range=${timeRange}`)
      setData(res)
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

    // 设置canvas尺寸 (推荐分享尺寸 1080x1620 - 更适合移动端分享)
    canvas.width = 1080
    canvas.height = 1620

    // 背景 - 温暖的渐变
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height * 0.7)
    gradient.addColorStop(0, '#f093fb')
    gradient.addColorStop(0.5, '#f5576c')
    gradient.addColorStop(1, '#4facfe')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // 底部装饰
    ctx.fillStyle = 'rgba(255,255,255,0.95)'
    ctx.beginPath()
    ctx.moveTo(0, 1200)
    ctx.bezierCurveTo(canvas.width * 0.3, 1150, canvas.width * 0.7, 1250, canvas.width, 1200)
    ctx.lineTo(canvas.width, canvas.height)
    ctx.lineTo(0, canvas.height)
    ctx.closePath()
    ctx.fill()

    // 绘制内容
    drawHeader(ctx, data)
    drawStats(ctx, data, canvas)
    drawTrendChart(ctx, data, canvas)
    drawFooter(ctx, canvas)
  }

  const drawHeader = (ctx: CanvasRenderingContext2D, data: ShareData) => {
    // 标题背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.25)'
    roundRect(ctx, 40, 40, 1000, 160, 24)
    ctx.fill()
    
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 56px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText('🌸 我的情绪月报', 80, 120)
    
    ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
    ctx.fillText(`${data.username ? data.username + ' · ' : ''}${formatTimeRange(data.time_range)}`, 80, 180)
    
    // 日期
    ctx.font = '24px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText(data.generated_at ? data.generated_at.split('T')[0] : '', 850, 180)
  }

  const drawStats = (ctx: CanvasRenderingContext2D, data: ShareData, canvas: HTMLCanvasElement) => {
    // 平均分卡片 - 白色背景
    ctx.fillStyle = '#ffffff'
    roundRect(ctx, 60, 260, 460, 240, 20)
    ctx.fill()
    
    // 彩色边框
    ctx.strokeStyle = '#ffd700'
    ctx.lineWidth = 4
    roundRect(ctx, 60, 260, 460, 240, 20)
    ctx.stroke()
    
    ctx.fillStyle = '#666666'
    ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText('平均情绪分', 100, 320)
    
    const score = Math.round(data.avg_score * 10) / 10
    ctx.fillStyle = '#333333'
    ctx.font = 'bold 72px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText(`${score}`, 100, 420)
    
    // 记录数卡片
    ctx.fillStyle = '#ffffff'
    roundRect(ctx, 560, 260, 460, 240, 20)
    ctx.fill()
    
    ctx.strokeStyle = '#87ceeb'
    ctx.lineWidth = 4
    roundRect(ctx, 560, 260, 460, 240, 20)
    ctx.stroke()
    
    const totalRecords = data.trend_data?.length || 0
    ctx.fillStyle = '#666666'
    ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText('记录天数', 600, 320)
    
    ctx.fillStyle = '#333333'
    ctx.font = 'bold 72px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText(`${totalRecords}`, 600, 420)
    ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText('天', 720, 420)
    
    // 情绪分布标题
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 36px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText('💭 情绪分布', 60, 580)
  }

  const drawTrendChart = (ctx: CanvasRenderingContext2D, data: ShareData, canvas: HTMLCanvasElement) => {
    if (!data.trend_data || data.trend_data.length === 0) return
    
    const chartY = 620
    const chartHeight = 300
    const chartWidth = 960
    const chartX = 60
    
    // 趋势图背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
    roundRect(ctx, chartX, chartY, chartWidth, chartHeight, 16)
    ctx.fill()
    
    // 绘制简易折线图
    const sortedData = [...data.trend_data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    if (sortedData.length < 2) return
    
    const maxScore = 10
    const minScore = 0
    const xStep = chartWidth / (sortedData.length - 1)
    
    // 绘制网格线
    ctx.strokeStyle = '#eeeeee'
    ctx.lineWidth = 1
    for (let i = 0; i <= 4; i++) {
      const y = chartY + 30 + (chartHeight - 60) * i / 4
      ctx.beginPath()
      ctx.moveTo(chartX + 20, y)
      ctx.lineTo(chartX + chartWidth - 20, y)
      ctx.stroke()
    }
    
    // 绘制折线
    ctx.strokeStyle = '#ff6b9d'
    ctx.lineWidth = 4
    ctx.beginPath()
    sortedData.forEach((d, i) => {
      const x = chartX + 40 + i * xStep
      const y = chartY + 30 + (chartHeight - 60) * (1 - (d.mood_score - minScore) / (maxScore - minScore))
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()
    
    // 绘制数据点和数值
    const moodEmojis = ['😢', '😔', '😐', '😊', '😄']
    sortedData.forEach((d, i) => {
      const x = chartX + 40 + i * xStep
      const y = chartY + 30 + (chartHeight - 60) * (1 - (d.mood_score - minScore) / (maxScore - minScore))
      
      // 数据点
      ctx.fillStyle = '#ff6b9d'
      ctx.beginPath()
      ctx.arc(x, y, 8, 0, Math.PI * 2)
      ctx.fill()
      
      // 数值标签
      ctx.fillStyle = '#666666'
      ctx.font = '20px "PingFang SC", "Microsoft YaHei", sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`${d.mood_score}`, x, y - 15)
      ctx.textAlign = 'left'
    })
  }

  const drawFooter = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    ctx.fillStyle = '#666666'
    ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('💜 心灵伴侣AI', canvas.width / 2, 1400)
    ctx.font = '22px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillStyle = '#999999'
    ctx.fillText('记录每一天，成为更好的自己', canvas.width / 2, 1440)
    ctx.textAlign = 'left'
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
