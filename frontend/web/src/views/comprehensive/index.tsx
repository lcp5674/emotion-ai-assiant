import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Progress, Spin, App, Steps, Tag, Row, Col } from 'antd'
import { UserOutlined, HeartOutlined, CrownOutlined, CheckCircleOutlined, RocketOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useAuthStore } from '../../stores'
import { useTheme } from '../../hooks/useTheme'

type TestType = 'mbti' | 'sbti' | 'attachment'

interface TestStatus {
  completed: boolean
  result?: any
}

export default function ComprehensiveTest() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { isAuthenticated } = useAuthStore()
  const { themeColors, themeColor } = useTheme()

  const [loading, setLoading] = useState(true)
  const [testStatuses, setTestStatuses] = useState<Record<TestType, TestStatus>>({
    mbti: { completed: false },
    sbti: { completed: false },
    attachment: { completed: false },
  })

  const currentStep = testStatuses.mbti.completed ? 
    (testStatuses.sbti.completed ? 
      (testStatuses.attachment.completed ? 3 : 2) : 1) : 0

  useEffect(() => {
    loadTestStatuses()
  }, [])

  const loadTestStatuses = async () => {
    setLoading(true)
    try {
      const [mbti, sbti, attachment] = await Promise.allSettled([
        api.mbti.result().catch(() => null),
        api.sbti.result().catch(() => null),
        api.attachment.result().catch(() => null),
      ])

      setTestStatuses({
        mbti: { completed: mbti.status === 'fulfilled' && !!mbti.value, result: mbti.value },
        sbti: { completed: sbti.status === 'fulfilled' && !!sbti.value, result: sbti.value },
        attachment: { completed: attachment.status === 'fulfilled' && !!attachment.value, result: attachment.value },
      })
    } catch (error) {
      console.error('加载测评状态失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const completedCount = Object.values(testStatuses).filter(t => t.completed).length
  const allCompleted = completedCount === 3

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
        background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 50%, #fa8c16 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <h1 style={{ fontSize: 32, marginBottom: 8, color: '#fff' }}>三位一体深度测评</h1>
          <p style={{ fontSize: 16, opacity: 0.9 }}>
            从MBTI人格、SBTI恋爱风格、依恋类型三个维度全面认识自己
          </p>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px', maxWidth: 800, margin: '0 auto' }}>
        {/* Progress */}
        <Card style={{ marginBottom: 24, borderRadius: 12 }}>
          <Steps
            current={currentStep}
            items={[
              { title: 'MBTI人格', icon: <UserOutlined /> },
              { title: 'SBTI恋爱', icon: <CrownOutlined /> },
              { title: '依恋风格', icon: <HeartOutlined /> },
            ]}
          />
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Progress 
              percent={Math.round((completedCount / 3) * 100)} 
              strokeColor="#722ed1"
              style={{ maxWidth: 400, margin: '0 auto' }}
            />
            <p style={{ color: '#8c8c8c', marginTop: 8 }}>
              已完成 {completedCount}/3 项测评
            </p>
          </div>
        </Card>

        {/* Test Cards */}
        <Row gutter={[16, 16]}>
          {/* MBTI Card */}
          <Col xs={24} md={8}>
            <Card
              style={{
                height: '100%',
                borderRadius: 12,
                borderTop: `4px solid ${testStatuses.mbti.completed ? '#52c41a' : '#6366f1'}`,
              }}
            >
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: testStatuses.mbti.completed ? '#52c41a' : 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  color: '#fff',
                  fontSize: 24,
                }}>
                  {testStatuses.mbti.completed ? <CheckCircleOutlined /> : <UserOutlined />}
                </div>
                <h3 style={{ marginBottom: 8 }}>MBTI人格测评</h3>
                <p style={{ color: '#8c8c8c', fontSize: 13, marginBottom: 16 }}>
                  16种人格类型，发现你的性格优势
                </p>
                {testStatuses.mbti.completed ? (
                  <div>
                    <Tag color="purple" style={{ marginBottom: 12 }}>{testStatuses.mbti.result?.mbti_type}</Tag>
                    <Button block onClick={() => navigate('/mbti/result')}>
                      查看结果
                    </Button>
                  </div>
                ) : (
                  <Button 
                    type="primary"
                    block
                    style={{ background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', border: 'none' }}
                    onClick={() => navigate('/mbti')}
                  >
                    开始测试
                  </Button>
                )}
              </div>
            </Card>
          </Col>

          {/* SBTI Card */}
          <Col xs={24} md={8}>
            <Card
              style={{
                height: '100%',
                borderRadius: 12,
                borderTop: `4px solid ${testStatuses.sbti.completed ? '#52c41a' : '#f472b6'}`,
              }}
            >
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: testStatuses.sbti.completed ? '#52c41a' : 'linear-gradient(135deg, #f472b6 0%, #ec4899 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  color: '#fff',
                  fontSize: 24,
                }}>
                  {testStatuses.sbti.completed ? <CheckCircleOutlined /> : <CrownOutlined />}
                </div>
                <h3 style={{ marginBottom: 8 }}>SBTI恋爱风格</h3>
                <p style={{ color: '#8c8c8c', fontSize: 13, marginBottom: 16 }}>
                  34种恋爱类型，解读你的恋爱模式
                </p>
                {testStatuses.sbti.completed ? (
                  <div>
                    <Tag color="magenta" style={{ marginBottom: 12 }}>
                      {testStatuses.sbti.result?.top5_themes?.[0] || '已完成'}
                    </Tag>
                    <Button block onClick={() => navigate('/sbti/result')}>
                      查看结果
                    </Button>
                  </div>
                ) : (
                  <Button 
                    type="primary"
                    block
                    style={{ background: 'linear-gradient(135deg, #f472b6 0%, #ec4899 100%)', border: 'none' }}
                    onClick={() => navigate('/sbti')}
                  >
                    开始测试
                  </Button>
                )}
              </div>
            </Card>
          </Col>

          {/* Attachment Card */}
          <Col xs={24} md={8}>
            <Card
              style={{
                height: '100%',
                borderRadius: 12,
                borderTop: `4px solid ${testStatuses.attachment.completed ? '#52c41a' : '#34d399'}`,
              }}
            >
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: testStatuses.attachment.completed ? '#52c41a' : 'linear-gradient(135deg, #34d399 0%, #14b8a6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  color: '#fff',
                  fontSize: 24,
                }}>
                  {testStatuses.attachment.completed ? <CheckCircleOutlined /> : <HeartOutlined />}
                </div>
                <h3 style={{ marginBottom: 8 }}>依恋风格测评</h3>
                <p style={{ color: '#8c8c8c', fontSize: 13, marginBottom: 16 }}>
                  4种依恋类型，认识你的依恋模式
                </p>
                {testStatuses.attachment.completed ? (
                  <div>
                    <Tag color="green" style={{ marginBottom: 12 }}>
                      {testStatuses.attachment.result?.style || '已完成'}
                    </Tag>
                    <Button block onClick={() => navigate('/attachment/result')}>
                      查看结果
                    </Button>
                  </div>
                ) : (
                  <Button 
                    type="primary"
                    block
                    style={{ background: 'linear-gradient(135deg, #34d399 0%, #14b8a6 100%)', border: 'none' }}
                    onClick={() => navigate('/attachment')}
                  >
                    开始测试
                  </Button>
                )}
              </div>
            </Card>
          </Col>
        </Row>

        {/* All Completed */}
        {allCompleted && (
          <Card
            style={{ 
              marginTop: 24, 
              borderRadius: 12,
              background: 'linear-gradient(135deg, #f0f5ff 0%, #f5f5f5 100%)',
              border: '2px solid #722ed1',
            }}
          >
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <RocketOutlined style={{ fontSize: 48, color: '#722ed1', marginBottom: 16 }} />
              <h2 style={{ marginBottom: 16, color: '#722ed1' }}>恭喜完成全部测评！</h2>
              <p style={{ color: '#595959', marginBottom: 24 }}>
                现在你可以查看完整的深度人格画像，获得最匹配的AI情感伴侣推荐
              </p>
              <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
                <Button 
                  type="primary"
                  size="large"
                  style={{ 
                    background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)',
                    border: 'none',
                    borderRadius: 24,
                    padding: '8px 32px'
                  }}
                  onClick={() => navigate('/profile/deep')}
                >
                  查看完整画像
                </Button>
                <Button 
                  size="large"
                  style={{ borderRadius: 24, padding: '8px 32px' }}
                  onClick={() => navigate('/assistants')}
                >
                  探索AI助手
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Navigation */}
        <div style={{ marginTop: 32, display: 'flex', justifyContent: 'center', gap: 16 }}>
          <Link to="/">
            <Button>返回首页</Button>
          </Link>
          <Link to="/profile/deep">
            <Button type="primary" style={{ background: '#722ed1' }}>
              查看深度画像
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
