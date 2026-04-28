import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Card,
  List,
  Button,
  Avatar,
  Tag,
  Spin,
  Empty,
  Space,
  Input,
  DatePicker,
  Select,
  Row,
  Col,
  App,
} from 'antd'
import {
  CalendarOutlined,
  SmileOutlined,
  EditOutlined,
  PlusOutlined,
  SearchOutlined,
  ArrowLeftOutlined,
  BookOutlined,
} from '@ant-design/icons'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import { useTheme } from '../../hooks/useTheme'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

// Mood colors configuration
const MOOD_CONFIG = {
  excellent: { color: '#10b981', label: '很棒', icon: '😄' },
  good: { color: '#34d399', label: '不错', icon: '🙂' },
  neutral: { color: '#f59e0b', label: '一般', icon: '😐' },
  bad: { color: '#f97316', label: '不好', icon: '😔' },
  terrible: { color: '#ef4444', label: '糟糕', icon: '😢' },
}

export default function DiaryList() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { themeColors, themeColor, theme } = useTheme()
  const {
    diaries,
    totalCount,
    currentPage,
    pageSize,
    loading,
    setDiaries,
    setTotalCount,
    setCurrentPage,
    setLoading,
    stats,
    setStats,
  } = useDiaryStore()

  const themeGradient = themeColors[themeColor]
  const [searchQuery, setSearchQuery] = useState('')
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([null, null])
  const [moodFilter, setMoodFilter] = useState<string>()
  const [emotionFilter, setEmotionFilter] = useState<string>()

  useEffect(() => {
    loadDiaries()
    loadStats()
  }, [])

  const loadDiaries = async (page = 1) => {
    setLoading(true)
    try {
      const params: any = {
        page,
        page_size: pageSize,
      }
      if (searchQuery) {
        params.tags = searchQuery
      }
      if (dateRange[0] && dateRange[1]) {
        params.start_date = dateRange[0].format('YYYY-MM-DD')
        params.end_date = dateRange[1].format('YYYY-MM-DD')
      }
      if (moodFilter) {
        params.mood_level = moodFilter
      }
      if (emotionFilter) {
        params.emotion = emotionFilter
      }

      const res = await api.diary.list(params)
      setDiaries(res.data)
      setTotalCount(res.total)
      setCurrentPage(page)
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '加载日记失败')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const res = await api.diary.stats()
      setStats(res)
    } catch (error) {
      console.error(error)
    }
  }

  const handleSearch = () => {
    loadDiaries(1)
  }

  const handleReset = () => {
    setSearchQuery('')
    setDateRange([null, null])
    setMoodFilter(undefined)
    setEmotionFilter(undefined)
    loadDiaries(1)
  }

  const handleEdit = (id: number) => {
    navigate(`/diary/${id}`)
  }

  const handleCreate = () => {
    navigate('/diary/create')
  }

  const getMoodInfo = (moodScore: number) => {
    if (moodScore >= 8) return MOOD_CONFIG.excellent
    if (moodScore >= 6) return MOOD_CONFIG.good
    if (moodScore >= 4) return MOOD_CONFIG.neutral
    if (moodScore >= 2) return MOOD_CONFIG.bad
    return MOOD_CONFIG.terrible
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {/* Header */}
      <header style={{
        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
        padding: '32px 24px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          top: '-30%',
          right: '-10%',
          width: '50%',
          height: '150%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            width: 64,
            height: 64,
            borderRadius: '18px',
            background: 'rgba(255,255,255,0.2)',
            backdropFilter: 'blur(10px)',
            margin: '0 auto 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid rgba(255,255,255,0.3)',
          }}>
            <BookOutlined style={{ fontSize: 28, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 8, fontWeight: 700 }}>
            情感日记
          </h1>
          <p style={{ opacity: 0.9, margin: 0, fontSize: 15 }}>
            记录心情变化，追踪情绪成长
          </p>
        </div>
      </header>

      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '24px 16px 60px' }}>
        {/* Back & Create */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <Link to="/">
            <Button icon={<ArrowLeftOutlined />} style={{ borderRadius: 12 }}>
              返回首页
            </Button>
          </Link>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
            style={{
              background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
              border: 'none',
              borderRadius: 12,
              height: 40,
            }}
          >
            写日记
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <Row gutter={[12, 12]} style={{ marginBottom: 20 }}>
            {[
              { label: '总记录', value: stats.total_count, gradient: themeGradient },
              { label: '连续记录', value: stats.current_streak, gradient: ['#f59e0b', '#fbbf24'] },
              { label: '平均心情', value: stats.avg_mood?.toFixed(1) || '0', gradient: ['#ec4899', '#f472b6'] },
            ].map((stat, idx) => (
              <Col xs={8} key={idx}>
                <Card
                  style={{
                    textAlign: 'center',
                    border: 'none',
                    borderRadius: 16,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                    background: theme === 'dark' ? 'rgba(255,255,255,0.05)' : '#fff',
                  }}
                  bodyStyle={{ padding: '16px 8px' }}
                >
                  <div style={{
                    fontSize: 24,
                    fontWeight: 700,
                    marginBottom: 4,
                    color: stat.gradient[0],
                  }}>
                    {stat.value}
                  </div>
                  <div style={{ fontSize: 12, color: theme === 'dark' ? 'rgba(255,255,255,0.65)' : '#6b7280' }}>{stat.label}</div>
                </Card>
              </Col>
            ))}
          </Row>
        )}

        {/* Search & Filter Card */}
        <Card
          style={{
            marginBottom: 20,
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
          }}
          bodyStyle={{ padding: 20 }}
        >
          <Row gutter={[12, 12]} align="middle">
            <Col xs={24} md={8}>
              <Input
                placeholder="搜索标签..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                prefix={<SearchOutlined style={{ color: themeGradient }} />}
                onPressEnter={handleSearch}
                allowClear
                style={{ borderRadius: 12, height: 40 }}
              />
            </Col>
            <Col xs={24} md={6}>
              <RangePicker
                value={dateRange}
                onChange={(dates) => setDateRange(dates as [dayjs.Dayjs | null, dayjs.Dayjs | null])}
                placeholder={['开始日期', '结束日期']}
                allowClear
                style={{ width: '100%', borderRadius: 12 }}
              />
            </Col>
            <Col xs={12} md={4}>
              <Select
                placeholder="心情筛选"
                value={moodFilter}
                onChange={setMoodFilter}
                allowClear
                style={{ width: '100%' }}
              >
                <Select.Option value="terrible">糟糕</Select.Option>
                <Select.Option value="bad">不好</Select.Option>
                <Select.Option value="neutral">一般</Select.Option>
                <Select.Option value="good">不错</Select.Option>
                <Select.Option value="excellent">很棒</Select.Option>
              </Select>
            </Col>
            <Col xs={12} md={4}>
              <Select
                placeholder="情绪筛选"
                value={emotionFilter}
                onChange={setEmotionFilter}
                allowClear
                style={{ width: '100%' }}
              >
                <Select.Option value="happy">开心</Select.Option>
                <Select.Option value="sad">难过</Select.Option>
                <Select.Option value="angry">生气</Select.Option>
                <Select.Option value="calm">平静</Select.Option>
                <Select.Option value="excited">兴奋</Select.Option>
                <Select.Option value="anxious">焦虑</Select.Option>
              </Select>
            </Col>
            <Col xs={12} md={2}>
              <Button
                type="primary"
                onClick={handleSearch}
                style={{
                  background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                  border: 'none',
                  borderRadius: 12,
                  height: 40,
                }}
              >
                搜索
              </Button>
            </Col>
            <Col xs={12} md={2}>
              <Button onClick={handleReset} style={{ borderRadius: 12, height: 40 }}>
                重置
              </Button>
            </Col>
          </Row>
        </Card>

        {/* Diary List */}
        <Card
          style={{
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
          }}
          bodyStyle={{ padding: 0 }}
        >
          <Spin spinning={loading}>
            {diaries.length > 0 ? (
              <List
                dataSource={diaries}
                renderItem={(item) => {
                  const moodInfo = getMoodInfo(item.mood_score)
                  return (
                    <List.Item
                      key={item.id}
                      onClick={() => navigate(`/diary/${item.id}`)}
                      style={{
                        cursor: 'pointer',
                        padding: '20px 24px',
                        borderBottom: '1px solid #f5f5f5',
                        transition: 'all 0.2s ease',
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.background = '#f8fafc'
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.background = '#fff'
                      }}
                    >
                      <List.Item.Meta
                        avatar={
                          <div style={{
                            width: 56,
                            height: 56,
                            borderRadius: '16px',
                            background: `${moodInfo.color}15`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 24,
                          }}>
                            {moodInfo.icon}
                          </div>
                        }
                        title={
                          <Space>
                            <span style={{ fontWeight: 600, color: '#1f2937' }}>
                              {dayjs(item.date).format('YYYY年MM月DD日')}
                            </span>
                            {item.category && (
                              <Tag
                                style={{
                                  background: `${themeGradient}15`,
                                  color: themeGradient,
                                  border: `1px solid ${themeGradient}30`,
                                  borderRadius: 8,
                                }}
                              >
                                {item.category}
                              </Tag>
                            )}
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size="small" style={{ width: '100%', marginTop: 8 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                              <span style={{ color: moodInfo.color, fontWeight: 600 }}>
                                心情: {item.mood_score}/10
                              </span>
                              {item.primary_emotion && (
                                <Tag
                                  style={{
                                    background: '#f3f4f6',
                                    color: '#6b7280',
                                    borderRadius: 8,
                                  }}
                                >
                                  {item.primary_emotion}
                                </Tag>
                              )}
                            </div>
                            {item.tags && (
                              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                                {item.tags.split(',').map((tag: string, index: number) => (
                                  <Tag
                                    key={index}
                                    style={{
                                      background: '#f3f4f6',
                                      color: '#6b7280',
                                      borderRadius: 8,
                                      fontSize: 12,
                                    }}
                                  >
                                    #{tag.trim()}
                                  </Tag>
                                ))}
                              </div>
                            )}
                            {item.summary && (
                              <p style={{ color: '#6b7280', fontSize: 14, margin: 0, lineHeight: 1.6 }}>
                                {item.summary.length > 80 ? `${item.summary.slice(0, 80)}...` : item.summary}
                              </p>
                            )}
                          </Space>
                        }
                      />
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEdit(item.id)
                        }}
                        style={{ color: themeGradient }}
                      >
                        编辑
                      </Button>
                    </List.Item>
                  )
                }}
                pagination={{
                  current: currentPage,
                  pageSize: pageSize,
                  total: totalCount,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条`,
                  onChange: (page, size) => {
                    setCurrentPage(page)
                    loadDiaries(page)
                  },
                  onShowSizeChange: (_, size) => {
                    setCurrentPage(1)
                    loadDiaries(1)
                  },
                }}
              />
            ) : (
              <div style={{ padding: '60px 20px', textAlign: 'center' }}>
                <Empty
                  description={
                    <span style={{ color: '#6b7280' }}>
                      还没有日记记录
                    </span>
                  }
                >
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreate}
                    style={{
                      background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                      border: 'none',
                      borderRadius: 12,
                    }}
                  >
                    开始写日记
                  </Button>
                </Empty>
              </div>
            )}
          </Spin>
        </Card>

        {/* Quick Action */}
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Button
            size="large"
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
            style={{
              background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
              border: 'none',
              borderRadius: 16,
              padding: '8px 40px',
              height: 52,
              fontSize: 16,
              fontWeight: 600,
              boxShadow: `0 8px 30px ${themeGradient}40`,
            }}
          >
            写日记
          </Button>
        </div>
      </div>
    </div>
  )
}
