import { useEffect, useState, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  Card,
  Row,
  Col,
  Spin,
  Empty,
  Select,
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
  FireOutlined,
  ReadOutlined,
  FieldTimeOutlined,
} from '@ant-design/icons'
import EmotionShareImage from '../../components/ShareImage'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import { useTheme } from '../../hooks/useTheme'
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

// 动画计数器Hook
function useAnimatedNumber(value: number, duration: number = 1500) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    let startTime: number
    let animationFrame: number

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)

      // 使用 easeOutExpo 缓动
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      setDisplayValue(Math.round(easeProgress * value))

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])

  return displayValue
}

// 统计卡片组件
const StatCard: React.FC<{
  icon: React.ReactNode
  value: number
  label: string
  color: string
  suffix?: string
}> = ({ icon, value, label, color, suffix = '' }) => {
  const animatedValue = useAnimatedNumber(value)

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: 20,
        padding: '28px 20px',
        textAlign: 'center',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        border: '1px solid #f0f0f0',
        transition: 'all 0.3s ease',
        cursor: 'default',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = `0 8px 30px ${color}20`
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.06)'
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          background: `${color}15`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          fontSize: 24,
          color: color,
        }}
      >
        {icon}
      </div>
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          color: '#1f2937',
          lineHeight: 1,
          marginBottom: 8,
          fontFamily: 'Inter, sans-serif',
        }}
      >
        {animatedValue}
        {suffix && <span style={{ fontSize: 18, color: '#6b7280' }}>{suffix}</span>}
      </div>
      <div
        style={{
          fontSize: 14,
          color: '#9ca3af',
        }}
      >
        {label}
      </div>
    </div>
  )
}

