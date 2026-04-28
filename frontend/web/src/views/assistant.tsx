import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Tag, Input, Spin, Button, App } from 'antd'
import { SearchOutlined, HeartOutlined, HeartFilled, MessageOutlined, ArrowLeftOutlined, RobotOutlined, FilterOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useTheme } from '../hooks/useTheme'

interface Assistant {
  id: number
  name: string
  avatar?: string
  mbti_type: string
  personality?: string
  speaking_style?: string
  expertise?: string
  greeting?: string
  tags?: string
  is_recommended: boolean
  is_favorited: boolean
}

// MBTI类型对应的渐变色
const MBTI_COLORS: Record<string, string[]> = {
  INTJ: ['#6366f1', '#8b5cf6'],
  INTP: ['#8b5cf6', '#a855f7'],
  ENTJ: ['#3b82f6', '#60a5fa'],
  ENTP: ['#06b6d4', '#22d3ee'],
  INFJ: ['#10b981', '#34d399'],
  INFP: ['#14b8a6', '#2dd4bf'],
  ENFJ: ['#f59e0b', '#fbbf24'],
  ENFP: ['#f97316', '#fb923c'],
  ISTJ: ['#64748b', '#94a3b8'],
  ISFJ: ['#ec4899', '#f472b6'],
  ESTJ: ['#8b5cf6', '#a78bfa'],
  ESFJ: ['#f43f5e', '#fb7185'],
  ISTP: ['#475569', '#64748b'],
  ISFP: ['#a855f7', '#c084fc'],
  ESTP: ['#f97316', '#fdba74'],
  ESFP: ['#ec4899', '#f9a8d4'],
}

