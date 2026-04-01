import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import {
  Card,
  Button,
  Avatar,
  Tag,
  Spin,
  Empty,
  Space,
  Divider,
  App,
} from 'antd'
import {
  CalendarOutlined,
  SmileOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { api } from '../../api/request'
import { useDiaryStore } from '../../stores'
import dayjs from 'dayjs'

export default function DiaryDetail() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { message } = App.useApp()
  const {
    currentDiary,
    setCurrentDiary,
    loading,
    setLoading,
  } = useDiaryStore()

  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    if (id) {
      loadDiary(parseInt(id))
    }
  }, [id])

  const loadDiary = async (diaryId: number) => {
    setLoading(true)
    try {
      const res = await api.diary.get(diaryId)
      setCurrentDiary(res)
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '加载日记失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !window.confirm('确定要删除这篇日记吗？')) {
      return
    }

    setLoading(true)
    try {
      await api.diary.delete(parseInt(id))
      message.success('删除成功')
      navigate('/diary')
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '删除失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!id) return

    setAnalyzing(true)
    try {
      const res = await api.diary.analyze(parseInt(id))
      if (res.analysis) {
        setCurrentDiary(prev => prev ? {
          ...prev,
          ai_analysis: res.analysis,
          ai_suggestion: res.suggestion,
        } : null)
        message.success('分析完成')
      } else {
        message.warning('无内容可分析')
      }
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '分析失败')
    } finally {
      setAnalyzing(false)
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

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!currentDiary) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Empty description="日记不存在" />
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
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/diary')}
            >
              回到列表
            </Button>
          </Space>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        <Card>
          {/* 日记信息 */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <Avatar style={{ backgroundColor: getMoodColor(currentDiary.mood_score) }} size={48}>
                  {currentDiary.mood_score}
                </Avatar>
                <div>
                  <h2 style={{ margin: 0, fontSize: 24 }}>
                    {dayjs(currentDiary.date).format('YYYY年MM月DD日')}
                  </h2>
                  <Space>
                    <Tag color={getMoodColor(currentDiary.mood_score)}>
                      {getMoodIcon(currentDiary.mood_score)}
                      {' '}{currentDiary.mood_score}/10
                    </Tag>
                    {currentDiary.primary_emotion && (
                      <Tag color="purple">
                        {getEmotionIcon(currentDiary.primary_emotion)}
                        {' '}{currentDiary.primary_emotion}
                      </Tag>
                    )}
                    {currentDiary.category && (
                      <Tag color="blue">
                        {currentDiary.category}
                      </Tag>
                    )}
                  </Space>
                </div>
              </div>
              <div>
                <Space>
                  <Button
                    icon={<EditOutlined />}
                    onClick={() => navigate(`/diary/${id}/edit`)}
                  >
                    编辑
                  </Button>
                  <Button
                    icon={<DeleteOutlined />}
                    danger
                    onClick={handleDelete}
                  >
                    删除
                  </Button>
                </Space>
              </div>
            </div>
          </div>

          {/* 标签 */}
          {currentDiary.tags && (
            <div style={{ marginBottom: 24 }}>
              {currentDiary.tags.split(',').map((tag, index) => (
                <Tag key={index} bordered={false} style={{ marginRight: 8, marginBottom: 8 }}>
                  {tag.trim()}
                </Tag>
              ))}
            </div>
          )}

          <Divider />

          {/* 日记内容 */}
          {currentDiary.content ? (
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ marginBottom: 16 }}>日记内容</h3>
              <div style={{
                fontSize: 16,
                lineHeight: 1.8,
                whiteSpace: 'pre-wrap',
                backgroundColor: '#fafafa',
                padding: 16,
                borderRadius: 8,
              }}>
                {currentDiary.content}
              </div>
            </div>
          ) : (
            <div style={{ marginBottom: 24, textAlign: 'center', color: '#999' }}>
              暂无内容
            </div>
          )}

          {/* AI分析 */}
          <Divider />
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              AI情绪分析
              <Button
                type="primary"
                size="small"
                onClick={handleAnalyze}
                loading={analyzing}
                style={{ background: '#722ed1' }}
              >
                {analyzing ? '分析中...' : currentDiary.ai_analysis ? '重新分析' : '分析'}
              </Button>
            </h3>

            {currentDiary.ai_analysis ? (
              <div>
                <div style={{ marginBottom: 16 }}>
                  <h4 style={{ marginBottom: 8 }}>情绪分析</h4>
                  <div style={{
                    backgroundColor: '#f0f5ff',
                    padding: 16,
                    borderRadius: 8,
                    borderLeft: '4px solid #722ed1',
                  }}>
                    {currentDiary.ai_analysis}
                  </div>
                </div>
                {currentDiary.ai_suggestion && (
                  <div>
                    <h4 style={{ marginBottom: 8 }}>建议</h4>
                    <div style={{
                      backgroundColor: '#f6ffed',
                      padding: 16,
                      borderRadius: 8,
                      borderLeft: '4px solid #52c41a',
                    }}>
                      {currentDiary.ai_suggestion}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Empty
                description="尚未分析，请点击上方按钮开始分析"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </div>

          {/* 操作按钮 */}
          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <Space>
              <Button
                size="large"
                icon={<EditOutlined />}
                onClick={() => navigate(`/diary/${id}/edit`)}
              >
                编辑
              </Button>
              <Button
                size="large"
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/diary')}
              >
                回到列表
              </Button>
            </Space>
          </div>
        </Card>
      </div>
    </div>
  )
}