export default function DiaryStats() {
  const {
    stats,
    trend,
    setStats,
    setTrend,
  } = useDiaryStore()
  const { themeColor, themeColors } = useTheme()

  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter' | 'year'>('month')
  const [loading, setLoading] = useState(true)
  const [shareModalVisible, setShareModalVisible] = useState(false)
  const [chartKey, setChartKey] = useState(0)
  const moodTrendRef = useRef<HTMLDivElement>(null)
  const emotionPieRef = useRef<HTMLDivElement>(null)

  // timeRange 变化时，强制图表重新渲染并加载新数据
  useEffect(() => {
    setChartKey(prev => prev + 1)
    loadData()
  }, [timeRange])

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [statsRes, trendRes] = await Promise.all([
        api.diary.stats(timeRange),
        api.diary.trend(timeRange),
      ])
      setStats(statsRes)
      setTrend(trendRes)
    } catch (error: any) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }, [timeRange, setStats, setTrend])

  useEffect(() => {
    if (!loading && trend && trend.trend_data && moodTrendRef.current) {
      renderMoodTrend()
    }
    if (!loading && trend && trend.emotion_distribution && emotionPieRef.current) {
      renderEmotionPie()
    }
  }, [loading, trend])

  const renderMoodTrend = () => {
    if (!moodTrendRef.current || !trend.trend_data || trend.trend_data.length === 0) return

    d3.select(moodTrendRef.current).selectAll('*').remove()

    const containerWidth = moodTrendRef.current.clientWidth
    const width = containerWidth
    const height = 300
    const margin = { top: 30, right: 30, bottom: 50, left: 60 }
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

    // 添加网格线
    g.append('g')
      .attr('class', 'grid')
      .attr('opacity', 0.1)
      .call(d3.axisLeft(y).ticks(5).tickSize(-innerWidth).tickFormat(() => ''))

    // X轴
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).ticks(6).tickFormat(d => dayjs(d.valueOf()).format('MM-DD')))
      .selectAll('text')
      .attr('fill', '#9ca3af')
      .attr('font-size', '12px')

    // Y轴 - 显示心情含义
    const moodLabels = ['很糟', '不太好', '一般', '不错', '很棒']
    const moodLabelPositions = [0, 2.5, 5, 7.5, 10]

    g.append('g')
      .call(d3.axisLeft(y).tickFormat((d) => {
        const val = d as number
        if (val <= 2) return moodLabels[0]
        if (val <= 4) return moodLabels[1]
        if (val <= 6) return moodLabels[2]
        if (val <= 8) return moodLabels[3]
        return moodLabels[4]
      }).ticks(5))
      .selectAll('text')
      .attr('fill', '#6b7280')
      .attr('font-size', '12px')
      .attr('font-weight', '500')

    // 渐变填充
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'areaGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%')

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', themeColors[themeColor])
      .attr('stop-opacity', 0.4)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', themeColors[themeColor])
      .attr('stop-opacity', 0.05)

    // 面积
    const area = d3.area<typeof data[0]>()
      .x(d => x(dayjs(d.date).valueOf()))
      .y0(innerHeight)
      .y1(d => y(d.mood_score))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(data)
      .attr('fill', 'url(#areaGradient)')
      .attr('d', area)

    // 线条
    const line = d3.line<typeof data[0]>()
      .x(d => x(dayjs(d.date).valueOf()))
      .y(d => y(d.mood_score))
      .curve(d3.curveMonotoneX)

    const path = g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', themeColors[themeColor])
      .attr('stroke-width', 3)
      .attr('stroke-linecap', 'round')
      .attr('d', line)

    // 线条动画
    const totalLength = path.node()?.getTotalLength() || 0
    path
      .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
      .attr('stroke-dashoffset', totalLength)
      .transition()
      .duration(2000)
      .ease(d3.easeQuadOut)
      .attr('stroke-dashoffset', 0)

    // 颜色映射
    const getMoodColor = (score: number) => {
      if (score >= 8) return '#22c55e'
      if (score >= 6) return '#84cc16'
      if (score >= 4) return '#fbbf24'
      return '#ef4444'
    }

    // 添加数据点
    g.selectAll('.dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => x(dayjs(d.date).valueOf()))
      .attr('cy', d => y(d.mood_score))
      .attr('r', 0)
      .attr('fill', d => getMoodColor(d.mood_score))
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 3)
      .transition()
      .delay((_, i) => 2000 + i * 50)
      .duration(300)
      .attr('r', 6)

    // 添加数据点悬停效果
    g.selectAll('.dot-hover')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => x(dayjs(d.date).valueOf()))
      .attr('cy', d => y(d.mood_score))
      .attr('r', 15)
      .attr('fill', 'transparent')
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        // 获取心情含义
        const score = d.mood_score
        let moodLabel = ''
        if (score <= 2) moodLabel = '很糟'
        else if (score <= 4) moodLabel = '不太好'
        else if (score <= 6) moodLabel = '一般'
        else if (score <= 8) moodLabel = '不错'
        else moodLabel = '很棒'

        d3.select(this.parentNode)
          .append('text')
          .attr('class', 'tooltip')
          .attr('x', x(dayjs(d.date).valueOf()))
          .attr('y', y(d.mood_score) - 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('font-weight', '600')
          .attr('fill', '#374151')
          .text(`${d.mood_score.toFixed(1)}分 (${moodLabel})`)
      })
      .on('mouseout', function() {
        d3.select(this.parentNode).selectAll('.tooltip').remove()
      })
  }

  const renderEmotionPie = () => {
    if (!emotionPieRef.current || !trend.emotion_distribution) return

    d3.select(emotionPieRef.current).selectAll('*').remove()

    const containerWidth = emotionPieRef.current.clientWidth
    const margin = { top: 10, right: 80, bottom: 10, left: 60 }
    const width = containerWidth - margin.left - margin.right
    const barHeight = 36
    const barGap = 12
    const height = Object.keys(trend.emotion_distribution).filter(k => (trend.emotion_distribution as any)[k] > 0).length * (barHeight + barGap)
    const innerHeight = height

    const svg = d3.select(emotionPieRef.current)
      .append('svg')
      .attr('width', containerWidth)
      .attr('height', innerHeight + margin.top + margin.bottom)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const colorMap: Record<string, string> = {
      happy: '#22c55e',
      excited: '#fbbf24',
      calm: '#3b82f6',
      neutral: '#9ca3af',
      sad: '#8b5cf6',
      anxious: '#f97316',
      angry: '#ef4444',
      confused: '#ec4899',
      surprised: '#06b6d4',
    }

    const emotionNames: Record<string, string> = {
      happy: '😊 开心',
      sad: '😢 悲伤',
      angry: '😠 愤怒',
      calm: '😌 平静',
      excited: '🎉 兴奋',
      anxious: '😰 焦虑',
      confused: '😕 困惑',
      surprised: '😮 惊讶',
      neutral: '😐 中性',
    }

    const data = Object.entries(trend.emotion_distribution)
      .map(([key, value]) => ({
        emotion: key,
        count: value as number,
        color: colorMap[key] || '#9ca3af',
        name: emotionNames[key] || key,
      }))
      .filter(d => d.count > 0)
      .sort((a, b) => b.count - a.count)

    if (data.length === 0) return

    const maxCount = Math.max(...data.map(d => d.count))

    const x = d3.scaleLinear()
      .domain([0, maxCount])
      .range([0, width])

    const y = d3.scaleBand()
      .domain(data.map(d => d.emotion))
      .range([0, innerHeight])
      .padding(0.3)

    // 添加进度条
    g.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', 0)
      .attr('y', d => y(d.emotion) || 0)
      .attr('width', 0)
      .attr('height', y.bandwidth())
      .attr('fill', d => d.color)
      .attr('rx', 6)
      .attr('ry', 6)
      .transition()
      .duration(800)
      .delay((_, i) => i * 100)
      .attr('width', d => x(d.count))

    // 添加标签
    g.selectAll('.label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('x', -8)
      .attr('y', d => (y(d.emotion) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .attr('font-size', '13px')
      .attr('fill', '#374151')
      .attr('font-weight', '500')
      .text(d => d.name)

    // 添加数值
    g.selectAll('.count')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'count')
      .attr('x', d => x(d.count) + 8)
      .attr('y', d => (y(d.emotion) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('font-size', '13px')
      .attr('font-weight', '600')
      .attr('fill', '#6b7280')
      .attr('opacity', 0)
      .text(d => `${d.count}次`)
      .transition()
      .duration(300)
      .delay((_, i) => 800 + i * 100)
      .attr('opacity', 1)
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

  const getMoodLabel = (level: string) => {
    const labels: Record<string, string> = {
      terrible: '糟糕',
      bad: '不好',
      neutral: '一般',
      good: '不错',
      excellent: '很棒',
    }
    return labels[level] || level
  }

  const getMoodColorForLevel = (level: string) => {
    const colors: Record<string, string> = {
      terrible: '#ef4444',
      bad: '#f97316',
      neutral: '#fbbf24',
      good: '#84cc16',
      excellent: '#22c55e',
    }
    return colors[level] || '#9ca3af'
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

  const getPeriodLabel = (range: string) => {
    const map: Record<string, string> = {
      week: '近一周记录',
      month: '本月记录',
      quarter: '近三月记录',
      year: '近一年记录',
    }
    return map[range] || '本月记录'
  }

  if (loading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(180deg, #fafbfc 0%, #f5f7ff 100%)',
        }}
      >
        <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
        <div style={{ color: '#6b7280', fontSize: 16 }}>正在加载你的情绪数据...</div>
      </div>
    )
  }

  if (!stats || !trend) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(180deg, #fafbfc 0%, #f5f7ff 100%)',
        }}
      >
        <Empty description="暂无数据">
          <Link to="/diary/create">
            <Button type="primary" style={{ borderRadius: 20 }}>
              开始记录日记
            </Button>
          </Link>
        </Empty>
      </div>
    )
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #fafbfc 0%, #f5f7ff 100%)',
      }}
    >
      {/* Header */}
      <header
        style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          padding: '16px 0',
          boxShadow: '0 2px 20px rgba(0,0,0,0.05)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: 1200,
            margin: '0 auto',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 12,
                  background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 18,
                  boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
                }}
              >
                💜
              </div>
              <span
                style={{
                  color: '#1f2937',
                  fontSize: 22,
                  fontWeight: 700,
                }}
              >
                心灵伴侣AI
              </span>
            </div>
          </Link>
          <Space>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 130, borderRadius: 12 }}
              size="large"
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
              style={{
                borderRadius: 12,
                background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                border: 'none',
              }}
            >
              生成分享图
            </Button>
            <Link to="/diary">
              <Button icon={<ArrowLeftOutlined />} style={{ borderRadius: 12 }}>
                回到列表
              </Button>
            </Link>
          </Space>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px 60px' }}>
        {/* 页面标题 */}
        <div style={{ marginBottom: 40, textAlign: 'center' }}>
          <h1
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: '#1f2937',
              marginBottom: 8,
            }}
          >
            📊 情绪数据统计
          </h1>
          <p style={{ color: '#9ca3af', fontSize: 16 }}>
            记录你的情绪轨迹，见证每一次成长
          </p>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[20, 20]} style={{ marginBottom: 32 }}>
          <Col xs={12} sm={8}>
            <StatCard
              icon={<ReadOutlined />}
              value={stats.total_count || 0}
              label="总记录数"
              color={themeColors[themeColor]}
              suffix="篇"
            />
          </Col>
          <Col xs={12} sm={8}>
            <StatCard
              icon={<FireOutlined />}
              value={stats.current_streak || 0}
              label="连续记录"
              color="#f97316"
              suffix="天"
            />
          </Col>
          <Col xs={12} sm={8}>
            <StatCard
              icon={<FieldTimeOutlined />}
              value={stats.max_streak || 0}
              label="最长连续"
              color="#ef4444"
              suffix="天"
            />
          </Col>
        </Row>

        <Row gutter={[20, 20]} style={{ marginBottom: 32 }}>
          <Col xs={12} sm={6}>
            <StatCard
              icon={<SmileOutlined />}
              value={Math.round(stats.avg_mood || 0)}
              label="平均心情"
              color="#22c55e"
            />
          </Col>
          <Col xs={12} sm={6}>
            <StatCard
              icon={<CalendarOutlined />}
              value={stats.avg_words_per_day || 0}
              label="日均字数"
              color="#3b82f6"
            />
          </Col>
          <Col xs={12} sm={6}>
            <StatCard
              icon={<ReadOutlined />}
              value={stats.period_count || 0}
              label={getPeriodLabel(timeRange)}
              color="#8b5cf6"
            />
          </Col>
        </Row>

        {/* 心情趋势图 */}
        <Card
          style={{
            borderRadius: 24,
            boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
            marginBottom: 32,
          }}
          bodyStyle={{ padding: 28 }}
        >
          <div style={{ marginBottom: 24 }}>
            <h3
              style={{
                fontSize: 20,
                fontWeight: 700,
                color: '#1f2937',
                margin: 0,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <span style={{ fontSize: 24 }}>📈</span> 心情趋势
              <span
                style={{
                  fontSize: 14,
                  color: '#9ca3af',
                  fontWeight: 400,
                  marginLeft: 8,
                }}
              >
                ({formatTimeRange(timeRange)})
              </span>
            </h3>
          </div>
          <div key={chartKey} ref={moodTrendRef} style={{ height: 300, width: '100%' }}>
            {(!trend.trend_data || trend.trend_data.length === 0) && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                }}
              >
                <Empty description="暂无足够数据生成趋势图" />
              </div>
            )}
          </div>
        </Card>

        {/* 情绪分布和统计 */}
        <Row gutter={[20, 20]} style={{ marginBottom: 32 }}>
          <Col xs={24} lg={12}>
            <Card
              style={{
                borderRadius: 24,
                boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                height: '100%',
              }}
              bodyStyle={{ padding: 28 }}
            >
              <div style={{ marginBottom: 24 }}>
                <h3
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    color: '#1f2937',
                    margin: 0,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <span style={{ fontSize: 24 }}>🥧</span> 情绪占比
                  <span
                    style={{
                      fontSize: 14,
                      color: '#9ca3af',
                      fontWeight: 400,
                      marginLeft: 8,
                    }}
                  >
                    ({formatTimeRange(timeRange)})
                  </span>
                </h3>
              </div>
              <div
                key={chartKey}
                ref={emotionPieRef}
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  minHeight: 320,
                }}
              >
                {Object.keys(trend.emotion_distribution || {}).filter(
                  k => (trend.emotion_distribution as any)[k] > 0
                ).length === 0 && (
                  <Empty description="暂无足够数据生成图表" />
                )}
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card
              style={{
                borderRadius: 24,
                boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                height: '100%',
              }}
              bodyStyle={{ padding: 28 }}
            >
              <div style={{ marginBottom: 24 }}>
                <h3
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    color: '#1f2937',
                    margin: 0,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <span style={{ fontSize: 24 }}>😊</span> 情绪统计
                  <span
                    style={{
                      fontSize: 14,
                      color: '#9ca3af',
                      fontWeight: 400,
                      marginLeft: 8,
                    }}
                  >
                    ({formatTimeRange(timeRange)})
                  </span>
                </h3>
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
                  gap: 16,
                }}
              >
                {Object.entries(trend.emotion_distribution || {})
                  .filter(([_, count]) => (count as number) > 0)
                  .map(([emotion, count]) => (
                    <div
                      key={emotion}
                      style={{
                        background: '#f9fafb',
                        borderRadius: 16,
                        padding: '20px 16px',
                        textAlign: 'center',
                        transition: 'all 0.3s ease',
                        cursor: 'default',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)'
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    >
                      <div style={{ fontSize: 36, marginBottom: 8 }}>
                        {getEmotionIcon(emotion)}
                      </div>
                      <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 4 }}>
                        {emotion === 'happy' && '开心'}
                        {emotion === 'sad' && '悲伤'}
                        {emotion === 'angry' && '愤怒'}
                        {emotion === 'calm' && '平静'}
                        {emotion === 'excited' && '兴奋'}
                        {emotion === 'anxious' && '焦虑'}
                        {emotion === 'confused' && '困惑'}
                        {emotion === 'surprised' && '惊讶'}
                        {emotion === 'neutral' && '中性'}
                      </div>
                      <div
                        style={{
                          fontSize: 20,
                          fontWeight: 700,
                          color: themeColors[themeColor],
                        }}
                      >
                        {count}次
                      </div>
                    </div>
                  ))}
              </div>
            </Card>
          </Col>
        </Row>

        {/* 心情等级分布 */}
        {trend.mood_distribution && Object.keys(trend.mood_distribution).length > 0 && (
          <Card
            style={{
              borderRadius: 24,
              boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
              marginBottom: 32,
            }}
            bodyStyle={{ padding: 28 }}
          >
            <div style={{ marginBottom: 24 }}>
              <h3
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: '#1f2937',
                  margin: 0,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span style={{ fontSize: 24 }}>📊</span> 心情等级分布
              </h3>
            </div>
            <div
              style={{
                display: 'flex',
                gap: 16,
                flexWrap: 'wrap',
              }}
            >
              {Object.entries(trend.mood_distribution)
                .filter(([_, count]) => (count as number) > 0)
                .map(([level, count]) => (
                  <div
                    key={level}
                    style={{
                      flex: '1 1 120px',
                      minWidth: 120,
                      background: `${getMoodColorForLevel(level)}15`,
                      borderRadius: 16,
                      padding: '20px 16px',
                      textAlign: 'center',
                      border: `1px solid ${getMoodColorForLevel(level)}30`,
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <div
                      style={{
                        fontSize: 14,
                        color: getMoodColorForLevel(level),
                        fontWeight: 600,
                        marginBottom: 8,
                      }}
                    >
                      {getMoodLabel(level)}
                    </div>
                    <div
                      style={{
                        fontSize: 24,
                        fontWeight: 700,
                        color: '#1f2937',
                      }}
                    >
                      {count}次
                    </div>
                    {/* 进度条 */}
                    <div
                      style={{
                        marginTop: 12,
                        height: 6,
                        background: '#e5e7eb',
                        borderRadius: 3,
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          height: '100%',
                          width: `${((count as number) / Math.max(...Object.values(trend.mood_distribution || {}).map(Number))) * 100}%`,
                          background: getMoodColorForLevel(level),
                          borderRadius: 3,
                          transition: 'width 1s ease-out',
                        }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          </Card>
        )}

        {/* 分类统计 */}
        {stats.categories && Object.keys(stats.categories).length > 0 && (
          <Card
            style={{
              borderRadius: 24,
              boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
            }}
            bodyStyle={{ padding: 28 }}
          >
            <div style={{ marginBottom: 24 }}>
              <h3
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: '#1f2937',
                  margin: 0,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span style={{ fontSize: 24 }}>📁</span> 分类统计
              </h3>
            </div>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                gap: 16,
              }}
            >
              {Object.entries(stats.categories)
                .filter(([_, count]) => (count as number) > 0)
                .map(([category, count]) => (
                  <div
                    key={category}
                    style={{
                      background: '#f9fafb',
                      borderRadius: 16,
                      padding: '20px 16px',
                      textAlign: 'center',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>
                      {category}
                    </div>
                    <div
                      style={{
                        fontSize: 24,
                        fontWeight: 700,
                        color: themeColors[themeColor],
                      }}
                    >
                      {count}次
                    </div>
                  </div>
                ))}
            </div>
          </Card>
        )}
      </div>

      {/* 分享图片弹窗 */}
      <Modal
        title={
          <span style={{ fontSize: 18, fontWeight: 600 }}>情绪趋势分享</span>
        }
        open={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
        bodyStyle={{ padding: 0 }}
      >
        <EmotionShareImage timeRange={timeRange} onClose={() => setShareModalVisible(false)} />
      </Modal>
    </div>
  )
}