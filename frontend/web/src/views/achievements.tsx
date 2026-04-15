import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Progress, Spin, Empty, Badge, Button, List } from 'antd'
import { TrophyOutlined, CrownOutlined, StarOutlined, FireOutlined, ArrowLeftOutlined, LockOutlined } from '@ant-design/icons'
import { api, apiClient } from '../api/request'
import { useAuthStore } from '../stores'

interface Badge {
  id: number
  badge_code: string
  name: string
  description: string
  icon: string
  rarity: string
  category: string
  is_earned: boolean
  earned_at?: string
}

interface UserLevel {
  level: number
  title: string
  current_exp: number
  max_exp: number
}

export default function AchievementsPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [badges, setBadges] = useState<Badge[]>([])
  const [userLevel, setUserLevel] = useState<UserLevel | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAchievements()
  }, [])

  const fetchAchievements = async () => {
    try {
      const [badgesRes, levelRes] = await Promise.all([
        apiClient.get('/growth/badges/user'),
        apiClient.get('/growth/level'),
      ])
      setBadges(badgesRes || [])
      setUserLevel(levelRes)
    } catch (error) {
      console.error('获取成就失败', error)
    } finally {
      setLoading(false)
    }
  }

  const getRarityColor = (rarity: string) => {
    const colors: Record<string, string> = {
      common: '#8c8c8c',
      uncommon: '#52c41a',
      rare: '#1890ff',
      epic: '#722ed1',
      legendary: '#fa8c16',
    }
    return colors[rarity] || '#8c8c8c'
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case '测评': return <CrownOutlined />
      case '日记': return <FireOutlined />
      case '互动': return <StarOutlined />
      default: return <TrophyOutlined />
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      <header style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <Link to="/">
            <Button icon={<ArrowLeftOutlined />} type="text" style={{ color: '#fff', position: 'absolute', left: 16, top: 20 }}>
              返回
            </Button>
          </Link>
          <TrophyOutlined style={{ fontSize: 48, marginBottom: 16 }} />
          <h1 style={{ fontSize: 28, marginBottom: 8 }}>我的成就</h1>
          <p>持续探索，获得成就徽章</p>
        </div>
      </header>

      <div className="container" style={{ marginTop: -20 }}>
        {userLevel && (
          <Card style={{ marginBottom: 24 }}>
            <Row gutter={[24, 24]} align="middle">
              <Col xs={24} md={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{
                    fontSize: 48,
                    fontWeight: 'bold',
                    color: '#722ed1',
                  }}>
                    {userLevel.level}
                  </div>
                  <div style={{ color: '#8c8c8c' }}>Lv.{userLevel.level}</div>
                </div>
              </Col>
              <Col xs={24} md={16}>
                <div>
                  <div style={{ marginBottom: 8 }}>
                    <strong>{userLevel.title}</strong>
                  </div>
                  <Progress
                    percent={Math.round((userLevel.current_exp / userLevel.max_exp) * 100)}
                    strokeColor="#722ed1"
                    trailColor="#f0f0f0"
                    format={() => `${userLevel.current_exp}/${userLevel.max_exp} 经验`}
                  />
                </div>
              </Col>
            </Row>
          </Card>
        )}

        <Card title="我的徽章">
          {badges.length === 0 ? (
            <Empty description="还没有获得任何徽章，快去完成测评和写日记吧！" />
          ) : (
            <Row gutter={[16, 16]}>
              {badges.map((badge) => (
                <Col xs={12} sm={8} md={6} key={badge.id}>
                  <Card
                    hoverable
                    style={{
                      textAlign: 'center',
                      opacity: badge.is_earned ? 1 : 0.5,
                    }}
                  >
                    <Badge>
                      <div style={{
                        fontSize: 36,
                        color: badge.is_earned ? getRarityColor(badge.rarity) : '#d9d9d9',
                      }}>
                        {badge.is_earned ? (badge.icon || '🏆') : '🔒'}
                      </div>
                    </Badge>
                    <div style={{ marginTop: 8, fontWeight: 'bold' }}>
                      {badge.is_earned ? badge.name : '???️'}
                    </div>
                    <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                      {badge.is_earned ? badge.description : '未解锁'}
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
        </Card>
      </div>
    </div>
  )
}