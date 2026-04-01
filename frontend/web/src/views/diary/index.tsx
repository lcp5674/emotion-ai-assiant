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
} from '@ant-design/icons'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Option } = Select

export default function DiaryList() {
  const navigate = useNavigate()
  const { message } = App.useApp()
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
          <div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
              style={{ background: '#722ed1' }}
            >
              写日记
            </Button>
          </div>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        {/* 统计卡片 */}
        {stats && (
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
                  {stats.current_streak}
                </div>
                <div style={{ color: '#8c8c8c' }}>连续记录</div>
              </Card>
            </Col>
            <Col xs={8}>
              <Card style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                  {stats.avg_mood.toFixed(1)}
                </div>
                <div style={{ color: '#8c8c8c' }}>平均心情</div>
              </Card>
            </Col>
          </Row>
        )}

        {/* 搜索和筛选 */}
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} md={8}>
              <Input
                placeholder="搜索标签..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                prefix={<SearchOutlined />}
                onPressEnter={handleSearch}
                allowClear
              />
            </Col>
            <Col xs={24} md={6}>
              <RangePicker
                value={dateRange}
                onChange={(dates) => setDateRange(dates as [dayjs.Dayjs | null, dayjs.Dayjs | null])}
                placeholder={['开始日期', '结束日期']}
                allowClear
              />
            </Col>
            <Col xs={12} md={4}>
              <Select
                placeholder="心情筛选"
                value={moodFilter}
                onChange={setMoodFilter}
                allowClear
              >
                <Option value="terrible">糟糕</Option>
                <Option value="bad">不好</Option>
                <Option value="neutral">一般</Option>
                <Option value="good">不错</Option>
                <Option value="excellent">很棒</Option>
              </Select>
            </Col>
            <Col xs={12} md={4}>
              <Select
                placeholder="情绪筛选"
                value={emotionFilter}
                onChange={setEmotionFilter}
                allowClear
              >
                <Option value="happy">开心</Option>
                <Option value="sad">难过</Option>
                <Option value="angry">生气</Option>
                <Option value="calm">平静</Option>
                <Option value="excited">兴奋</Option>
                <Option value="anxious">焦虑</Option>
              </Select>
            </Col>
            <Col xs={24} md={2}>
              <Button type="primary" onClick={handleSearch} style={{ background: '#722ed1' }}>
                搜索
              </Button>
            </Col>
            <Col xs={24} md={2}>
              <Button onClick={handleReset}>重置</Button>
            </Col>
          </Row>
        </Card>

        {/* 日记列表 */}
        <Card>
          <Spin spinning={loading}>
            {diaries.length > 0 ? (
              <List
                dataSource={diaries}
                renderItem={(item) => (
                  <List.Item
                    key={item.id}
                    actions={[
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(item.id)}
                      >
                        编辑
                      </Button>,
                    ]}
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/diary/${item.id}`)}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar style={{ backgroundColor: getMoodColor(item.mood_score) }}>
                          {item.mood_score}
                        </Avatar>
                      }
                      title={
                        <Space>
                          {dayjs(item.date).format('YYYY年MM月DD日')}
                          {item.category && (
                            <Tag color="blue">{item.category}</Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            {getMoodIcon(item.mood_score)}
                            <span>心情评分: {item.mood_score}/10</span>
                            {item.primary_emotion && (
                              <Tag color="purple">
                                {item.primary_emotion}
                              </Tag>
                            )}
                          </div>
                          {item.tags && (
                            <div>
                              {item.tags.split(',').map((tag, index) => (
                                <Tag key={index} bordered={false} style={{ marginRight: 4, marginBottom: 4 }}>
                                  {tag.trim()}
                                </Tag>
                              ))}
                            </div>
                          )}
                          {item.summary && (
                            <p style={{ color: '#666', fontSize: 14 }}>
                              {item.summary}
                            </p>
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                )}
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
              <Empty
                description="还没有日记记录"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleCreate}
                  style={{ background: '#722ed1' }}
                >
                  开始写日记
                </Button>
              </Empty>
            )}
          </Spin>
        </Card>

        {/* 快速操作 */}
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Button
            size="large"
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
            style={{ background: '#722ed1' }}
          >
            写日记
          </Button>
        </div>
      </div>
    </div>
  )
}
