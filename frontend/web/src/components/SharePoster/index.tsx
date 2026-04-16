/**
 * 分享海报生成组件
 * 支持多种场景：打卡成就、情绪月报、测评结果等
 */
import { useEffect, useRef, useState } from 'react'
import { Button, Card, Spin, message, Space, Segmented } from 'antd'
import { DownloadOutlined, ShareAltOutlined } from '@ant-design/icons'
import { apiClient } from '../../api/request'
import './index.css'

interface SharePosterProps {
  type?: 'checkin' | 'diary' | 'achievement'
  onClose?: () => void
}

interface CheckInShareData {
  username: string
  total_checkins: number
  current_streak: number
  max_streak: number
  total_xp_earned: number
  generated_at: string
}

interface DiaryShareData {
  username: string
  time_range: string
  avg_score: number
  trend_data: any[]
  emotion_distribution: Record<string, number>
  mood_distribution: Record<string, number>
  generated_at: string
}

interface AchievementShareData {
  username: string
  level: number
  total_badges: number
  unlocked_badges: number
  generated_at: string
}

type ShareData = CheckInShareData | DiaryShareData | AchievementShareData

export default function SharePoster({ type = 'checkin', onClose }: SharePosterProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<ShareData | null>(null)
  const [posterType, setPosterType] = useState<'checkin' | 'diary' | 'achievement'>(type)

  useEffect(() => {
    fetchShareData()
  }, [posterType])

  const fetchShareData = async () => {
    setLoading(true)
    try {
      let endpoint = ''
      switch (posterType) {
        case 'checkin':
          endpoint = '/checkin/share/poster'
          break
        case 'diary':
          endpoint = '/diary/trend/share-image'
          break
        case 'achievement':
          endpoint = '/growth/overview'
          break
      }
      const res = await apiClient.get(endpoint)
      setData(res.data || res)
      drawPoster()
    } catch (error) {
      console.error('获取分享数据失败', error)
      message.error('获取分享数据失败')
    } finally {
      setLoading(false)
    }
  }

  const drawPoster = () => {
    if (!canvasRef.current || !data) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 设置canvas尺寸 (推荐分享尺寸 1080x1920)
    canvas.width = 1080
    canvas.height = 1920

    // 根据类型选择配色
    const colorSchemes: Record<string, { gradient: string[]; accent: string }> = {
      checkin: { gradient: ['#fa8c16', '#faad14'], accent: '#fff' },
      diary: { gradient: ['#667eea', '#764ba2'], accent: '#fff' },
      achievement: { gradient: ['#722ed1', '#b37feb'], accent: '#fff' },
    }

    const colors = colorSchemes[posterType] || colorSchemes.diary

    // 背景渐变
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
    gradient.addColorStop(0, colors.gradient[0])
    gradient.addColorStop(1, colors.gradient[1])
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // 绘制装饰元素
    drawDecorations(ctx, canvas, colors)

    // 绘制内容
    if (posterType === 'checkin') {
      drawCheckinContent(ctx, data as CheckInShareData, canvas)
    } else if (posterType === 'diary') {
      drawDiaryContent(ctx, data as DiaryShareData, canvas)
    } else if (posterType === 'achievement') {
      drawAchievementContent(ctx, data as AchievementShareData, canvas)
    }

    drawFooter(ctx, canvas)
  }

  const drawDecorations = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement, colors: { gradient: string[]; accent: string }) => {
    // 左上角装饰圆
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.beginPath()
    ctx.arc(0, 0, 300, 0, Math.PI * 2)
    ctx.fill()

    // 右下角装饰圆
    ctx.fillStyle = 'rgba(255, 255, 255, 0.08)'
    ctx.beginPath()
    ctx.arc(canvas.width, canvas.height, 400, 0, Math.PI * 2)
    ctx.fill()

    // 顶部横条装饰
    ctx.fillStyle = 'rgba(255, 255, 255, 0.05)'
    ctx.fillRect(0, 200, canvas.width, 2)
  }

  const drawCheckinContent = (ctx: CanvasRenderingContext2D, data: CheckInShareData, canvas: HTMLCanvasElement) => {
    // 标题
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 56px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('我的打卡成就', canvas.width / 2, 280)

    // 用户名
    ctx.font = '32px sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.fillText(data.username, canvas.width / 2, 340)

    // 打卡天数卡片
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
    roundRect(ctx, 80, 400, canvas.width - 160, 280, 24)
    ctx.fill()

    // 连续打卡天数
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 120px sans-serif'
    ctx.fillText(`${data.current_streak}`, canvas.width / 2, 560)
    ctx.font = '36px sans-serif'
    ctx.fillText('连续打卡天数', canvas.width / 2, 620)

    // 统计数据
    const stats = [
      { label: '总打卡', value: data.total_checkins },
      { label: '最高连续', value: data.max_streak },
      { label: '累计经验', value: data.total_xp_earned },
    ]

    let x = 120
    stats.forEach((stat) => {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
      roundRect(ctx, x - 60, 720, 280, 160, 16)
      ctx.fill()

      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
      ctx.font = 'bold 48px sans-serif'
      ctx.fillText(`${stat.value}`, x + 80, 800)
      ctx.font = '28px sans-serif'
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
      ctx.fillText(stat.label, x + 80, 850)

      x += 320
    })
  }

  const drawDiaryContent = (ctx: CanvasRenderingContext2D, data: DiaryShareData, canvas: HTMLCanvasElement) => {
    // 标题
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 56px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('我的情绪月报', canvas.width / 2, 280)

    // 用户名和时间范围
    ctx.font = '32px sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.fillText(`${data.username} · ${formatTimeRange(data.time_range)}`, canvas.width / 2, 340)

    // 平均分卡片
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
    roundRect(ctx, 80, 400, canvas.width - 160, 200, 24)
    ctx.fill()

    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 48px sans-serif'
    ctx.fillText('平均情绪分', 120, 480)

    const score = Math.round(data.avg_score * 10) / 10
    ctx.font = 'bold 100px sans-serif'
    ctx.fillText(`${score}`, 120, 580)

    // 情绪分布
    let y = 680
    ctx.font = 'bold 40px sans-serif'
    ctx.fillText('情绪分布', 80, y)
    y += 60

    Object.entries(data.emotion_distribution).forEach(([emotion, count]) => {
      const barWidth = 880
      const maxCount = Math.max(...Object.values(data.emotion_distribution))
      const ratio = count / maxCount
      const currentWidth = barWidth * ratio

      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
      roundRect(ctx, 80, y - 30, barWidth, 50, 12)
      ctx.fill()

      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
      ctx.fillRect(80, y - 30, currentWidth, 50)

      ctx.font = '28px sans-serif'
      ctx.fillText(`${emotion} (${count})`, 100, y + 5)
      y += 80
    })
  }

  const drawAchievementContent = (ctx: CanvasRenderingContext2D, data: AchievementShareData, canvas: HTMLCanvasElement) => {
    // 标题
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 56px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('我的成长成就', canvas.width / 2, 280)

    // 用户名
    ctx.font = '32px sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.fillText(data.username, canvas.width / 2, 340)

    // 等级卡片
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
    roundRect(ctx, 80, 400, canvas.width - 160, 300, 24)
    ctx.fill()

    // 等级
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.font = 'bold 140px sans-serif'
    ctx.fillText(`Lv.${data.level}`, canvas.width / 2, 600)

    // 徽章统计
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
    roundRect(ctx, 80, 750, canvas.width - 160, 160, 16)
    ctx.fill()

    ctx.font = '36px sans-serif'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.fillText(`已解锁 ${data.unlocked_badges} / ${data.total_badges} 枚徽章`, canvas.width / 2, 850)
  }

  const drawFooter = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)'
    ctx.font = '32px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('生成于情感AI助手', canvas.width / 2, canvas.height - 80)
    ctx.font = '24px sans-serif'
    ctx.fillText('记录每一天，成为更好的自己', canvas.width / 2, canvas.height - 40)
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
      a.download = `share-poster-${posterType}-${Date.now()}.png`
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

      const file = new File([blob], `share-poster-${posterType}.png`, { type: 'image/png' })

      if (navigator.share) {
        try {
          await navigator.share({
            files: [file],
            title: '我的成长记录',
            text: '来情感AI助手记录你的成长足迹'
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
    <div className="share-poster-container">
      <Card
        title="生成分享海报"
        extra={onClose && <Button onClick={onClose}>关闭</Button>}
      >
        <div style={{ marginBottom: 16 }}>
          <Segmented
            value={posterType}
            onChange={(value) => setPosterType(value as typeof posterType)}
            options={[
              { label: '打卡成就', value: 'checkin' },
              { label: '情绪月报', value: 'diary' },
              { label: '成长徽章', value: 'achievement' },
            ]}
          />
        </div>

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
          <div className="share-actions" style={{ marginTop: 16 }}>
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
