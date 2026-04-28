import { Card, Segmented, Row, Col } from 'antd'
import { Link } from 'react-router-dom'
import { useTheme } from '../../../hooks/useTheme'
import { useEffect, useState, useRef, useMemo } from 'react'
import * as d3 from 'd3'

interface MoodData {
  date: string
  mood_score?: number
  score?: number
  mood_level?: string
  primary_emotion?: string
}

interface DiaryStats {
  total_diaries?: number
  total_words?: number
  streak_days?: number
  current_streak?: number
  max_streak?: number
  avg_mood_score?: number
  avg_mood?: number
  most_common_emotion?: string
  top_themes?: string[]
  first_diary_date?: string
  recent_diary_date?: string
}

interface CheckinRecord {
  id: number
  checkin_date: string
  note?: string
}

interface CheckinStats {
  current_streak?: number
  max_streak?: number
  total_checkins?: number
}

interface Props {
  moodData?: MoodData[]
  diaryStats?: DiaryStats | null
  checkinRecords?: CheckinRecord[]
  checkinStats?: CheckinStats | null
  timeRange?: string
  onTimeRangeChange?: (range: string) => void
}

const moodEmojis = ['', '😢', '😔', '😐', '😊', '😄']
const moodColors = ['', '#ef4444', '#f97316', '#fbbf24', '#22c55e', '#10b981']

const getMoodEmoji = (score: number) => moodEmojis[Math.min(Math.max(Math.round(score), 1), 5)]
const getMoodColor = (score: number) => moodColors[Math.min(Math.max(Math.round(score), 1), 5)]

const getMoodLabel = (score: number) => {
  if (score <= 2) return '很糟'
  if (score <= 4) return '不太好'
  if (score <= 6) return '一般'
  if (score <= 8) return '不错'
  return '很棒'
}

const getTimeRangeLabel = (range: string) => {
  switch (range) {
    case 'week': return '本周'
    case 'month': return '本月'
    case 'quarter': return '本季'
    case 'year': return '本年'
    case 'all': return '全部'
    default: return '本月'
  }
}

