import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Tag, Input, Spin, Button, App } from 'antd'
import { SearchOutlined, HeartOutlined, MessageOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { api } from '../api/request'

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
}

export default function AssistantSquare() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [assistants, setAssistants] = useState<Assistant[]>([])
  const [loading, setLoading] = useState(true)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedMbti, setSelectedMbti] = useState<string | null>(null)

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
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <h1 style={{ fontSize: 36, marginBottom: 8 }}>AI助手广场</h1>
          <p style={{ fontSize: 18, opacity: 0.9 }}>
            选择你喜欢的AI情感助手，开启温暖对话
          </p>
        </div>
      </header>

      <div className="container" style={{ padding: '24px 16px' }}>
        <div style={{ marginBottom: 16 }}>
          <Link to="/">
            <Button icon={<ArrowLeftOutlined />}>返回首页</Button>
          </Link>
        </div>

        {/* Search & Filter */}
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} md={8}>
              <Input
                placeholder="搜索助手..."
                prefix={<SearchOutlined />}
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                allowClear
              />
            </Col>
            <Col xs={24} md={16}>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Tag
                  onClick={() => setSelectedMbti(null)}
                  style={{ cursor: 'pointer' }}
                  color={selectedMbti === null ? '#722ed1' : 'default'}
                >
                  全部
                </Tag>
                {mbtiTypes.map(mbti => (
                  <Tag
                    key={mbti}
                    onClick={() => setSelectedMbti(mbti)}
                    style={{ cursor: 'pointer' }}
                    color={selectedMbti === mbti ? '#722ed1' : 'default'}
                  >
                    {mbti}
                  </Tag>
                ))}
              </div>
            </Col>
          </Row>
        </Card>

        {/* Assistants Grid */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
          </div>
        ) : (
          <Row gutter={[24, 24]}>
            {filteredAssistants.map((assistant) => (
              <Col xs={24} sm={12} lg={8} xl={6} key={assistant.id}>
                <Card
                  hoverable
                  cover={
                    <div style={{
                      height: 120,
                      background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {assistant.avatar ? (
                        <img 
                          src={assistant.avatar} 
                          alt={assistant.name}
                          style={{
                            width: 80,
                            height: 80,
                            borderRadius: '50%',
                            objectFit: 'cover',
                            border: '3px solid #fff',
                          }}
                        />
                      ) : (
                        <div style={{
                          width: 80,
                          height: 80,
                          borderRadius: '50%',
                          background: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 32,
                          color: '#722ed1',
                          fontWeight: 'bold',
                        }}>
                          {assistant.name[0]}
                        </div>
                      )}
                    </div>
                  }
                  actions={[
                    <Button
                      type="text"
                      icon={<HeartOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        message.success('已添加到收藏')
                      }}
                    >
                      收藏
                    </Button>,
                    <Button
                      type="text"
                      icon={<MessageOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/chat?assistant_id=${assistant.id}`)
                      }}
                    >
                      聊天
                    </Button>,
                  ]}
                >
                  <Card.Meta
                    title={
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {assistant.name}
                        <Tag color="purple">{assistant.mbti_type}</Tag>
                      </div>
                    }
                    description={
                      <div>
                        <p style={{ marginBottom: 8, color: '#8c8c8c' }}>
                          {assistant.speaking_style?.slice(0, 60)}...
                        </p>
                        {assistant.tags && (
                          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                            {assistant.tags.split(',').slice(0, 3).map((tag: string, i: number) => (
                              <Tag key={i}>{tag}</Tag>
                            ))}
                          </div>
                        )}
                      </div>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        )}

        {filteredAssistants.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: 60, color: '#8c8c8c' }}>
            暂无匹配的助手
          </div>
        )}
      </div>

      {/* Back to home */}
      <div style={{ textAlign: 'center', padding: 24 }}>
        <Link to="/">
          <Button>返回首页</Button>
        </Link>
      </div>
    </div>
  )
}