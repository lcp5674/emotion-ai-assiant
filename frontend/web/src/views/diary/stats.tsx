import { useEffect, useState, useRef } from 'react'
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
  Modal,
} from 'antd'
import {
  SmileOutlined,
  CalendarOutlined,
  ArrowLeftOutlined,
  PieChartOutlined,
  ShareAltOutlined,
} from '@ant-design/icons'
import EmotionShareImage from '../../components/ShareImage'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import dayjs from 'dayjs'
import * as d3 from 'd3'

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

  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter' | 'year'>('month')
  const [loading, setLoading] = useState(true)
  const [shareModalVisible, setShareModalVisible] = useState(false)
  const moodTrendRef = useRef<HTMLDivElement>(null)
  const emotionPieRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadData()
  }, [timeRange])

  useEffect(() => {
    if (!loading && trend && trend.trend_data && moodTrendRef.current) {
      renderMoodTrend()
    }
    if (!loading && trend && trend.emotion_distribution && emotionPieRef.current) {
      renderEmotionPie()
    }
  }, [loading, trend])

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

  const renderMoodTrend = () => {
    if (!moodTrendRef.current || !trend.trend_data || trend.trend_data.length === 0) return

    // Clear existing
    d3.select(moodTrendRef.current).selectAll('*').remove()

    const width = moodTrendRef.current.clientWidth
    const height = 200
    const margin = { top: 20, right: 20, bottom: 30, left: 40 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3.select(moodTrendRef.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const data = trend.trend_data.sort((a, b) => dayjs(a.date).valueOf() - dayjs(b.date).valueOf())

    const x = d3.scaleTime()
      .domain(d3.extent(data, d => dayjs(d.date).valueOf()) as [number, number])
      .range([0, innerWidth])

    const y = d3.scaleLinear()
      .domain([0, 10])
      .range([innerHeight, 0])

    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat(d => dayjs(d.valueOf()).format('MM-DD')))

    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5))

    // Add line
    const line = d3.line<typeof data[0]>()
      .x(d => x(dayjs(d.date).valueOf()))
      .y(d => y(d.mood_score))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#722ed1')
      .attr('stroke-width', 2)
      .attr('d', line)

    // Add dots with color based on mood
    const getMoodColor = (score: number) => {
      if (score >= 8) return '#52c41a'
      if (score >= 6) return '#faad14'
      if (score >= 4) return '#fa8c16'
      return '#ff4d4f'
    }

    g.selectAll('.dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => x(dayjs(d.date).valueOf()))
      .attr('cy', d => y(d.mood_score))
      .attr('r', 4)
      .attr('fill', d => getMoodColor(d.mood_score))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
  }

  const renderEmotionPie = () => {
    if (!emotionPieRef.current || !trend.emotion_distribution) return

    // Clear existing
    d3.select(emotionPieRef.current).selectAll('*').remove()

    const width = 300
    const height = 300
    const radius = Math.min(width, height) / 2

    const svg = d3.select(emotionPieRef.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`)

    const colorMap: Record<string, string> = {
      happy: '#52c41a',
      excited: '#faad14',
      calm: '#1890ff',
      neutral: '#8c8c8c',
      sad: '#722ed1',
      anxious: '#fa8c16',
      angry: '#ff4d4f',
      confused: '#fa8c16',
      surprised: '#13c2c2',
    }

    const data = Object.entries(trend.emotion_distribution).map(([key, value]) => ({
      emotion: key,
      count: value as number,
      color: colorMap[key] || '#8c8c8c',
    })).filter(d => d.count > 0)

    if (data.length === 0) return

    const pie = d3.pie<typeof data[0]>()
      .value(d => d.count)
      .sort(null)

    const arc = d3.arc<d3.PieArcDatum<typeof data[0]>>()
      .outerRadius(radius - 10)
      .innerRadius(radius - 70)

    const labelArc = d3.arc<d3.PieArcDatum<typeof data[0]>>()
      .outerRadius(radius)
      .innerRadius(radius - 40)

    // Add arcs
    const arcs = svg.selectAll('.arc')
      .data(pie(data))
      .enter()
      .append('g')
      .attr('class', 'arc')

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => d.data.color)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    // Add labels
    const getEmotionName = (emotion: string) => {
      const names: Record<string, string> = {
        happy: '开心',
        sad: '悲伤',
        angry: '愤怒',
        calm: '平静',
        excited: '兴奋',
        anxious: '焦虑',
        confused: '困惑',
        surprised: '惊讶',
        neutral: '平静',
      }
      return names[emotion] || emotion
    }

    arcs.append('text')
      .attr('transform', d => `translate(${labelArc.centroid(d)})`)
      .attr('dy', '.35em')
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#fff')
      .text(d => getEmotionName(d.data.emotion))
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
            <Button
              type="primary"
              icon={<ShareAltOutlined />}
              onClick={() => setShareModalVisible(true)}
              disabled={!trend || !trend.trend_data || trend.trend_data.length === 0}
            >
              生成分享图
            </Button>
            <Link to="/diary">
              <Button icon={<ArrowLeftOutlined />}>回到列表</Button>
            </Link>
          </Space>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.total_count}
              </div>
              <div style={{ color: '#8c8c8c' }}>总记录</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.current_streak}天
              </div>
              <div style={{ color: '#8c8c8c' }}>连续记录</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.max_streak}天
              </div>
              <div style={{ color: '#8c8c8c' }}>最长连续</div>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.avg_mood.toFixed(1)}
              </div>
              <div style={{ color: '#8c8c8c' }}>平均心情</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats.avg_words_per_day.toFixed(0)}
              </div>
              <div style={{ color: '#8c8c8c' }}>平均字数</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
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
          <div ref={moodTrendRef} style={{ height: 200, width: '100%' }}>
            {(!trend.trend_data || trend.trend_data.length === 0) && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Empty description="暂无足够数据生成趋势图" />
              </div>
            )}
          </div>
        </Card>

        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={12}>
            {/* 情绪分布饼图 */}
            <Card>
              <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <PieChartOutlined />
                情绪占比 ({formatTimeRange(timeRange)})
              </h3>
              <div ref={emotionPieRef} style={{ display: 'flex', justifyContent: 'center' }}>
                {Object.keys(trend.emotion_distribution).filter(k => trend.emotion_distribution[k] > 0).length === 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
                    <Empty description="暂无足够数据生成图表" />
                  </div>
                )}
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            {/* 情绪分布卡片 */}
            <Card>
              <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <SmileOutlined />
                情绪统计 ({formatTimeRange(timeRange)})
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                {Object.entries(trend.emotion_distribution).filter(([_, count]) => count > 0).map(([emotion, count]) => (
                  <Card
                    key={emotion}
                    size="small"
                    style={{
                      minWidth: 100,
                      textAlign: 'center',
                      flex: 1,
                    }}
                  >
                    <div style={{ fontSize: 28, marginBottom: 4 }}>
                      {getEmotionIcon(emotion)}
                    </div>
                    <div style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 4 }}>
                      {emotion === 'happy' && '开心'}
                      {emotion === 'sad' && '悲伤'}
                      {emotion === 'angry' && '愤怒'}
                      {emotion === 'calm' && '平静'}
                      {emotion === 'excited' && '兴奋'}
                      {emotion === 'anxious' && '焦虑'}
                      {emotion === 'confused' && '困惑'}
                      {emotion === 'surprised' && '惊讶'}
                    </div>
                    <div style={{ fontSize: 18, fontWeight: 'bold', color: '#722ed1' }}>
                      {count}次
                    </div>
                  </Card>
                ))}
              </div>
            </Card>
          </Col>
        </Row>

        {/* 心情等级分布 */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>心情等级分布</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            {Object.entries(trend.mood_distribution).filter(([_, count]) => count > 0).map(([level, count]) => (
              <Card
                key={level}
                style={{
                  minWidth: 120,
                  textAlign: 'center',
                  flex: 1,
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
        {Object.keys(stats.categories).length > 0 && (
          <Card style={{ marginBottom: 24 }}>
            <h3 style={{ marginBottom: 16 }}>分类统计</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
              {Object.entries(stats.categories).filter(([_, count]) => count > 0).map(([category, count]) => (
                <Card
                  key={category}
                  style={{
                    minWidth: 120,
                    textAlign: 'center',
                    flex: 1,
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
        )}
      </div>

      {/* 分享图片弹窗 */}
      <Modal
        title="情绪趋势分享"
        open={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        <EmotionShareImage timeRange={timeRange} onClose={() => setShareModalVisible(false)} />
      </Modal>
    </div>
  )
}
