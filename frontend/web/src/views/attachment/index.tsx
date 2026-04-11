import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Row, Col, Spin, App } from 'antd'
import { HeartOutlined, UserOutlined, SolutionOutlined, TeamOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { api } from '../../api/request'

export default function AttachmentIndex() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [hasResult, setHasResult] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkResult()
  }, [])

  const checkResult = async () => {
    try {
      const res = await api.attachment.result()
      setHasResult(true)
    } catch (error: any) {
      if (error.response?.status === 404) {
        setHasResult(false)
      }
    } finally {
      setLoading(false)
    }
  }

  const styles = [
    {
      type: '安全型',
      color: '#52c41a',
      icon: <HeartOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      description: '能够在亲密关系中保持健康的依赖与独立平衡',
    },
    {
      type: '焦虑型',
      color: '#fa8c16',
      icon: <UserOutlined style={{ fontSize: 32, color: '#fa8c16' }} />,
      description: '渴望亲密，容易担心被抛弃，情绪波动较大',
    },
    {
      type: '回避型',
      color: '#1890ff',
      icon: <SolutionOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      description: '重视独立，倾向于保持情感距离',
    },
    {
      type: '混乱型',
      color: '#eb2f96',
      icon: <TeamOutlined style={{ fontSize: 32, color: '#eb2f96' }} />,
      description: '在依赖与回避之间摇摆不定',
    },
  ]

  const benefits = [
    '深入了解自己的依恋模式',
    '认识亲密关系中的优势与挑战',
    '获得针对性的关系改善建议',
    '找到与你有良好匹配的伴侣类型',
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
        background: 'linear-gradient(135deg, #eb2f96 0%, #b37feb 100%)',
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
            <HeartOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 36, marginBottom: 16, color: '#fff' }}>依恋风格测评</h1>
          <p style={{ fontSize: 18, opacity: 0.9, maxWidth: 600, margin: '0 auto' }}>
            探索你在亲密关系中的依恋模式，了解你与他人的情感连接方式，
            发现建立健康关系的关键
          </p>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        {/* Attachment Styles */}
        <h2 style={{ textAlign: 'center', marginBottom: 32 }}>四种依恋风格</h2>
        <Row gutter={[24, 24]} style={{ marginBottom: 40 }}>
          {styles.map((style, index) => (
            <Col xs={24} sm={12} key={index}>
              <Card
                style={{
                  textAlign: 'center',
                  height: '100%',
                  borderTop: `4px solid ${style.color}`,
                }}
              >
                <div style={{ marginBottom: 16 }}>{style.icon}</div>
                <h3 style={{ marginBottom: 8, color: style.color }}>{style.type}</h3>
                <p style={{ color: '#8c8c8c', fontSize: 14 }}>{style.description}</p>
              </Card>
            </Col>
          ))}
        </Row>

        {/* Benefits */}
        <Card
          style={{
            marginBottom: 40,
            background: 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)',
            border: 'none',
          }}
        >
          <h3 style={{ textAlign: 'center', marginBottom: 24 }}>测评收获</h3>
          <Row gutter={[24, 16]}>
            {benefits.map((benefit, index) => (
              <Col xs={24} sm={12} key={index}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <CheckCircleOutlined style={{ fontSize: 20, color: '#fa8c16' }} />
                  <span>{benefit}</span>
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Test Info */}
        <Card style={{ marginBottom: 40, textAlign: 'center' }}>
          <h2 style={{ marginBottom: 16 }}>测评包含10道题目</h2>
          <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
            评估你在亲密关系中的焦虑程度和回避程度
          </p>

          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: 40,
            marginBottom: 24,
            flexWrap: 'wrap',
          }}>
            <div>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: '#eb2f96' }}>焦虑维度</div>
              <div style={{ color: '#8c8c8c' }}>担心被抛弃的程度</div>
            </div>
            <div>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: '#1890ff' }}>回避维度</div>
              <div style={{ color: '#8c8c8c' }}>回避亲密的程度</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              type="primary"
              size="large"
              style={{ background: '#eb2f96', minWidth: 200 }}
              onClick={() => navigate('/attachment/test')}
            >
              {hasResult ? '重新测评' : '开始测评'}
            </Button>
            {hasResult && (
              <Button
                size="large"
                style={{ minWidth: 200 }}
                onClick={() => navigate('/attachment/result')}
              >
                查看上次结果
              </Button>
            )}
          </div>
        </Card>

        {/* CTA */}
        <Card style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, color: '#52c41a' }}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <span>完成测评解锁完整深度画像</span>
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