export default function AssistantSquare() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { themeColors, themeColor } = useTheme()
  const [assistants, setAssistants] = useState<Assistant[]>([])
  const [loading, setLoading] = useState(true)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedMbti, setSelectedMbti] = useState<string | null>(null)

  const themeGradient = themeColors[themeColor]

  const mbtiTypes = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP',
    'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']

  useEffect(() => {
    loadAssistants()
  }, [selectedMbti])

  const loadAssistants = async () => {
    setLoading(true)
    try {
      const res = await api.mbti.assistants({
        mbti_type: selectedMbti || undefined,
      })
      setAssistants(res.list || [])
    } catch (error) {
      message.error('加载助手失败')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleFavorite = async (assistant: Assistant, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const res = await api.mbti.toggleFavorite(assistant.id)
      setAssistants(prev => prev.map(a =>
        a.id === assistant.id ? { ...a, is_favorited: res.is_favorited } : a
      ))
      message.success(res.is_favorited ? '已收藏' : '已取消收藏')
    } catch (error: any) {
      const errorMsg = error?.message || String(error)
      if (errorMsg.includes('登录') || errorMsg === '登录失败') {
        message.error('请先登录')
        navigate('/login')
      } else {
        message.error('操作失败')
      }
    }
  }

  const filteredAssistants = assistants.filter(a => {
    if (!searchKeyword) return true
    const keyword = searchKeyword.toLowerCase()
    return (
      a.name.toLowerCase().includes(keyword) ||
      a.mbti_type.toLowerCase().includes(keyword) ||
      a.tags?.toLowerCase().includes(keyword)
    )
  })

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
        padding: '60px 24px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background Elements */}
        <div style={{
          position: 'absolute',
          top: '-30%',
          right: '-10%',
          width: '50%',
          height: '150%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-20%',
          left: '-5%',
          width: '30%',
          height: '100%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '24px',
            background: 'rgba(255,255,255,0.2)',
            backdropFilter: 'blur(10px)',
            margin: '0 auto 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid rgba(255,255,255,0.3)',
          }}>
            <RobotOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{
            fontSize: 36,
            marginBottom: 12,
            fontWeight: 700,
            textShadow: '0 2px 10px rgba(0,0,0,0.1)',
          }}>
            AI助手广场
          </h1>
          <p style={{ fontSize: 18, opacity: 0.9, margin: 0 }}>
            选择你喜欢的AI情感助手，开启温暖对话
          </p>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 16px 60px' }}>
        {/* Back Button */}
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          style={{
            borderRadius: 12,
            marginBottom: 20,
            height: 40,
            padding: '0 16px',
          }}
        >
          返回
        </Button>

        {/* Search & Filter Card */}
        <Card
          style={{
            marginBottom: 24,
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
          }}
          bodyStyle={{ padding: 20 }}
        >
          {/* Search Bar */}
          <Input
            placeholder="搜索助手名称、MBTI类型或标签..."
            prefix={<SearchOutlined style={{ color: themeGradient }} />}
            suffix={
              searchKeyword && (
                <Button
                  type="text"
                  size="small"
                  onClick={() => setSearchKeyword('')}
                  style={{ color: '#9ca3af' }}
                >
                  清除
                </Button>
              )
            }
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            allowClear
            size="large"
            style={{
              borderRadius: 14,
              marginBottom: 16,
              height: 48,
            }}
          />

          {/* MBTI Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: '#6b7280',
              fontSize: 13,
              fontWeight: 500,
            }}>
              <FilterOutlined />
              <span>筛选类型：</span>
            </div>
            <Tag
              onClick={() => setSelectedMbti(null)}
              style={{
                cursor: 'pointer',
                borderRadius: 20,
                padding: '4px 16px',
                fontSize: 13,
                border: selectedMbti === null ? `2px solid ${themeGradient}` : '1px solid #e5e7eb',
                background: selectedMbti === null ? `${themeGradient}10` : '#fff',
                color: selectedMbti === null ? themeGradient : '#6b7280',
              }}
            >
              全部
            </Tag>
            {mbtiTypes.map(mbti => {
              const colors = MBTI_COLORS[mbti] || ['#6366f1', '#8b5cf6']
              const isSelected = selectedMbti === mbti
              return (
                <Tag
                  key={mbti}
                  onClick={() => setSelectedMbti(mbti)}
                  style={{
                    cursor: 'pointer',
                    borderRadius: 20,
                    padding: '4px 14px',
                    fontSize: 12,
                    fontWeight: 500,
                    border: isSelected ? `2px solid ${colors[0]}` : '1px solid #e5e7eb',
                    background: isSelected ? `${colors[0]}15` : '#fff',
                    color: isSelected ? colors[0] : '#6b7280',
                    transition: 'all 0.2s ease',
                  }}
                >
                  {mbti}
                </Tag>
              )
            })}
          </div>
        </Card>

        {/* Results Count */}
        <div style={{
          marginBottom: 16,
          color: '#6b7280',
          fontSize: 14,
        }}>
          共找到 <span style={{ fontWeight: 600, color: themeGradient }}>{filteredAssistants.length}</span> 位AI助手
        </div>

        {/* Assistants Grid */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 80 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: '#6b7280' }}>正在加载AI助手...</div>
          </div>
        ) : (
          <Row gutter={[20, 20]}>
            {filteredAssistants.map((assistant) => {
              const colors = MBTI_COLORS[assistant.mbti_type] || [themeGradient, themeGradient]
              return (
                <Col xs={24} sm={12} lg={8} xl={6} key={assistant.id}>
                  <Card
                    hoverable
                    onClick={() => navigate(`/chat?assistant_id=${assistant.id}`)}
                    style={{
                      border: 'none',
                      borderRadius: 20,
                      overflow: 'hidden',
                      boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
                      transition: 'all 0.3s ease',
                    }}
                    bodyStyle={{ padding: 0 }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(-8px)'
                      ;(e.currentTarget as HTMLElement).style.boxShadow = `0 20px 50px ${colors[0]}25`
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(0)'
                      ;(e.currentTarget as HTMLElement).style.boxShadow = '0 8px 30px rgba(0,0,0,0.08)'
                    }}
                  >
                    {/* Avatar Header */}
                    <div style={{
                      height: 140,
                      background: `linear-gradient(135deg, ${colors[0]} 0%, ${colors[1]} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                    }}>
                      {/* Recommended Badge */}
                      {assistant.is_recommended && (
                        <div style={{
                          position: 'absolute',
                          top: 12,
                          left: 12,
                          background: 'rgba(255,255,255,0.95)',
                          borderRadius: 20,
                          padding: '4px 12px',
                          fontSize: 11,
                          fontWeight: 600,
                          color: colors[0],
                        }}>
                          推荐
                        </div>
                      )}

                      {assistant.avatar ? (
                        <img
                          src={assistant.avatar}
                          alt={assistant.name}
                          style={{
                            width: 88,
                            height: 88,
                            borderRadius: '50%',
                            objectFit: 'cover',
                            border: '4px solid rgba(255,255,255,0.9)',
                            boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
                          }}
                        />
                      ) : (
                        <div style={{
                          width: 88,
                          height: 88,
                          borderRadius: '50%',
                          background: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 36,
                          fontWeight: 700,
                          color: colors[0],
                          boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
                        }}>
                          {assistant.name[0]}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div style={{ padding: '20px 20px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                        <span style={{ fontSize: 18, fontWeight: 700, color: '#1f2937' }}>
                          {assistant.name}
                        </span>
                        <Tag
                          style={{
                            background: `${colors[0]}15`,
                            color: colors[0],
                            border: `1px solid ${colors[0]}30`,
                            borderRadius: 8,
                            fontWeight: 600,
                            fontSize: 12,
                          }}
                        >
                          {assistant.mbti_type}
                        </Tag>
                      </div>

                      <p style={{
                        fontSize: 13,
                        color: '#6b7280',
                        lineHeight: 1.6,
                        marginBottom: 12,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {assistant.speaking_style || assistant.greeting || '一位懂你的AI情感助手'}
                      </p>

                      {assistant.tags && (
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                          {assistant.tags.split(',').slice(0, 3).map((tag: string, i: number) => (
                            <Tag
                              key={i}
                              style={{
                                background: 'rgba(114, 46, 209, 0.1)',
                                color: '#722ED1',
                                borderRadius: 4,
                                fontSize: 11,
                                padding: '2px 8px',
                                border: 'none',
                              }}
                            >
                              {tag.trim()}
                            </Tag>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div style={{
                      display: 'flex',
                      borderTop: '1px solid #f3f4f6',
                    }}>
                      <Button
                        type="text"
                        icon={assistant.is_favorited ? <HeartFilled style={{ color: '#ef4444' }} /> : <HeartOutlined style={{ color: '#6b7280' }} />}
                        onClick={(e) => handleToggleFavorite(assistant, e)}
                        style={{
                          flex: 1,
                          height: 48,
                          borderRadius: 0,
                          color: assistant.is_favorited ? '#ef4444' : '#6b7280',
                          fontSize: 13,
                        }}
                      >
                        {assistant.is_favorited ? '已收藏' : '收藏'}
                      </Button>
                      <Button
                        type="text"
                        icon={<MessageOutlined />}
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/chat?assistant_id=${assistant.id}`)
                        }}
                        style={{
                          flex: 1,
                          height: 48,
                          borderRadius: 0,
                          color: colors[0],
                          fontWeight: 600,
                          fontSize: 13,
                          background: `${colors[0]}10`,
                        }}
                      >
                        开始聊天
                      </Button>
                    </div>
                  </Card>
                </Col>
              )
            })}
          </Row>
        )}

        {filteredAssistants.length === 0 && !loading && (
          <Card
            style={{
              textAlign: 'center',
              padding: '60px 20px',
              border: 'none',
              borderRadius: 20,
            }}
          >
            <RobotOutlined style={{ fontSize: 48, color: '#d1d5db', marginBottom: 16 }} />
            <h3 style={{ color: '#6b7280', marginBottom: 8 }}>暂无匹配的助手</h3>
            <p style={{ color: '#9ca3af', fontSize: 14 }}>试试其他搜索条件或筛选类型</p>
          </Card>
        )}
      </div>
    </div>
  )
}
