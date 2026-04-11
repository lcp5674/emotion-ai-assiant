import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, Carousel, Card, Row, Col, Spin, Tag, Alert } from 'antd'
import { HeartOutlined, TeamOutlined, BookOutlined, MessageOutlined, UserOutlined, CalendarOutlined, PhoneOutlined, WarningOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'

const { Meta } = Card

export default function Home() {
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()
  const [banners, setBanners] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBanners()
  }, [])

  const loadBanners = async () => {
    try {
      const res = await api.knowledge.banners('home')
      setBanners(res.list || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: <HeartOutlined style={{ fontSize: 40, color: '#722ed1' }} />,
      title: 'MBTI人格测试',
      desc: '专业48题MBTI测试，了解真实的自己',
      path: '/mbti',
      tag: '推荐',
    },
    {
      icon: <CalendarOutlined style={{ fontSize: 40, color: '#722ed1' }} />,
      title: '情感日记',
      desc: '记录心情变化，追踪情绪成长',
      path: '/diary',
      tag: '新功能',
    },
    {
      icon: <MessageOutlined style={{ fontSize: 40, color: '#722ed1' }} />,
      title: 'AI情感陪伴',
      desc: '智能AI助手，24小时倾听与陪伴',
      path: '/assistants',
    },
    {
      icon: <BookOutlined style={{ fontSize: 40, color: '#722ed1' }} />,
      title: '心理知识库',
      desc: '海量心理学知识，助你自我成长',
      path: '/knowledge',
    },
    {
      icon: <TeamOutlined style={{ fontSize: 40, color: '#722ed1' }} />,
      title: '助手广场',
      desc: '选择你喜欢的AI情感助手',
      path: '/assistants',
    },
  ]

  return (
    <div className="home">
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '16px 0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <h1 style={{ color: '#fff', fontSize: 24, margin: 0 }}>
            心灵伴侣AI
          </h1>
          <div>
            {isAuthenticated ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <Link to="/profile">
                  <Button type="text" icon={<UserOutlined />} style={{ color: '#fff' }}>
                    {user?.nickname || '个人中心'}
                  </Button>
                </Link>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: 12 }}>
                <Link to="/login">
                  <Button ghost style={{ color: '#fff', borderColor: '#fff' }}>登录</Button>
                </Link>
                <Link to="/register">
                  <Button style={{ background: '#fff', color: '#722ed1' }}>注册</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '60px 0 100px',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <h2 style={{ fontSize: 'clamp(28px, 5vw, 42px)', marginBottom: 16 }}>
            你的AI情感伴侣
          </h2>
          <p style={{ fontSize: 'clamp(16px, 3vw, 18px)', marginBottom: 32, opacity: 0.9 }}>
            基于MBTI人格测试，匹配最适合你的AI助手<br />
            随时随地倾听你的心声，陪伴你成长
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
            <Link to="/mbti">
              <Button size="large" style={{ background: '#fff', color: '#722ed1', height: 48, paddingInline: 32 }}>
                开始测试
              </Button>
            </Link>
            <Link to="/assistants">
              <Button size="large" ghost style={{ borderColor: '#fff', color: '#fff', height: 48, paddingInline: 32 }}>
                了解更多
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '60px 0', background: '#fafafa' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: 40, fontSize: 'clamp(24px, 4vw, 28px)' }}>
            核心功能
          </h2>
          <Row gutter={[24, 24]}>
            {features.map((feature, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card
                  hoverable
                  onClick={() => navigate(feature.path)}
                  style={{ textAlign: 'center', height: '100%' }}
                >
                  <div style={{ marginBottom: 16, position: 'relative' }}>
                    {feature.icon}
                    {feature.tag && (
                      <Tag color={feature.tag === '新功能' ? 'red' : 'orange'} style={{ position: 'absolute', top: 12, right: 12 }}>
                        {feature.tag}
                      </Tag>
                    )}
                  </div>
                  <Meta title={feature.title} description={feature.desc} />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* MBTI Banner */}
      <section style={{ padding: '60px 0' }}>
        <div className="container">
          <Card
            style={{
              background: 'linear-gradient(135deg, #fff0f6 0%, #ffd6e7 100%)',
              border: 'none',
            }}
          >
            <Row align="middle" gutter={[24, 16]}>
              <Col flex="auto">
                <h3 style={{ fontSize: 24, marginBottom: 8 }}>还没有做过MBTI测试？</h3>
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  只需3分钟，了解你的性格特点，匹配最适合你的AI情感助手
                </p>
                <Link to="/mbti">
                  <Button type="primary" size="large">
                    立即测试
                  </Button>
                </Link>
              </Col>
              <Col xs={24} sm={6} style={{ textAlign: 'center' }}>
                <div style={{
                  width: 120,
                  height: 120,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 48,
                }}>
                  <HeartOutlined />
                </div>
              </Col>
            </Row>
          </Card>
        </div>
      </section>

      {/* Crisis Intervention Banner */}
      {isAuthenticated && (
        <section style={{ padding: '24px 0' }}>
          <div className="container">
            <Alert
              message="如果你正在经历心理危机，请立即寻求帮助"
              description="这里有专业的危机干预资源，随时为你提供帮助"
              type="warning"
              showIcon
              icon={<WarningOutlined />}
              action={
                <Button danger size="small" icon={<PhoneOutlined />} onClick={() => navigate('/crisis')}>
                  查看求助资源
                </Button>
              }
            />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer style={{
        background: '#262626',
        padding: '40px 0',
        color: '#8c8c8c',
        textAlign: 'center',
      }}>
        <div className="container">
          <p>© 2024 心灵伴侣AI - 你的AI情感助手</p>
          <div style={{ marginTop: 16 }}>
            <Link to="/privacy" style={{ color: '#8c8c8c', marginRight: 16 }}>
              隐私政策
            </Link>
            <span>|</span>
            <Link to="/crisis" style={{ color: '#8c8c8c', marginLeft: 16 }}>
              危机求助
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
