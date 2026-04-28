import { useEffect, useState, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Progress, Spin, Empty, Badge, Button, List, Modal } from 'antd'
import { TrophyOutlined, CrownOutlined, StarOutlined, FireOutlined, ArrowLeftOutlined, LockOutlined, CalendarOutlined } from '@ant-design/icons'
import { api, apiClient } from '../api/request'
import confetti from 'canvas-confetti'
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
  next_level?: number | null
  exp_to_next_level?: number
  progress_percent?: number
  current_level?: number
}


export const celebrateBadgeUnlock = (badge) => {
  const duration = 3000
  const end = Date.now() + duration
  const frame = () => {
    confetti({particleCount: 3, angle: 60, spread: 70, origin: {x: 0, y: 0.7}, colors: ["#ffd700", "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]})
    confetti({particleCount: 3, angle: 120, spread: 70, origin: {x: 1, y: 0.7}, colors: ["#ffd700", "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]})
    if (Date.now() < end) requestAnimationFrame(frame)
  }
  frame()
  Modal.success({
    title: <div style={{textAlign: "center"}}><span style={{fontSize: 48}}>{badge.icon}</span><div style={{marginTop: 8, fontSize: 24, color: "#fa8c16"}}>🎉 徽章解锁！🎉</div></div>,
    content: <div style={{textAlign: "center", padding: "16px 0"}}><h2 style={{color: "#722ed1", marginBottom: 8}}>{badge.name}</h2><p style={{color: "#666"}}>{badge.description}</p><div style={{marginTop: 16, padding: 12, background: "#f6ffed", borderRadius: 8, color: "#52c41a", fontWeight: 600}}>+50 经验值已到账！</div></div>,
    okText: "太棒了！",
    okButtonProps: {style: {background: "#722ed1", borderColor: "#722ed1", fontWeight: 600}},
    width: 360
  })
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

  const [emotionIntensity, setEmotionIntensity] = useState(0)

  const celebrationShown = useRef(false)

  const [prevBadges, setPrevBadges] = useState<Set<number>>(new Set())
  const [prevEmotion, setPrevEmotion] = useState("neutral")


  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const detectionIntervalRef = null

  const fetchAchievements = async () => {
    try {
      const [badgesRes, levelRes] = await Promise.all([
        apiClient.get('/growth/badges/user'),
        apiClient.get('/growth/level'),
      ])
      setBadges(badgesRes || [])
      setUserLevel(levelRes)

      if (!celebrationShown.current) {
        const currentBadgeIds = new Set<number>((badgesRes || []).filter(b => b.is_earned).map(b => b.id))
        const newBadges = (badgesRes || []).filter(b => b.is_earned && !prevBadges.has(b.id))
        if (newBadges.length > 0) {
          celebrationShown.current = true
          const newestBadge = newBadges[0]
          setTimeout(() => {
            celebrateBadgeUnlock({name: newestBadge.name, icon: newestBadge.icon, description: newestBadge.description})
          }, 500)
        }
        setPrevBadges(new Set<number>(currentBadgeIds))
      }
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
                    fontSize: 'clamp(32px, 6vw, 48px)',
                    fontWeight: 'bold',
                    color: '#722ed1',
                  }}>
                    {userLevel.current_level}
                  </div>
                  <div style={{ color: '#8c8c8c' }}>Lv.{userLevel.current_level}</div>
                </div>
              </Col>
              <Col xs={24} md={16}>
                <div>
                  <div style={{ marginBottom: 8 }}>
                    <strong>{userLevel.title || '新手'}</strong>
                  </div>
                  <Progress
                    percent={userLevel?.progress_percent ?? (userLevel?.max_exp ? Math.round(((userLevel.current_exp || 0) / userLevel.max_exp) * 100) : 0)}
                    strokeColor="#722ed1"
                    trailColor="#f0f0f0"
                    format={() => `${userLevel?.current_exp || 0}/${userLevel?.max_exp || 100} 经验`}
                  />
                </div>
              </Col>
            </Row>
          </Card>
        )}

        <Card title="我的徽章" extra={
          <Link to="/checkin">
            <Button icon={<CalendarOutlined />}>每日打卡</Button>
          </Link>
        }>
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