import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Row, Col, Spin, App, Modal } from 'antd'
import { CrownOutlined, TeamOutlined, HeartOutlined, RocketOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useAuthStore } from '../../stores'

export default function SbtiIndex() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { user } = useAuthStore()
  const [hasResult, setHasResult] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkResult()
  }, [])

  const checkResult = async () => {
    try {
      const res = await api.sbti.result()
      setHasResult(true)
    } catch (error: any) {
      if (error.response?.status === 404) {
        setHasResult(false)
      }
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: <TeamOutlined style={{ fontSize: 32, color: '#722ed1' }} />,
      title: '发现你的才干主题',
      description: '基于盖洛普34个才干主题，深度分析你的独特优势',
    },
    {
      icon: <HeartOutlined style={{ fontSize: 32, color: '#eb2f96' }} />,
      title: '关系优势分析',
      description: '了解你在亲密关系中的人际互动模式',
    },
    {
      icon: <RocketOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      title: '职业发展指导',
      description: '根据才干特点提供个性化的职业建议',
    },
    {
      icon: <CrownOutlined style={{ fontSize: 32, color: '#fa8c16' }} />,
      title: 'AI伴侣匹配',
      description: '智能推荐与你才干互补的AI情感伴侣',
    },
  ]

  const process = [
    { step: 1, text: '开始24道二选一测评' },
    { step: 2, text: '获得你的Top5才干主题' },
    { step: 3, text: '查看详细解读和建议' },
  ]

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
        padding: '60px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.2)',
            margin: '0 auto 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <CrownOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 36, marginBottom: 16, color: '#fff' }}>SBTI 才干测评</h1>
          <p style={{ fontSize: 18, opacity: 0.9, maxWidth: 600, margin: '0 auto' }}>
            基于盖洛普优势识别器，发现你的34个才干主题中最重要的5个，
            深度了解你在工作、关系和生活中的独特优势
          </p>
          {user?.mbti_type && (
            <div style={{ marginTop: 16 }}>
              <span style={{
                background: 'rgba(255,255,255,0.2)',
                padding: '4px 16px',
                borderRadius: 20,
                fontSize: 14,
              }}>
                MBTI: {user.mbti_type}
              </span>
            </div>
          )}
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        {/* Features */}
        <Row gutter={[24, 24]} style={{ marginBottom: 40 }}>
          {features.map((feature, index) => (
            <Col xs={24} sm={12} md={6} key={index}>
              <Card
                style={{
                  textAlign: 'center',
                  height: '100%',
                  border: 'none',
                  boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                }}
              >
                <div style={{ marginBottom: 16 }}>{feature.icon}</div>
                <h3 style={{ fontSize: 16, marginBottom: 8 }}>{feature.title}</h3>
                <p style={{ color: '#8c8c8c', fontSize: 14 }}>{feature.description}</p>
              </Card>
            </Col>
          ))}
        </Row>

        {/* Process */}
        <Card
          style={{
            marginBottom: 40,
            background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
            border: 'none',
          }}
        >
          <h3 style={{ textAlign: 'center', marginBottom: 24 }}>测评流程</h3>
          <Row gutter={[16, 16]} justify="center">
            {process.map((item, index) => (
              <Col xs={24} sm={8} key={index}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: '#52c41a',
                    color: '#fff',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 18,
                    fontWeight: 'bold',
                    marginBottom: 8,
                  }}>
                    {item.step}
                  </div>
                  <p style={{ margin: 0 }}>{item.text}</p>
                  {index < process.length - 1 && (
                    <div style={{
                      display: 'none',
                      '@media (min-width: 576px)': { display: 'block' },
                      position: 'absolute',
                      top: 20,
                      left: '50%',
                      width: 'calc(100% - 80px)',
                      height: 2,
                      background: '#52c41a',
                    }} />
                  )}
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* CTA */}
        <Card style={{ textAlign: 'center', padding: '20px 0' }}>
          <h2 style={{ marginBottom: 24 }}>准备好发现你的才干了？</h2>
          <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
            测评包含24道二选一题目，大约需要5分钟完成
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              type="primary"
              size="large"
              style={{ background: '#722ed1', minWidth: 200 }}
              onClick={() => navigate('/sbti/test')}
            >
              {hasResult ? '重新测评' : '开始测评'}
            </Button>
            {hasResult && (
              <Button
                size="large"
                style={{ minWidth: 200 }}
                onClick={() => navigate('/sbti/result')}
              >
                查看上次结果
              </Button>
            )}
          </div>
          <div style={{ marginTop: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, color: '#8c8c8c' }}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <span>完成测评即可解锁深度画像功能</span>
          </div>
        </Card>

        {/* Back Link */}
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Link to="/">
            <Button type="text">返回首页</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
