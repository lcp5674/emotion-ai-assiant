import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Card,
  Row,
  Col,
  Spin,
  Empty,
  Select,
  App,
  Space,
  Button,
} from 'antd'
import {
  SmileOutlined,
  CalendarOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import dayjs from 'dayjs'

const { Option } = Select

interface TrendData {
  date: string
  mood_score: number
  mood_level?: string
  primary_emotion?: string
  count: number
}

export default function DiaryStats() {
  const { message } = App.useApp()
  const {
    stats,
    trend,
    setStats,
    setTrend,
  } = useDiaryStore()

  const [timeRange, setTimeRange] = useState('month') // week/month/quarter/year
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [timeRange])

  const loadData = async () => {
    setLoading(true)
    try {
      // 同时加载统计和趋势数据
      const [statsRes, trendRes] = await Promise.all([
        api.diary.stats(),
        api.diary.trend(timeRange),
      ])
      setStats(statsRes)
      setTrend(trendRes)
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const getMoodIcon = (moodScore: number) => {
    if (moodScore >= 8) return <SmileOutlined style={{ color: '#52c41a' }} />
    if (moodScore >= 6) return <SmileOutlined style={{ color: '#faad14' }} />
    if (moodScore >= 4) return <SmileOutlined style={{ color: '#fa8c16' }} />
    return <SmileOutlined style={{ color: '#ff4d4f' }} />
  }

  const getMoodColor = (moodScore: number) => {
    if (moodScore >= 8) return 'success'
    if (moodScore >= 6) return 'warning'
    if (moodScore >= 4) return 'orange'
    return 'error'
  }

  const getEmotionIcon = (emotion: string) => {
    const emotionMap: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      calm: '😌',
      excited: '🎉',
      anxious: '😰',
      confused: '😕',
      surprised: '😮',
    }
    return emotionMap[emotion] || '😐'
  }

  const formatTimeRange = (range: string) => {
    const map: Record<string, string> = {
      week: '最近一周',
      month: '最近一月',
      quarter: '最近三月',
      year: '最近一年',
    }
    return map[range] || '最近一月'
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!stats || !trend) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Empty description="暂无数据" />
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        background: '#fff',
        padding: '16px 0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/" style={{ fontSize: 20, color: '#722ed1', fontWeight: 'bold' }}>
            心灵伴侣AI
          </Link>
          <Space>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 120 }}
            >
              <Option value="week">最近一周</Option>
              <Option value="month">最近一月</Option>
              <Option value="quarter">最近三月</Option>
              <Option value="year">最近一年</Option>
            </Select>
            <Link to="/diary">
              <Button icon={<ArrowLeftOutlined />}>回到列表</Button>
            </Link>
          </Space>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.total_count}
              </div>
              <div style={{ color: '#8c8c8c' }}>总记录</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.current_streak}天
              </div>
              <div style={{ color: '#8c8c8c' }}>连续记录</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.max_streak}天
              </div>
              <div style={{ color: '#8c8c8c' }}>最长连续</div>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.avg_mood.toFixed(1)}
              </div>
              <div style={{ color: '#8c8c8c' }}>平均心情</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.avg_words_per_day.toFixed(0)}
              </div>
              <div style={{ color: '#8c8c8c' }}>平均字数</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.this_month_count}
              </div>
              <div style={{ color: '#8c8c8c' }}>本月记录</div>
            </Card>
          </Col>
        </Row>

        {/* 心情趋势图 */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <CalendarOutlined />
            心情趋势 ({formatTimeRange(timeRange)})
          </h3>
          <div style={{ height: 200 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Empty description="图表功能开发中" />
            </div>
          </div>
        </Card>

        {/* 情绪分布 */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <SmileOutlined />
            情绪分布 ({formatTimeRange(timeRange)})
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            {Object.entries(trend.emotion_distribution).map(([emotion, count]) => (
              <Card
                key={emotion}
                style={{
                  minWidth: 120,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 24 }}>
                  {getEmotionIcon(emotion)}
                </div>
                <div style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 8 }}>
                  {emotion}
                </div>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#722ed1' }}>
                  {count}次
                </div>
              </Card>
            ))}
          </div>
        </Card>

        {/* 心情等级分布 */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>心情等级分布</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            {Object.entries(trend.mood_distribution).map(([level, count]) => (
              <Card
                key={level}
                style={{
                  minWidth: 120,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 8 }}>
                  {level === 'terrible' && '糟糕'}
                  {level === 'bad' && '不好'}
                  {level === 'neutral' && '一般'}
                  {level === 'good' && '不错'}
                  {level === 'excellent' && '很棒'}
                </div>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#722ed1' }}>
                  {count}次
                </div>
              </Card>
            ))}
          </div>
        </Card>

        {/* 分类统计 */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>分类统计</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            {Object.entries(stats.categories).map(([category, count]) => (
              <Card
                key={category}
                style={{
                  minWidth: 120,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 8 }}>
                  {category}
                </div>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#722ed1' }}>
                  {count}次
                </div>
              </Card>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
