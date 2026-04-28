import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, Card, Row, Col, Tag, Dropdown, Space } from 'antd'
import {
  HeartOutlined,
  CalendarOutlined,
  MessageOutlined,
  BookOutlined,
  TeamOutlined,
  UserOutlined,
  SettingOutlined,
  BankOutlined,
  ToolOutlined,
} from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import { useTheme } from '../hooks/useTheme'
import { useHomeUserData } from './home/hooks/useHomeUserData'
import { useMemo } from 'react'
import {
  HeroWelcome,
  TodayInsights,
  MoodStation,
  GrowthMilestone,
  AICompanion,
  DailyQuote,
  CheckInStreak,
} from './home/components'

export default function Home() {
  const navigate = useNavigate()
  const { isAuthenticated, isHydrated, user } = useAuthStore()
  const { themeColor, changeThemeColor, themeColors, toggleTheme, theme } = useTheme()
  const [banners, setBanners] = useState<any[]>([])

  const { moodData, mbtiResult, sbtiResult, attachmentResult, diaryStats, checkinRecords, checkinStats, loading, timeRange, refreshMoodData } = useHomeUserData()

  // Show loading until hydration is complete
  if (!isHydrated) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(180deg, #fafbfc 0%, #f5f7ff 100%)',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>💜</div>
          <div style={{ color: '#6b7280', fontSize: 14 }}>加载中...</div>
        </div>
      </div>
    )
  }

  useEffect(() => {
    loadBanners()
  }, [])

  const loadBanners = useCallback(async () => {
    try {
      const res = await api.knowledge.banners('home')
      setBanners(res.list || [])
    } catch (e) {
      console.error(e)
      setBanners([])
    }
  }, [])

  // 判断用户是否完成测评
  const hasCompletedAssessment = Boolean(mbtiResult)

  // 背景装饰组件
  const FloatingOrb: React.FC<{
    size: number
    gradient: string
    duration?: number
    delay?: number
    style?: React.CSSProperties
  }> = ({ size, gradient, duration = 20, delay = 0, style }) => (
    <div
      style={{
        position: 'absolute',
        width: size,
        height: size,
        borderRadius: '50%',
        background: gradient,
        filter: 'blur(80px)',
        animation: `orbFloat${size} ${duration}s ease-in-out infinite`,
        animationDelay: `${delay}s`,
        ...style,
      }}
    >
      <style>{`@keyframes orbFloat${size} { 0%, 100% { transform: translate(0, 0) scale(1); } 25% { transform: translate(30px, -30px) scale(1.1); } 50% { transform: translate(-20px, 20px) scale(0.9); } 75% { transform: translate(20px, 10px) scale(1.05); } }`}</style>
    </div>
  )

  const AnimatedFloatingParticles: React.FC<{ color: string; count?: number }> = ({
    color,
    count = 20,
  }) => {
    const particles = useMemo(
      () =>
        Array.from({ length: count }, (_, i) => ({
          id: i,
          left: Math.random() * 100,
          top: Math.random() * 100,
          size: 2 + Math.random() * 4,
          opacity: 0.1 + Math.random() * 0.4,
          duration: 15 + Math.random() * 15,
          delay: Math.random() * 5,
        })),
      [count]
    )
    return (
      <div
        style={{
          position: 'absolute',
          inset: 0,
          overflow: 'hidden',
          pointerEvents: 'none',
          zIndex: 1,
        }}
      >
        {particles.map((p) => (
          <div
            key={p.id}
            style={{
              position: 'absolute',
              left: `${p.left}%`,
              top: `${p.top}%`,
              width: p.size,
              height: p.size,
              background: color,
              borderRadius: '50%',
              opacity: 0,
              animation: `floatRise${p.id} ${p.duration}s ease-in-out infinite`,
              animationDelay: `${p.delay}s`,
              boxShadow: `0 0 ${p.size * 2}px ${color}40`,
            }}
          >
            <style>{`@keyframes floatRise${p.id} { 0% { transform: translateY(0) scale(1); opacity: 0; } 10% { opacity: ${p.opacity}; } 90% { opacity: ${p.opacity}; } 100% { transform: translateY(-400px) scale(0.3); opacity: 0; } }`}</style>
          </div>
        ))}
      </div>
    )
  }

  // ==================== 未登录用户首页 ====================
  if (!isAuthenticated) {
    return (
      <div
        className="home"
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden',
          background: `linear-gradient(135deg, #fafbfc 0%, #f5f7ff 100%)`,
        }}
      >
        <FloatingOrb
          size={600}
          gradient={`linear-gradient(135deg, ${themeColors[themeColor]}30 0%, ${themeColors[themeColor]}10 100%)`}
          duration={35}
          delay={0}
          style={{ top: '-15%', left: '-15%' }}
        />
        <FloatingOrb
          size={500}
          gradient={`linear-gradient(135deg, ${themeColors[themeColor]}25 0%, transparent 100%)`}
          duration={28}
          delay={10}
          style={{ top: '40%', right: '-10%' }}
        />
        <AnimatedFloatingParticles color={themeColors[themeColor]} count={40} />

        {/* Header */}
        <header
          style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            padding: '16px 0',
            position: 'sticky',
            top: 0,
            zIndex: 100,
            boxShadow: '0 2px 20px rgba(0, 0, 0, 0.05)',
          }}
        >
          <div
            className="container"
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              maxWidth: '1200px',
              margin: '0 auto',
              padding: '0 24px',
            }}
          >
            <Link to="/" style={{ textDecoration: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '12px',
                    background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
                  }}
                >
                  <HeartOutlined style={{ fontSize: 20 }} />
                </div>
                <h1
                  style={{
                    color: '#1f2937',
                    fontSize: 24,
                    fontWeight: 700,
                    margin: 0,
                    fontFamily: 'Inter, sans-serif',
                  }}
                >
                  心灵伴侣AI
                </h1>
              </div>
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'themeMode',
                      label: (
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            width: '120px',
                          }}
                        >
                          <span>明暗模式</span>
                          <Button type="text" onClick={toggleTheme} style={{ minWidth: 'auto' }}>
                            {theme === 'light' ? '🌙' : '☀️'}
                          </Button>
                        </div>
                      ),
                    },
                    { type: 'divider' },
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
                                  border:
                                    themeColor === key ? '2px solid #1f2937' : '2px solid transparent',
                                  transition: 'all 0.2s ease',
                                }}
                                onClick={() => changeThemeColor(key as any)}
                                onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.1)')}
                                onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
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
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(0, 0, 0, 0.05)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                />
              </Dropdown>
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
                    }}
                  >
                    注册
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section - Landing Page */}
        <section
          style={{
            background: `linear-gradient(135deg, ${themeColors[themeColor]}05 0%, ${themeColors[themeColor]}10 100%)`,
            padding: '80px 0 100px',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              maxWidth: '1200px',
              margin: '0 auto',
              padding: '0 24px',
              position: 'relative',
              zIndex: 1,
            }}
          >
            <div style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
              <Tag
                style={{
                  background: `${themeColors[themeColor]}10`,
                  color: themeColors[themeColor],
                  padding: '6px 16px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: 500,
                  border: `1px solid ${themeColors[themeColor]}20`,
                  marginBottom: 24,
                }}
              >
                <HeartOutlined style={{ marginRight: 6 }} />
                你的AI情感伴侣
              </Tag>

              <h2
                style={{
                  fontSize: 'clamp(32px, 6vw, 48px)',
                  fontWeight: 800,
                  marginBottom: 24,
                  color: '#1f2937',
                  lineHeight: '1.2',
                  fontFamily: 'Inter, sans-serif',
                }}
              >
                与懂你的AI助手
                <br />
                <span style={{ color: themeColors[themeColor], fontWeight: 800 }}>
                  开启心灵之旅
                </span>
              </h2>

              <p
                style={{
                  fontSize: 'clamp(16px, 3vw, 20px)',
                  marginBottom: 40,
                  color: '#6b7280',
                  lineHeight: '1.6',
                }}
              >
                三位一体深度测评：MBTI人格 + SBTI恋爱风格 + 依恋类型
                <br />
                全面认识自己，找到最懂你的AI情感伴侣
              </p>

              {/* 三大测评入口卡片 */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: 16,
                  maxWidth: '800px',
                  margin: '0 auto',
                  width: '100%',
                }}
              >
                <Link to="/mbti" style={{ textDecoration: 'none' }}>
                  <div
                    style={{
                      background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                      borderRadius: '20px',
                      padding: '24px 20px',
                      textAlign: 'center',
                      color: '#fff',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 8px 25px rgba(99, 102, 241, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 35px rgba(99, 102, 241, 0.45)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 8px 25px rgba(99, 102, 241, 0.35)'
                    }}
                  >
                    <div style={{ fontSize: 36, marginBottom: 12 }}>🔱</div>
                    <h4 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6, color: '#fff' }}>
                      MBTI人格测评
                    </h4>
                    <p style={{ fontSize: 12, opacity: 0.9, marginBottom: 0 }}>发现你的性格优势</p>
                  </div>
                </Link>

                <Link to="/sbti" style={{ textDecoration: 'none' }}>
                  <div
                    style={{
                      background: 'linear-gradient(135deg, #f472b6 0%, #ec4899 100%)',
                      borderRadius: '20px',
                      padding: '24px 20px',
                      textAlign: 'center',
                      color: '#fff',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 8px 25px rgba(244, 114, 182, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 35px rgba(244, 114, 182, 0.45)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 8px 25px rgba(244, 114, 182, 0.35)'
                    }}
                  >
                    <div style={{ fontSize: 36, marginBottom: 12 }}>💕</div>
                    <h4 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6, color: '#fff' }}>
                      SBTI恋爱风格
                    </h4>
                    <p style={{ fontSize: 12, opacity: 0.9, marginBottom: 0 }}>找到理想伴侣类型</p>
                  </div>
                </Link>

                <Link to="/attachment" style={{ textDecoration: 'none' }}>
                  <div
                    style={{
                      background: 'linear-gradient(135deg, #34d399 0%, #14b8a6 100%)',
                      borderRadius: '20px',
                      padding: '24px 20px',
                      textAlign: 'center',
                      color: '#fff',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 8px 25px rgba(52, 211, 153, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 35px rgba(52, 211, 153, 0.45)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 8px 25px rgba(52, 211, 153, 0.35)'
                    }}
                  >
                    <div style={{ fontSize: 36, marginBottom: 12 }}>💙</div>
                    <h4 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6, color: '#fff' }}>
                      依恋风格测评
                    </h4>
                    <p style={{ fontSize: 12, opacity: 0.9, marginBottom: 0 }}>认识你的依恋模式</p>
                  </div>
                </Link>
              </div>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: 16,
                  flexWrap: 'wrap',
                  marginTop: 32,
                }}
              >
                <Link to="/register">
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
                    }}
                  >
                    开始探索
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
                    }}
                  >
                    了解更多
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* 功能介绍区块 */}
        <section style={{ padding: '80px 0', background: '#ffffff' }}>
          <div
            style={{
              maxWidth: '1200px',
              margin: '0 auto',
              padding: '0 24px',
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: 60 }}>
              <h2
                style={{
                  fontSize: 'clamp(28px, 4vw, 36px)',
                  fontWeight: 700,
                  marginBottom: 16,
                  color: '#1f2937',
                }}
              >
                核心功能
              </h2>
              <p
                style={{
                  fontSize: '18px',
                  color: '#6b7280',
                  maxWidth: '600px',
                  margin: '0 auto',
                }}
              >
                全方位的情感支持与自我成长工具，助你成为更好的自己
              </p>
            </div>

            <Row gutter={[32, 32]}>
              {[
                {
                  icon: <BankOutlined />,
                  title: 'MBTI人格测试',
                  desc: '16型人格深度解析，了解真实的自己',
                  color: '#6366f1',
                },
                {
                  icon: <ToolOutlined />,
                  title: 'SBTI甜蜜测评',
                  desc: '解读你的恋爱风格，找到理想伴侣',
                  color: '#f472b6',
                },
                {
                  icon: <UserOutlined />,
                  title: '依恋风格测评',
                  desc: '分析你的依恋类型，建立健康关系',
                  color: '#34d399',
                },
                {
                  icon: <CalendarOutlined />,
                  title: '情感日记',
                  desc: '记录心情变化，追踪情绪成长',
                  color: '#f472b6',
                },
                {
                  icon: <MessageOutlined />,
                  title: 'AI情感陪伴',
                  desc: '智能AI助手，24小时倾听与陪伴',
                  color: '#60a5fa',
                },
                {
                  icon: <BookOutlined />,
                  title: '心理知识库',
                  desc: '海量心理学知识，助你自我成长',
                  color: '#fbbf24',
                },
              ].map((feature, index) => (
                <Col xs={24} sm={12} lg={8} key={index}>
                  <Card
                    hoverable
                    style={{
                      borderRadius: 20,
                      border: 'none',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                      height: '100%',
                    }}
                    bodyStyle={{ padding: 28, textAlign: 'center' }}
                  >
                    <div
                      style={{
                        width: 64,
                        height: 64,
                        borderRadius: 16,
                        background: `${feature.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px',
                        fontSize: 28,
                        color: feature.color,
                      }}
                    >
                      {feature.icon}
                    </div>
                    <h3
                      style={{
                        fontSize: 18,
                        fontWeight: 600,
                        marginBottom: 8,
                        color: '#1f2937',
                      }}
                    >
                      {feature.title}
                    </h3>
                    <p
                      style={{
                        fontSize: 14,
                        color: '#6b7280',
                        margin: 0,
                        lineHeight: 1.6,
                      }}
                    >
                      {feature.desc}
                    </p>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </section>

        {/* Footer */}
        <footer
          style={{
            background: '#f9fafb',
            padding: '40px 0',
            textAlign: 'center',
            borderTop: '1px solid #f0f0f0',
          }}
        >
          <p style={{ color: '#9ca3af', fontSize: 14, margin: 0 }}>
            © 2026 心灵伴侣AI · 你的专属情感陪伴助手
          </p>
        </footer>
      </div>
    )
  }

  // ==================== 已登录用户首页 ====================
  return (
    <div
      className="home"
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
        background: `linear-gradient(180deg, #fafbfc 0%, #f5f7ff 100%)`,
      }}
    >
      <FloatingOrb
        size={600}
        gradient={`linear-gradient(135deg, ${themeColors[themeColor]}20 0%, ${themeColors[themeColor]}08 100%)`}
        duration={35}
        delay={0}
        style={{ top: '-15%', left: '-15%' }}
      />
      <FloatingOrb
        size={400}
        gradient={`linear-gradient(135deg, ${themeColors[themeColor]}15 0%, transparent 100%)`}
        duration={25}
        delay={12}
        style={{ bottom: '10%', right: '-5%' }}
      />
      <AnimatedFloatingParticles color={themeColors[themeColor]} count={30} />

      {/* Header */}
      <header
        style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          padding: '16px 0',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          boxShadow: '0 2px 20px rgba(0, 0, 0, 0.05)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 24px',
          }}
        >
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: '12px',
                  background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  boxShadow: `0 4px 15px ${themeColors[themeColor]}40`,
                }}
              >
                <HeartOutlined style={{ fontSize: 20 }} />
              </div>
              <h1
                style={{
                  color: '#1f2937',
                  fontSize: 24,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                心灵伴侣AI
              </h1>
            </div>
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'themeMode',
                    label: (
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          width: '120px',
                        }}
                      >
                        <span>明暗模式</span>
                        <Button type="text" onClick={toggleTheme} style={{ minWidth: 'auto' }}>
                          {theme === 'light' ? '🌙' : '☀️'}
                        </Button>
                      </div>
                    ),
                  },
                  { type: 'divider' },
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
                                border:
                                  themeColor === key ? '2px solid #1f2937' : '2px solid transparent',
                                transition: 'all 0.2s ease',
                              }}
                              onClick={() => changeThemeColor(key as any)}
                              onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.1)')}
                              onMouseLeave={(e) =>
                                (e.currentTarget.style.transform = 'scale(1)')
                              }
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
                }}
              />
            </Dropdown>

            <Link to="/profile">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  borderRadius: '20px',
                  cursor: 'pointer',
                }}
              >
                <UserOutlined style={{ color: themeColors[themeColor] }} />
                <span style={{ color: '#1f2937', fontWeight: 500 }}>
                  {user?.nickname || '个人中心'}
                </span>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ flex: 1, position: 'relative', zIndex: 2 }}>
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '32px 24px 60px',
          }}
        >
          {/* 已测评用户 - 情感化Dashboard */}
          {hasCompletedAssessment ? (
            <>
              {/* 1. Hero欢迎区 */}
              <HeroWelcome />

              {/* 2. 今日专属发现 */}
              <TodayInsights
                moodData={moodData}
                mbtiResult={mbtiResult}
                diaryStats={diaryStats}
              />

              {/* 3. 情绪能量站 */}
              <MoodStation
                moodData={moodData}
                diaryStats={diaryStats}
                checkinRecords={checkinRecords}
                checkinStats={checkinStats}
                timeRange={timeRange}
                onTimeRangeChange={refreshMoodData}
              />

              {/* 4. 成长里程碑 */}
              <GrowthMilestone
                diaryStats={diaryStats}
                checkinRecords={checkinRecords}
                mbtiResult={mbtiResult}
              />

              {/* 5. 打卡激励 */}
              <CheckInStreak streak={checkinStats?.current_streak} />

              {/* 6. AI陪伴推荐 */}
              <AICompanion />

              {/* 7. 今日语录 */}
              <DailyQuote />
            </>
          ) : (
            <>
              {/* 未测评用户 - 引导测评页面 */}

              {/* 欢迎卡片 */}
              <Card
                style={{
                  borderRadius: 24,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                  marginBottom: 32,
                  border: 'none',
                }}
                bodyStyle={{ padding: 32 }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 24,
                    flexWrap: 'wrap',
                  }}
                >
                  <div
                    style={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}99 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 32,
                      color: '#fff',
                      boxShadow: `0 8px 24px ${themeColors[themeColor]}40`,
                    }}
                  >
                    🌟
                  </div>
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <h2
                      style={{
                        fontSize: 24,
                        fontWeight: 700,
                        margin: '0 0 8px',
                        color: '#1f2937',
                      }}
                    >
                      {new Date().getHours() < 12
                        ? '🌤️ 早上好'
                        : new Date().getHours() < 18
                          ? '☀️ 下午好'
                          : '🌙 晚上好'}
                      ，{user?.nickname || '朋友'}
                    </h2>
                    <p style={{ fontSize: 16, color: '#6b7280', margin: 0 }}>
                      完成三大测评，开启你的心灵成长之旅
                    </p>
                  </div>
                </div>
              </Card>

              {/* 三大测评入口 */}
              <div style={{ marginBottom: 32 }}>
                <h3
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    marginBottom: 20,
                    color: '#1f2937',
                  }}
                >
                  🔮 开启你的测评之旅
                </h3>
                <Row gutter={[16, 16]}>
                  {[
                    {
                      icon: '🔱',
                      title: 'MBTI人格测评',
                      desc: '发现你的性格优势与成长点',
                      path: '/mbti',
                      gradient: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                    },
                    {
                      icon: '💕',
                      title: 'SBTI恋爱风格',
                      desc: '解读你的恋爱模式',
                      path: '/sbti',
                      gradient: 'linear-gradient(135deg, #f472b6 0%, #ec4899 100%)',
                    },
                    {
                      icon: '💙',
                      title: '依恋风格测评',
                      desc: '认识你的依恋模式',
                      path: '/attachment',
                      gradient: 'linear-gradient(135deg, #34d399 0%, #14b8a6 100%)',
                    },
                  ].map((item, i) => (
                    <Col xs={24} md={8} key={i}>
                      <Link to={item.path} style={{ textDecoration: 'none' }}>
                        <Card
                          hoverable
                          style={{
                            borderRadius: 20,
                            overflow: 'hidden',
                            boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                          }}
                          bodyStyle={{ padding: 0 }}
                        >
                          <div
                            style={{
                              background: item.gradient,
                              padding: 28,
                              textAlign: 'center',
                              color: '#fff',
                            }}
                          >
                            <div style={{ fontSize: 48, marginBottom: 12 }}>{item.icon}</div>
                            <h4
                              style={{
                                fontSize: 18,
                                fontWeight: 600,
                                marginBottom: 6,
                                color: '#fff',
                              }}
                            >
                              {item.title}
                            </h4>
                            <p style={{ fontSize: 13, opacity: 0.9, margin: 0 }}>{item.desc}</p>
                          </div>
                        </Card>
                      </Link>
                    </Col>
                  ))}
                </Row>
              </div>

              {/* 快捷入口 */}
              <Card
                style={{
                  borderRadius: 24,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                  border: 'none',
                }}
                bodyStyle={{ padding: 24 }}
              >
                <h3
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    marginBottom: 20,
                    color: '#1f2937',
                  }}
                >
                  📝 其他功能
                </h3>
                <Row gutter={[12, 12]}>
                  {[
                    { icon: '📓', title: '写日记', path: '/diary/create', color: '#f472b6' },
                    { icon: '💬', title: 'AI对话', path: '/chat', color: '#60a5fa' },
                    { icon: '📚', title: '知识库', path: '/knowledge', color: '#fbbf24' },
                    { icon: '⚙️', title: '设置', path: '/settings', color: '#9ca3af' },
                  ].map((item, i) => (
                    <Col xs={12} sm={6} key={i}>
                      <Link to={item.path} style={{ textDecoration: 'none' }}>
                        <div
                          style={{
                            padding: '20px 12px',
                            background: `${item.color}10`,
                            borderRadius: 16,
                            textAlign: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-2px)'
                            e.currentTarget.style.boxShadow = `0 4px 12px ${item.color}20`
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)'
                            e.currentTarget.style.boxShadow = 'none'
                          }}
                        >
                          <div style={{ fontSize: 32, marginBottom: 8 }}>{item.icon}</div>
                          <div
                            style={{
                              fontSize: 14,
                              fontWeight: 600,
                              color: '#374151',
                            }}
                          >
                            {item.title}
                          </div>
                        </div>
                      </Link>
                    </Col>
                  ))}
                </Row>
              </Card>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer
        style={{
          background: '#ffffff',
          padding: '24px 0',
          textAlign: 'center',
          borderTop: '1px solid #f0f0f0',
        }}
      >
        <p style={{ color: '#9ca3af', fontSize: 13, margin: 0 }}>
          © 2026 心灵伴侣AI · 你的专属情感陪伴助手
        </p>
      </footer>
    </div>
  )
}