export function MoodStation({
  moodData = [],
  diaryStats = null,
  checkinRecords = [],
  checkinStats = null,
  timeRange = 'month',
  onTimeRangeChange
}: Props) {
  const { themeColor, themeColors } = useTheme()
  const chartRef = useRef<HTMLDivElement>(null)
  const [localTimeRange, setLocalTimeRange] = useState(timeRange)
  const [dataVersion, setDataVersion] = useState(0)

  // 同步外部timeRange变化
  useEffect(() => {
    setLocalTimeRange(timeRange)
  }, [timeRange])

  const handleTimeRangeChange = (value: string | number) => {
    const newRange = value === '本周' ? 'week' : value === '本月' ? 'month' : value === '全部' ? 'all' : 'month'
    setLocalTimeRange(newRange)
    onTimeRangeChange?.(newRange)
  }

  // 监听 moodData 变化，递增版本号确保重新渲染
  const prevMoodDataRef = useRef(moodData)
  useEffect(() => {
    if (prevMoodDataRef.current !== moodData) {
      prevMoodDataRef.current = moodData
      setDataVersion(v => v + 1)
    }
  }, [moodData])

  // 使用后端的连续打卡天数
  const streak = checkinStats?.current_streak ?? 0

  // 数据处理 - 使用 useMemo 确保稳定的计算
  // 后端 API 已根据 time_range 返回过滤好的数据，这里只做去重处理
  const { chartData, deduplicatedData, avgScore, diaryCount, hasData } = useMemo(() => {
    const data = moodData.slice(-30)

    // 对数据进行去重处理：同一天的数据取平均值
    // 使用 YYYY-MM-DD 格式确保时区一致性
    const map = new Map<string, { total: number; count: number }>()
    data.forEach(d => {
      const dateObj = new Date(d.date)
      const dateKey = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`
      const existing = map.get(dateKey) || { total: 0, count: 0 }
      const score = d.mood_score || d.score || 3
      map.set(dateKey, { total: existing.total + score, count: existing.count + 1 })
    })

    const deduplicated = Array.from(map.entries())
      .map(([dateKey, { total, count }]) => ({
        date: new Date(dateKey),
        score: total / count,
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime())

    const avg = deduplicated.length > 0
      ? (deduplicated.reduce((s, i) => s + i.score, 0) / deduplicated.length).toFixed(1)
      : '0.0'

    const count = diaryStats?.total_diaries || deduplicated.length
    const hasEnoughData = deduplicated.length > 0

    return {
      chartData: data,
      deduplicatedData: deduplicated,
      avgScore: avg,
      diaryCount: count,
      hasData: hasEnoughData
    }
  }, [moodData, diaryStats])

  // 使用 D3 渲染图表 - 必须放在所有 hooks 之后
  useEffect(() => {
    if (!chartRef.current) return

    // 清除现有内容
    d3.select(chartRef.current).selectAll('*').remove()

    if (deduplicatedData.length === 0) return

    const containerWidth = chartRef.current.clientWidth
    const margin = { top: 40, right: 30, bottom: 40, left: 50 }
    const width = containerWidth - margin.left - margin.right
    const height = 240 - margin.top - margin.bottom

    const svg = d3.select(chartRef.current)
      .append('svg')
      .attr('width', containerWidth)
      .attr('height', 240)
      .attr('viewBox', `0 0 ${containerWidth} 240`)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // 数据准备
    const data = deduplicatedData.map(d => ({
      date: d.date,
      score: d.score,
    }))

    // 根据时间范围计算完整的日期区间
    const now = new Date()
    let rangeStart: Date
    const rangeEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    if (localTimeRange === 'week') {
      const weekday = now.getDay()
      rangeStart = new Date(now)
      rangeStart.setDate(now.getDate() - weekday)
    } else if (localTimeRange === 'month') {
      rangeStart = new Date(now.getFullYear(), now.getMonth(), 1)
    } else if (localTimeRange === 'year') {
      rangeStart = new Date(now.getFullYear(), 0, 1)
    } else if (localTimeRange === 'all') {
      rangeStart = data.length > 0 ? data[0].date : rangeEnd
    } else {
      rangeStart = new Date(now.getFullYear(), now.getMonth(), 1)
    }

    // X轴 - 使用整个时间范围，而不是只显示有数据的范围
    const x = d3.scaleTime()
      .domain([rangeStart, rangeEnd])
      .range([0, width])

    // Y轴 - 心情分数 1-5
    const y = d3.scaleLinear()
      .domain([1, 5])
      .range([height, 0])

    // 颜色映射
    const colorMap: Record<number, string> = {
      1: '#ef4444',
      2: '#f97316',
      3: '#fbbf24',
      4: '#22c55e',
      5: '#10b981',
    }

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
      .x(d => x(d.date))
      .y0(height)
      .y1(d => y(d.score))
      .curve(d3.curveMonotoneX)

    svg.append('path')
      .datum(data)
      .attr('fill', 'url(#areaGradient)')
      .attr('d', area)

    // 线条
    const line = d3.line<typeof data[0]>()
      .x(d => x(d.date))
      .y(d => y(d.score))
      .curve(d3.curveMonotoneX)

    const path = svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', themeColors[themeColor])
      .attr('stroke-width', 2.5)
      .attr('stroke-linecap', 'round')
      .attr('d', line)

    // 线条动画
    const totalLength = path.node()?.getTotalLength() || 0
    path
      .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
      .attr('stroke-dashoffset', totalLength)
      .transition()
      .duration(1500)
      .ease(d3.easeQuadOut)
      .attr('stroke-dashoffset', 0)

    // Y轴网格线
    svg.append('g')
      .attr('class', 'grid')
      .attr('opacity', 0.1)
      .call(d3.axisLeft(y).ticks(4).tickSize(-width).tickFormat(() => ''))

    // Y轴
    const moodLabels = ['', '很糟', '不太好', '一般', '不错', '很棒']
    svg.append('g')
      .call(d3.axisLeft(y).ticks(4).tickFormat(d => moodLabels[d as number] || ''))
      .selectAll('text')
      .attr('fill', '#6b7280')
      .attr('font-size', '12px')

    // X轴 - 动态调整ticks数量，避免日期重复
    const dataRange = data.length > 0 ? (data[data.length - 1].date.getTime() - data[0].date.getTime()) : 0
    const daysDiff = Math.ceil(dataRange / (1000 * 60 * 60 * 24))
    const tickCount = Math.min(Math.max(daysDiff, 3), 6)
    
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(tickCount).tickFormat(d => d3.timeFormat('%m/%d')(d as Date)))
      .selectAll('text')
      .attr('fill', '#9ca3af')
      .attr('font-size', '11px')

    // 数据点
    svg.selectAll('.dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.score))
      .attr('r', 0)
      .attr('fill', d => colorMap[Math.round(d.score)] || themeColors[themeColor])
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .transition()
      .delay((_, i) => 1500 + i * 30)
      .duration(200)
      .attr('r', 5)

    // 悬停效果
    svg.selectAll('.dot-hover')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.score))
      .attr('r', 15)
      .attr('fill', 'transparent')
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        const score = d.score
        const label = getMoodLabel(score)
        const emoji = getMoodEmoji(score)

        d3.select(this.parentNode)
          .append('text')
          .attr('class', 'tooltip')
          .attr('x', x(d.date))
          .attr('y', y(d.score) - 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('font-weight', '600')
          .attr('fill', '#374151')
          .text(`${emoji} ${score.toFixed(1)}分 (${label})`)
      })
      .on('mouseout', function() {
        d3.select(this.parentNode).selectAll('.tooltip').remove()
      })

  }, [deduplicatedData, themeColor, themeColors, dataVersion])

  return (
    <Card
      style={{
        borderRadius: 24,
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
        marginBottom: 32,
      }}
      bodyStyle={{ padding: 24 }}
    >
      {/* 头部 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 24,
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        <div>
          <h3
            style={{
              fontSize: 20,
              fontWeight: 700,
              margin: 0,
              color: '#1f2937',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span style={{ fontSize: 22 }}>📊</span> 情绪能量站
          </h3>
          <p
            style={{
              fontSize: 13,
              color: '#9ca3af',
              margin: '4px 0 0',
            }}
          >
            过去{deduplicatedData.length}天的情绪轨迹
          </p>
        </div>
        <Segmented
          size="small"
          options={['本周', '本月', '全部']}
          value={getTimeRangeLabel(localTimeRange)}
          onChange={handleTimeRangeChange}
        />
      </div>

      {/* 图表区域 - 无数据时显示空状态，但保留切换功能 */}
      {hasData ? (
        <div
          ref={chartRef}
          style={{
            height: 240,
            background: '#fafafa',
            borderRadius: 16,
            marginBottom: 24,
            overflow: 'visible',
          }}
        />
      ) : (
        <div
          style={{
            height: 240,
            background: '#fafafa',
            borderRadius: 16,
            marginBottom: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9ca3af',
            fontSize: 15,
          }}
        >
          <span style={{ fontSize: 48, display: 'block', marginBottom: 8 }}>📊</span>
          <p>开始记录心情后，这里将展示你的情绪趋势</p>
        </div>
      )}

      {/* 底部统计 */}
      <Row gutter={16}>
        <Col span={8}>
          <div
            style={{
              textAlign: 'center',
              padding: '16px 8px',
              background: '#fef7f0',
              borderRadius: 16,
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 4 }}>
              {getMoodEmoji(parseFloat(avgScore))}
            </div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                color: '#1f2937',
                lineHeight: 1,
              }}
            >
              {avgScore}
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#9ca3af',
                marginTop: 4,
              }}
            >
              平均能量
            </div>
          </div>
        </Col>
        <Col span={8}>
          <div
            style={{
              textAlign: 'center',
              padding: '16px 8px',
              background: '#fdf2f8',
              borderRadius: 16,
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 4 }}>🔥</div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                color: '#1f2937',
                lineHeight: 1,
              }}
            >
              {streak}
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#9ca3af',
                marginTop: 4,
              }}
            >
              连续天数
            </div>
          </div>
        </Col>
        <Col span={8}>
          <div
            style={{
              textAlign: 'center',
              padding: '16px 8px',
              background: '#f5f3ff',
              borderRadius: 16,
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 4 }}>📝</div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                color: '#1f2937',
                lineHeight: 1,
              }}
            >
              {diaryCount}
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#9ca3af',
                marginTop: 4,
              }}
            >
              篇日记
            </div>
          </div>
        </Col>
      </Row>

      {/* 查看详情链接 */}
      <div style={{ textAlign: 'center', marginTop: 20 }}>
        <Link
          to="/diary/stats"
          style={{
            fontSize: 14,
            color: themeColors[themeColor],
            fontWeight: 500,
            textDecoration: 'none',
          }}
        >
          查看详细分析 →
        </Link>
      </div>
    </Card>
  )
}

export default MoodStation
