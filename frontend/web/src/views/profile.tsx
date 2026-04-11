import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Button, Avatar, Tag, Spin, List, App, Modal } from 'antd'
import { UserOutlined, SettingOutlined, LogoutOutlined, MessageOutlined, HeartOutlined, CalendarOutlined, CrownOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import PaymentPage from './payment'

export default function Profile() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { user, logout } = useAuthStore()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [paymentModalVisible, setPaymentModalVisible] = useState(false)
  const [currentMembership, setCurrentMembership] = useState<any>(null)
  const [plansLoading, setPlansLoading] = useState(false)

  useEffect(() => {
    loadStats()
    if (user?.member_level !== 'free') {
      loadCurrentMembership()
    }
  }, [])

  const loadStats = async () => {
    try {
      const res = await api.user.stats()
      setStats(res)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentMembership = async () => {
    try {
      const res = await api.payment.getCurrentMembership()
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
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  const getMemberLevelText = () => {
    if (!user || user.member_level === 'free') return '免费'
    return user.member_level
  }

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
          <Avatar
            size={80}
            icon={<UserOutlined />}
            style={{ background: 'rgba(255,255,255,0.2)', marginBottom: 16 }}
          />
          <h2 style={{ fontSize: 24, marginBottom: 8 }}>{user?.nickname || '用户'}</h2>
          <p style={{ opacity: 0.9 }}>{user?.phone}</p>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            {user?.mbti_type && (
              <Tag color="purple" style={{ marginTop: 8 }}>{user.mbti_type}</Tag>
            )}
            {user?.member_level && user.member_level !== 'free' && (
              <Tag color="gold" icon={<CrownOutlined />} style={{ marginTop: 8 }}>
                {user.member_level}会员
              </Tag>
            )}
          </div>
        </div>
      </header>

      <div className="container" style={{ marginTop: -30, paddingBottom: 40 }}>
        {/* 会员提示卡片 */}
        {(!currentMembership || currentMembership.level === 'free') && (
          <Card
            style={{
              marginBottom: 24,
              background: 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)',
              border: 'none',
            }}
          >
            <Row align="middle" gutter={16}>
              <Col flex="auto">
                <h3 style={{ margin: 0, color: '#fa8c16', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CrownOutlined /> 升级会员解锁更多功能
                </h3>
                <p style={{ margin: '8px 0 0 0', color: '#fa8c16', opacity: 0.8 }}>
                  无限对话次数 · 高级AI模型 · 情绪深度分析 · 云备份
                </p>
              </Col>
              <Col>
                <Button
                  type="primary"
                  style={{ background: '#fa8c16', borderColor: '#fa8c16' }}
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
              marginBottom: 24,
              background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
              border: 'none',
            }}
          >
            <Row align="middle" gutter={16}>
              <Col flex="auto">
                <h3 style={{ margin: 0, color: '#52c41a', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CrownOutlined /> {currentMembership.plan_name}会员
                </h3>
                <p style={{ margin: '8px 0 0 0', color: '#52c41a', opacity: 0.8 }}>
                  有效期至 {currentMembership.expires_at}
                </p>
              </Col>
              <Col>
                <Button
                  type="primary"
                  style={{ background: '#52c41a', borderColor: '#52c41a' }}
                  onClick={openMembershipModal}
                >
                  续费会员
                </Button>
              </Col>
            </Row>
          </Card>
        )}

        {/* Stats */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats?.conversation_count || 0}
              </div>
              <div style={{ color: '#8c8c8c' }}>对话数</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats?.mbti_test_count || 0}
              </div>
              <div style={{ color: '#8c8c8c' }}>测试次数</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card style={{ textAlign: 'center' }} onClick={openMembershipModal} className="cursor-pointer">
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {getMemberLevelText()}
              </div>
              <div style={{ color: '#8c8c8c' }}>
                {user?.member_level === 'free' ? '点击升级会员' : '会员等级'}
              </div>
            </Card>
          </Col>
        </Row>

        {/* Menu */}
        <Card>
          <List
            dataSource={[
              {
                icon: <MessageOutlined />,
                title: '我的对话',
                path: '/chat',
              },
              {
                icon: <CalendarOutlined />,
                title: '情感日记',
                path: '/diary',
              },
              {
                icon: <HeartOutlined />,
                title: '我的收藏',
                path: '/knowledge/collections',
              },
              {
                icon: <UserOutlined />,
                title: 'MBTI结果',
                path: '/mbti/result',
              },
              {
                icon: <CrownOutlined />,
                title: '会员中心',
                action: openMembershipModal,
              },
              {
                icon: <SettingOutlined />,
                title: '账户设置',
                path: '/settings',
              },
            ].concat(user?.id === 10 ? [{
                icon: <SettingOutlined />,
                title: '系统管理',
                path: '/admin',
              }] : []).filter(Boolean)}
            renderItem={(item) => (
              <List.Item
                actions={[<Button type="text" icon={item.icon} />]}
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  if (item.action) {
                    item.action()
                  } else if (item.path) {
                    navigate(item.path)
                  }
                }}
              >
                {item.title}
              </List.Item>
            )}
          />
        </Card>

        {/* Logout */}
        <div style={{ marginTop: 24 }}>
          <Button
            type="text"
            danger
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            block
          >
            退出登录
          </Button>
        </div>

        {/* Data Privacy Link */}
        <div style={{ marginTop: 16 }}>
          <List>
            <List.Item
              style={{ cursor: 'pointer' }}
              onClick={() => navigate('/privacy')}
            >
              数据隐私说明
            </List.Item>
          </List>
        </div>

        {/* Back */}
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Link to="/">
            <Button>返回首页</Button>
          </Link>
        </div>
      </div>

      {/* 会员购买弹窗 */}
      <Modal
        title="会员套餐"
        open={paymentModalVisible}
        onCancel={() => setPaymentModalVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <PaymentPage />
      </Modal>
    </div>
  )
}
