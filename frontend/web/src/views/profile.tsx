import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Button, Avatar, Tag, Spin, List, App, Modal } from 'antd'
import { UserOutlined, SettingOutlined, LogoutOutlined, MessageOutlined, HeartOutlined, CalendarOutlined, CrownOutlined, StarOutlined, BookOutlined, TrophyOutlined, RightOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import { useTheme } from '../hooks/useTheme'
import PaymentPage from './payment'

export default function Profile() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { user, logout, updateUser } = useAuthStore()
  const { themeColors, themeColor } = useTheme()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [paymentModalVisible, setPaymentModalVisible] = useState(false)
  const [currentMembership, setCurrentMembership] = useState<any>(null)

  const themeGradient = themeColors[themeColor]

  useEffect(() => {
    loadStats()
    if (user?.member_level !== 'free') {
      loadCurrentMembership()
    }
  }, [])

  const loadStats = async () => {
    try {
      const [profileRes, statsRes] = await Promise.all([
        api.user.profile(),
        api.user.stats()
      ])
      // 同步用户数据到 auth store
      updateUser(profileRes)
      setStats({
        ...profileRes,
        ...statsRes
      })
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentMembership = async () => {
    try {
      const res = await api.payment.currentMembership()
      setCurrentMembership(res)
    } catch (error) {
      console.error('获取会员信息失败', error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
    message.success('已退出登录')
  }

  const openMembershipModal = async () => {
    setPaymentModalVisible(true)
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: '#f8fafc',
      }}>
        <Spin size="large" />
      </div>
    )
  }

  const getMemberLevelText = () => {
    if (!user || user.member_level === 'free') return '免费'
    return user.member_level
  }

  const menuItems = [
    { icon: <MessageOutlined />, title: '我的对话', path: '/chat', gradient: ['#6366f1', '#8b5cf6'] },
    { icon: <CalendarOutlined />, title: '情感日记', path: '/diary', gradient: ['#ec4899', '#f472b6'] },
    { icon: <BookOutlined />, title: '我的收藏', path: '/knowledge/collections', gradient: ['#f59e0b', '#fbbf24'] },
    { icon: <TrophyOutlined />, title: '成长成就', path: '/achievements', gradient: ['#fbbf24', '#f59e0b'] },
    { icon: <StarOutlined />, title: '深度画像', path: '/profile/deep', gradient: ['#8b5cf6', '#c084fc'] },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {/* Header with Gradient */}
      <header style={{
        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
        padding: '48px 24px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background Pattern */}
        <div style={{
          position: 'absolute',
          top: '-50%',
          right: '-20%',
          width: '60%',
          height: '200%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            width: 96,
            height: 96,
            borderRadius: '24px',
            background: 'rgba(255,255,255,0.2)',
            backdropFilter: 'blur(10px)',
            margin: '0 auto 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '3px solid rgba(255,255,255,0.3)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
          }}>
            {user?.avatar ? (
              <Avatar src={user.avatar} size={88} />
            ) : (
              <UserOutlined style={{ fontSize: 40, color: '#fff' }} />
            )}
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 8, fontWeight: 700 }}>
            {stats?.nickname || '用户'}
          </h1>
          <p style={{ opacity: 0.9, fontSize: 15 }}>{stats?.phone}</p>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginTop: 16 }}>
            {stats?.mbti_type && (
              <Tag
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  color: '#fff',
                  borderRadius: 20,
                  padding: '4px 16px',
                }}
              >
                {user.mbti_type}
              </Tag>
            )}
            {stats?.member_level && stats.member_level !== 'free' && (
              <Tag
                icon={<CrownOutlined />}
                style={{
                  background: 'linear-gradient(135deg, #ffd700 0%, #ffb700 100%)',
                  border: 'none',
                  color: '#fff',
                  borderRadius: 20,
                  padding: '4px 16px',
                }}
              >
                {user.member_level}会员
              </Tag>
            )}
          </div>
        </div>
      </header>

      <div style={{ maxWidth: 800, margin: '-30px auto 0', padding: '0 16px 40px', position: 'relative', zIndex: 2 }}>
        {/* Membership Banner */}
        {(!currentMembership || currentMembership.level === 'free') && (
          <Card
            style={{
              marginBottom: 20,
              background: 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)',
              border: 'none',
              borderRadius: 20,
              boxShadow: '0 8px 30px rgba(250, 140, 22, 0.2)',
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Row align="middle" gutter={[16, 16]}>
              <Col flex="auto">
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 48,
                    height: 48,
                    borderRadius: '14px',
                    background: 'linear-gradient(135deg, #fa8c16 0%, #ffc53d 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <CrownOutlined style={{ fontSize: 24, color: '#fff' }} />
                  </div>
                  <div>
                    <h3 style={{ margin: 0, color: '#d46b00', fontWeight: 600, fontSize: 16 }}>
                      升级VIP会员
                    </h3>
                    <p style={{ margin: '4px 0 0 0', color: '#fa8c16', fontSize: 13, opacity: 0.8 }}>
                      ✅ 无限对话 · ✅ 高级AI模型 · ✅ 深度人格分析
                    </p>
                  </div>
                </div>
              </Col>
              <Col>
                <Button
                  type="primary"
                  style={{
                    background: 'linear-gradient(135deg, #fa8c16 0%, #ffc53d 100%)',
                    border: 'none',
                    borderRadius: 14,
                    height: 40,
                    fontWeight: 600,
                  }}
                  onClick={openMembershipModal}
                >
                  立即升级
                </Button>
              </Col>
            </Row>
          </Card>
        )}

        {currentMembership && currentMembership.level !== 'free' && (
          <Card
            style={{
              marginBottom: 20,
              background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
              border: 'none',
              borderRadius: 20,
              boxShadow: '0 8px 30px rgba(82, 196, 26, 0.2)',
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Row align="middle" gutter={[16, 16]}>
              <Col flex="auto">
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 48,
                    height: 48,
                    borderRadius: '14px',
                    background: 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <CrownOutlined style={{ fontSize: 24, color: '#fff' }} />
                  </div>
                  <div>
                    <h3 style={{ margin: 0, color: '#389e0d', fontWeight: 600, fontSize: 16 }}>
                      {currentMembership.plan_name}会员
                    </h3>
                    <p style={{ margin: '4px 0 0 0', color: '#52c41a', fontSize: 13, opacity: 0.8 }}>
                      有效期至 {currentMembership.expires_at}
                    </p>
                  </div>
                </div>
              </Col>
              <Col>
                <Button
                  style={{
                    background: '#fff',
                    border: '1px solid #52c41a',
                    borderRadius: 14,
                    height: 40,
                    color: '#52c41a',
                    fontWeight: 600,
                  }}
                  onClick={openMembershipModal}
                >
                  续费
                </Button>
              </Col>
            </Row>
          </Card>
        )}

        {/* Stats Cards - 对齐的统计卡片 */}
        <Row gutter={[12, 12]} style={{ marginBottom: 20 }} justify="center">
          <Col xs={8}>
            <Card
              style={{
                textAlign: 'center',
                border: 'none',
                borderRadius: 16,
                boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
              }}
              bodyStyle={{ padding: '16px 8px' }}
            >
              <div style={{
                fontSize: 28,
                fontWeight: 700,
                color: '#1f2937',
                marginBottom: 4,
                textShadow: '0 1px 2px rgba(0,0,0,0.1)',
              }}>
                {stats?.conversation_count || 0}
              </div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>对话数</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card
              style={{
                textAlign: 'center',
                border: 'none',
                borderRadius: 16,
                boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
              }}
              bodyStyle={{ padding: '16px 8px' }}
            >
              <div style={{
                fontSize: 28,
                fontWeight: 700,
                color: '#1f2937',
                marginBottom: 4,
                textShadow: '0 1px 2px rgba(0,0,0,0.1)',
              }}>
                {stats?.mbti_test_count || 0}
              </div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>测试次数</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card
              style={{
                textAlign: 'center',
                border: 'none',
                borderRadius: 16,
                cursor: 'pointer',
                boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                background: stats?.member && stats.member.level !== 'free' 
                  ? 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)' 
                  : 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
              }}
              bodyStyle={{ padding: '16px 8px' }}
              onClick={openMembershipModal}
            >
              <div style={{
                fontSize: 28,
                fontWeight: 700,
                color: '#1f2937',
                marginBottom: 4,
                textShadow: '0 1px 2px rgba(0,0,0,0.1)',
              }}>
                {stats?.member?.level && stats.member.level !== 'free' ? stats.member.level : '免费'}
              </div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>会员等级</div>
            </Card>
          </Col>
        </Row>

        {/* Menu Cards */}
        <Card
          style={{
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
            overflow: 'hidden',
          }}
          bodyStyle={{ padding: 0 }}
        >
          {menuItems.map((item, idx) => (
            <div
              key={idx}
              onClick={() => navigate(item.path)}
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                borderBottom: idx < menuItems.length - 1 ? '1px solid #f0f0f0' : 'none',
                transition: 'all 0.2s ease',
                background: '#fff',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = '#f8fafc'
                ;(e.currentTarget as HTMLElement).style.paddingLeft = '24px'
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = '#fff'
                ;(e.currentTarget as HTMLElement).style.paddingLeft = '20px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: '12px',
                  background: `linear-gradient(135deg, ${item.gradient[0]} 0%, ${item.gradient[1]} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 18,
                }}>
                  {item.icon}
                </div>
                <span style={{ fontSize: 15, fontWeight: 500, color: '#1f2937' }}>
                  {item.title}
                </span>
              </div>
              <RightOutlined style={{ color: '#9ca3af', fontSize: 12 }} />
            </div>
          ))}
        </Card>

        {/* Settings & Admin */}
        <Card
          style={{
            marginTop: 16,
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
            overflow: 'hidden',
          }}
          bodyStyle={{ padding: 0 }}
        >
          {[
            { icon: <SettingOutlined />, title: '账户设置', path: '/settings', gradient: ['#64748b', '#94a3b8'] },
            ...(stats?.is_admin ? [{ icon: <SettingOutlined />, title: '系统管理', path: '/admin', gradient: ['#ef4444', '#f87171'] }] : []),
          ].map((item, idx) => (
            <div
              key={idx}
              onClick={() => navigate(item.path)}
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                borderBottom: idx < 1 ? '1px solid #f0f0f0' : 'none',
                transition: 'all 0.2s ease',
                background: '#fff',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = '#f8fafc'
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = '#fff'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: '12px',
                  background: `linear-gradient(135deg, ${item.gradient[0]} 0%, ${item.gradient[1]} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 18,
                }}>
                  {item.icon}
                </div>
                <span style={{ fontSize: 15, fontWeight: 500, color: '#1f2937' }}>
                  {item.title}
                </span>
              </div>
              <RightOutlined style={{ color: '#9ca3af', fontSize: 12 }} />
            </div>
          ))}
        </Card>

        {/* Privacy Link */}
        <div
          onClick={() => navigate('/privacy')}
          style={{
            marginTop: 16,
            padding: '14px 20px',
            textAlign: 'center',
            color: '#6b7280',
            fontSize: 13,
            cursor: 'pointer',
            borderRadius: 16,
            background: '#fff',
            boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
          }}
        >
          数据隐私说明
        </div>

        {/* Logout */}
        <Button
          type="text"
          danger
          icon={<LogoutOutlined />}
          onClick={handleLogout}
          block
          style={{
            marginTop: 16,
            height: 52,
            borderRadius: 16,
            fontSize: 16,
            fontWeight: 500,
            background: '#fff',
            boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
          }}
        >
          退出登录
        </Button>

        {/* Back */}
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Link to="/">
            <Button type="link" style={{ color: themeGradient, fontWeight: 500 }}>
              返回首页
            </Button>
          </Link>
        </div>
      </div>

      {/* Payment Modal */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CrownOutlined style={{ color: themeGradient }} />
            <span>会员套餐</span>
          </div>
        }
        open={paymentModalVisible}
        onCancel={() => setPaymentModalVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
        styles={{ body: { padding: 24 } }}
      >
        <PaymentPage />
      </Modal>
    </div>
  )
}
