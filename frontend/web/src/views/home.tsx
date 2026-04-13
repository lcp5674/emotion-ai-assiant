import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, Card, Row, Col, Tag, Alert, Dropdown, Space } from 'antd'
import { HeartOutlined, CalendarOutlined, MessageOutlined, BookOutlined, TeamOutlined, UserOutlined, PhoneOutlined, WarningOutlined, ShakeOutlined, BankOutlined, ToolOutlined, SettingOutlined, ColorPickerOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import { useTheme } from '../hooks/useTheme'

const { Meta } = Card

export default function Home() {
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()
  const { themeColor, changeThemeColor, themeColors, toggleTheme, theme } = useTheme()
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
      // 后端服务不可用时，使用默认横幅数据
      setBanners([])
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: <BankOutlined />,
      title: 'MBTI人格测试',
      desc: '专业48题MBTI测试，了解真实的自己',
      path: '/mbti',
      tag: '推荐',
      gradient: ['#6366f1', '#a855f7'],
    },
    {
      icon: <ToolOutlined />,
      title: '情感日记',
      desc: '记录心情变化，追踪情绪成长',
      path: '/diary',
      tag: '新功能',
      gradient: ['#f472b6', '#ec4899'],
    },
    {
      icon: <MessageOutlined />,
      title: 'AI情感陪伴',
      desc: '智能AI助手，24小时倾听与陪伴',
      path: '/assistants',
      gradient: ['#60a5fa', '#22d3ee'],
    },
    {
      icon: <BookOutlined />,
      title: '心理知识库',
      desc: '海量心理学知识，助你自我成长',
      path: '/knowledge',
      gradient: ['#fbbf24', '#f97316'],
    },
    {
      icon: <TeamOutlined />,
      title: '助手广场',
      desc: '选择你喜欢的AI情感助手',
      path: '/assistants',
      gradient: ['#34d399', '#14b8a6'],
    },
  ]

  return (
    <div className="home" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        padding: '16px 0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 2px 20px rgba(0, 0, 0, 0.05)',
        transition: 'all 0.3s ease',
      }}>
        <div className="container" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
        }}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 40,
                height: 40,
                borderRadius: '12px',
                background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
              }}>
                <HeartOutlined style={{ fontSize: 20 }} />
              </div>
              <h1 style={{ color: '#1f2937', fontSize: 24, fontWeight: 700, margin: 0, fontFamily: 'Inter, sans-serif' }}>
                心灵伴侣AI
              </h1>
            </div>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* 主题设置 */}
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'themeMode',
                    label: (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '120px' }}>
                        <span>明暗模式</span>
                        <Button
                          type="text"
                          onClick={toggleTheme}
                          style={{ minWidth: 'auto' }}
                        >
                          {theme === 'light' ? '🌙' : '☀️'}
                        </Button>
                      </div>
                    ),
                  },
                  {
                    type: 'divider',
                  },
                  {
                    key: 'themeColor',
                    label: (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <span>主题颜色</span>
                        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                          {Object.entries(themeColors).map(([key, color]) => (
                            <div
                              key={key}
                              style={{
                                width: 24,
                                height: 24,
                                borderRadius: '50%',
                                background: color,
                                cursor: 'pointer',
                                border: themeColor === key ? '2px solid #1f2937' : '2px solid transparent',
                                transition: 'all 0.2s ease',
                              }}
                              onClick={() => changeThemeColor(key as any)}
                              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            />
                          ))}
                        </div>
                      </div>
                    ),
                  },
                ],
              }}
              trigger={['click']}
            >
              <Button
                type="text"
                icon={<SettingOutlined />}
                style={{
                  color: '#1f2937',
                  fontSize: 18,
                  padding: 8,
                  borderRadius: '50%',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.05)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              />
            </Dropdown>

            {isAuthenticated ? (
              <Link to="/profile">
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  borderRadius: '20px',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                }} onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.05)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                  <UserOutlined style={{ color: themeColors[themeColor] }} />
                  <span style={{ color: '#1f2937', fontWeight: 500 }}>
                    {user?.nickname || '个人中心'}
                  </span>
                </div>
              </Link>
            ) : (
              <div style={{ display: 'flex', gap: 12 }}>
                <Link to="/login">
                  <Button
                    style={{
                      background: 'transparent',
                      color: themeColors[themeColor],
                      border: `1px solid ${themeColors[themeColor]}20`,
                      borderRadius: '20px',
                      padding: '8px 24px',
                      fontWeight: 500,
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = `${themeColors[themeColor]}10`;
                      e.currentTarget.style.borderColor = `${themeColors[themeColor]}40`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.borderColor = `${themeColors[themeColor]}20`;
                    }}
                  >
                    登录
                  </Button>
                </Link>
                <Link to="/register">
                  <Button
                    style={{
                      background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                      color: '#fff',
                      border: 'none',
                      borderRadius: '20px',
                      padding: '8px 24px',
                      fontWeight: 500,
                      boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = `0 6px 20px ${themeColors[themeColor]}60`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = `0 4px 15px ${themeColors[themeColor]}40`;
                    }}
                  >
                    注册
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        background: `linear-gradient(135deg, ${themeColors[themeColor]}05 0%, ${themeColors[themeColor]}10 100%)`,
        padding: '80px 0 120px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background Elements */}
        <div style={{
          position: 'absolute',
          top: '-50%',
          right: '-20%',
          width: '60%',
          height: '200%',
          background: `radial-gradient(circle, ${themeColors[themeColor]}10 0%, transparent 70%)`,
          borderRadius: '50%',
          zIndex: 0,
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-40%',
          left: '-10%',
          width: '40%',
          height: '150%',
          background: `radial-gradient(circle, ${themeColors[themeColor]}10 0%, transparent 70%)`,
          borderRadius: '50%',
          zIndex: 0,
        }} />

        <div className="container" style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
          position: 'relative',
          zIndex: 1,
        }}>
          <div style={{
            textAlign: 'center',
            maxWidth: '800px',
            margin: '0 auto',
          }}>
            <div style={{ marginBottom: 24 }}>
              <Tag
                style={{
                  background: `${themeColors[themeColor]}10`,
                  color: themeColors[themeColor],
                  padding: '6px 16px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: 500,
                  border: `1px solid ${themeColors[themeColor]}20`,
                }}
              >
                <ShakeOutlined style={{ marginRight: 6 }} />
                你的AI情感伴侣
              </Tag>
            </div>
            <h2 style={{
              fontSize: 'clamp(32px, 6vw, 48px)',
              fontWeight: 800,
              marginBottom: 24,
              color: '#1f2937',
              lineHeight: '1.2',
              fontFamily: 'Inter, sans-serif',
            }}>
              与懂你的AI助手<br />
              <span style={{ 
                color: themeColors[themeColor],
                fontWeight: 800
              }}>
                开启心灵之旅
              </span>
            </h2>
            <p style={{
              fontSize: 'clamp(16px, 3vw, 20px)',
              marginBottom: 40,
              color: '#6b7280',
              lineHeight: '1.6',
            }}>
              基于MBTI人格测试，匹配最适合你的AI情感助手
              随时随地倾听你的心声，陪伴你成长
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
              <Link to="/mbti">
                <Button
                  size="large"
                  style={{
                    background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                    color: '#fff',
                    border: 'none',
                    borderRadius: '28px',
                    padding: '12px 40px',
                    fontSize: '16px',
                    fontWeight: 600,
                    boxShadow: `0 6px 20px ${themeColors[themeColor]}40`,
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-3px)';
                    e.currentTarget.style.boxShadow = `0 8px 25px ${themeColors[themeColor]}50`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = `0 6px 20px ${themeColors[themeColor]}40`;
                  }}
                >
                  开始测试
                </Button>
              </Link>
              <Link to="/assistants">
                <Button
                  size="large"
                  style={{
                    background: '#fff',
                    color: '#1f2937',
                    border: `1px solid ${themeColors[themeColor]}20`,
                    borderRadius: '28px',
                    padding: '12px 40px',
                    fontSize: '16px',
                    fontWeight: 600,
                    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-3px)';
                    e.currentTarget.style.boxShadow = `0 4px 15px ${themeColors[themeColor]}20`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
                  }}
                >
                  探索助手
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '100px 0', background: '#fff' }}>
        <div className="container" style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
        }}>
          <div style={{ textAlign: 'center', marginBottom: 60 }}>
            <h2 style={{
              fontSize: 'clamp(28px, 4vw, 36px)',
              fontWeight: 700,
              marginBottom: 16,
              color: '#1f2937',
              fontFamily: 'Inter, sans-serif',
            }}>
              核心功能
            </h2>
            <p style={{
              fontSize: '18px',
              color: '#6b7280',
              maxWidth: '600px',
              margin: '0 auto',
            }}>
              全方位的情感支持与自我成长工具，助你成为更好的自己
            </p>
          </div>
          <Row gutter={[32, 32]}>
            {features.map((feature, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card
                  hoverable
                  onClick={() => navigate(feature.path)}
                  style={{
                    textAlign: 'center',
                    height: '100%',
                    border: 'none',
                    borderRadius: '20px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
                    transition: 'all 0.3s ease',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-10px)';
                    e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.05)';
                  }}
                >
                  <div style={{ marginBottom: 24, position: 'relative' }}>
                    <div style={{
                      width: 80,
                      height: 80,
                      borderRadius: '20px',
                      background: `linear-gradient(135deg, ${feature.gradient[0]} 0%, ${feature.gradient[1]} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                      fontSize: 32,
                      margin: '0 auto 16px',
                      boxShadow: `0 8px 25px ${feature.gradient[0]}40`,
                      transition: 'all 0.3s ease',
                    }}>
                      {feature.icon}
                    </div>
                    {feature.tag && (
                      <Tag
                        color={feature.tag === '新功能' ? 'red' : 'orange'}
                        style={{
                          position: 'absolute',
                          top: 12,
                          right: 12,
                          borderRadius: '12px',
                          padding: '4px 12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}
                      >
                        {feature.tag}
                      </Tag>
                    )}
                  </div>
                  <Meta
                    title={
                      <h3 style={{
                        fontSize: '18px',
                        fontWeight: 600,
                        marginBottom: 8,
                        color: '#1f2937',
                      }}>
                        {feature.title}
                      </h3>
                    }
                    description={
                      <p style={{
                        fontSize: '14px',
                        color: '#6b7280',
                        lineHeight: '1.5',
                      }}>
                        {feature.desc}
                      </p>
                    }
                  />
                  <div style={{ marginTop: 20 }}>
                    <div style={{
                      display: 'inline-block',
                      padding: '6px 16px',
                      borderRadius: '16px',
                      background: `${themeColors[themeColor]}05`,
                      color: themeColors[themeColor],
                      fontSize: '12px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }} onMouseEnter={(e) => e.currentTarget.style.background = `${themeColors[themeColor]}10`}>
                      了解更多 →
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* MBTI Banner */}
      <section style={{ padding: '80px 0', background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%)' }}>
        <div className="container" style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
        }}>
          <Card
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '24px',
              border: 'none',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.05)',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            {/* Background Pattern */}
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              width: '50%',
              height: '100%',
              background: `radial-gradient(circle at top right, ${themeColors[themeColor]}10 0%, transparent 70%)`,
              zIndex: 0,
            }} />
            <Row align="middle" gutter={[48, 24]} style={{ position: 'relative', zIndex: 1 }}>
              <Col xs={24} md={16}>
                <div style={{}}>
                  <h3 style={{
                    fontSize: 'clamp(20px, 3vw, 28px)',
                    fontWeight: 700,
                    marginBottom: 12,
                    color: '#1f2937',
                    fontFamily: 'Inter, sans-serif',
                  }}>
                    还没有做过MBTI测试？
                  </h3>
                  <p style={{
                    fontSize: '16px',
                    color: '#6b7280',
                    marginBottom: 24,
                    lineHeight: '1.6',
                  }}>
                    只需3分钟，了解你的性格特点，匹配最适合你的AI情感助手
                    开启个性化的情感支持之旅
                  </p>
                  <Link to="/mbti">
                    <Button
                    type="primary"
                    size="large"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                      color: '#fff',
                      border: 'none',
                      borderRadius: '24px',
                      padding: '12px 32px',
                      fontSize: '16px',
                      fontWeight: 600,
                      boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
                      transition: 'all 0.3s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = `0 6px 20px ${themeColors[themeColor]}60`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = `0 4px 15px ${themeColors[themeColor]}40`;
                    }}
                  >
                    立即测试
                  </Button>
                  </Link>
                </div>
              </Col>
              <Col xs={24} md={8} style={{ textAlign: 'center' }}>
                <div style={{}}>
                  <div style={{
                    width: 160,
                    height: 160,
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 64,
                    boxShadow: `0 10px 30px ${themeColors[themeColor]}40`,
                    position: 'relative',
                    overflow: 'hidden',
                  }}>
                    <HeartOutlined />
                    {/* Animation effect */}
                    <div style={{
                      position: 'absolute',
                      top: '-50%',
                      left: '-50%',
                      width: '200%',
                      height: '200%',
                      background: 'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%)',
                      transform: 'rotate(0deg)',
                    }} />
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </div>
      </section>

      {/* Crisis Intervention Banner */}
      {isAuthenticated && (
        <section style={{ padding: '32px 0' }}>
          <div className="container" style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 24px',
          }}>
            <Alert
              message="如果你正在经历心理危机，请立即寻求帮助"
              description="这里有专业的危机干预资源，随时为你提供帮助"
              type="warning"
              showIcon
              icon={<WarningOutlined />}
              style={{
                borderRadius: '12px',
                border: '1px solid #fde68a',
                background: '#fef3c7',
              }}
              action={
                <Button
                  danger
                  size="small"
                  icon={<PhoneOutlined />}
                  onClick={() => navigate('/crisis')}
                  style={{
                    borderRadius: '16px',
                    fontWeight: 500,
                  }}
                >
                  查看求助资源
                </Button>
              }
            />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer style={{
        background: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)',
        padding: '60px 0 40px',
        color: '#9ca3af',
        marginTop: 'auto',
      }}>
        <div className="container" style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 40 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{
                width: 48,
                height: 48,
                borderRadius: '12px',
                background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}>
                <HeartOutlined style={{ fontSize: 24 }} />
              </div>
              <h2 style={{ color: '#fff', fontSize: 28, fontWeight: 700, margin: 0, fontFamily: 'Inter, sans-serif' }}>
                心灵伴侣AI
              </h2>
            </div>
            <p style={{ textAlign: 'center', maxWidth: '600px', margin: 0, lineHeight: '1.6' }}>
              用AI科技，守护你的心理健康，陪伴你每一步成长
            </p>
          </div>
          <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: 32, textAlign: 'center' }}>
            <p style={{ marginBottom: 16 }}>© 2026 心灵伴侣AI - 你的AI情感助手</p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 24, flexWrap: 'wrap' }}>
              <Link to="/privacy" style={{ color: '#9ca3af', textDecoration: 'none', transition: 'color 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}>
                隐私政策
              </Link>
              <Link to="/crisis" style={{ color: '#9ca3af', textDecoration: 'none', transition: 'color 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}>
                危机求助
              </Link>
              <Link to="/knowledge" style={{ color: '#9ca3af', textDecoration: 'none', transition: 'color 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}>
                知识库
              </Link>
              <Link to="/assistants" style={{ color: '#9ca3af', textDecoration: 'none', transition: 'color 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}>
                助手广场
              </Link>
            </div>
          </div>
        </div>
      </footer>


    </div>
  )
}
