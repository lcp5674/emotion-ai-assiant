import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Button, Avatar, Tag, Spin, List, App } from 'antd'
import { UserOutlined, SettingOutlined, LogoutOutlined, MessageOutlined, HeartOutlined, CalendarOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'

export default function Profile() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { user, logout } = useAuthStore()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
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

  const handleLogout = () => {
    logout()
    navigate('/')
    message.success('已退出登录')
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
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
          {user?.mbti_type && (
            <Tag color="purple" style={{ marginTop: 8 }}>{user.mbti_type}</Tag>
          )}
        </div>
      </header>

      <div className="container" style={{ marginTop: -30, paddingBottom: 40 }}>
        {/* Stats */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats?.conversation_count || 0}
              </div>
              <div style={{ color: '#8c8c8c' }}>对话数</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {stats?.mbti_test_count || 0}
              </div>
              <div style={{ color: '#8c8c8c' }}>测试次数</div>
            </Card>
          </Col>
          <Col xs={8}>
            <Card style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                {user?.member_level === 'free' ? '免费' : user?.member_level}
              </div>
              <div style={{ color: '#8c8c8c' }}>会员等级</div>
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
                onClick={() => navigate(item.path)}
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

        {/* Back */}
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Link to="/">
            <Button>返回首页</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}