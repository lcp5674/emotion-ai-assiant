import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Progress, Spin, App, List } from 'antd'
import { HeartOutlined, CheckCircleOutlined, BulbOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useAttachmentStore } from '../../stores'

export default function AttachmentResult() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { result, setResult } = useAttachmentStore()
  const [loading, setLoading] = useState(!result)

  useEffect(() => {
    if (!result) {
      loadResult()
    }
  }, [])

  const loadResult = async () => {
    setLoading(true)
    try {
      const res = await api.attachment.result()
      setResult(res)
    } catch (error: any) {
      if (error.response?.status === 404) {
        message.info('请先完成依恋风格测试')
        navigate('/attachment')
      }
    } finally {
      setLoading(false)
    }
  }

  const getStyleColor = (style: string) => {
    const colors: Record<string, string> = {
      '安全型': '#52c41a',
      '焦虑型': '#fa8c16',
      '回避型': '#1890ff',
      '混乱型': '#eb2f96',
    }
    return colors[style] || '#722ed1'
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!result) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <h2>请先完成依恋风格测试</h2>
        <Link to="/attachment">
          <Button type="primary" style={{ marginTop: 16, background: '#eb2f96' }}>
            开始测试
          </Button>
        </Link>
      </div>
    )
  }

  const styleColor = getStyleColor(result.style)

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      {/* Header */}
      <header style={{
        background: `linear-gradient(135deg, ${styleColor} 0%, #b37feb 100%)`,
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.2)',
            margin: '0 auto 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <HeartOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 8, color: '#fff' }}>你的依恋风格</h1>
          <Tag
            color={result.style === '安全型' ? 'green' : result.style === '焦虑型' ? 'orange' : result.style === '回避型' ? 'blue' : 'magenta'}
            style={{ fontSize: 18, padding: '4px 16px', marginTop: 8 }}
          >
            {result.style}
          </Tag>
        </div>
      </header>

      <div className="container" style={{ marginTop: -20 }}>
        <div style={{ marginBottom: 16 }}>
          <Link to="/attachment">
            <Button icon={<ArrowLeftOutlined />}>返回测试</Button>
          </Link>
        </div>

        {/* Dimension Scores */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 24 }}>依恋维度分析</h3>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={12}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>焦虑程度</span>
                  <span style={{ color: '#eb2f96', fontWeight: 'bold' }}>{result.anxiety_score}%</span>
                </div>
                <Progress
                  percent={result.anxiety_score}
                  strokeColor="#eb2f96"
                  trailColor="#f0f0f0"
                  format={percent => ''}
                />
                <p style={{ color: '#8c8c8c', fontSize: 12, marginTop: 4 }}>
                  担心被抛弃或不被爱的程度
                </p>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>回避程度</span>
                  <span style={{ color: '#1890ff', fontWeight: 'bold' }}>{result.avoidance_score}%</span>
                </div>
                <Progress
                  percent={result.avoidance_score}
                  strokeColor="#1890ff"
                  trailColor="#f0f0f0"
                  format={percent => ''}
                />
                <p style={{ color: '#8c8c8c', fontSize: 12, marginTop: 4 }}>
                  回避亲密和依赖的程度
                </p>
              </div>
            </Col>
          </Row>
        </Card>

        {/* Characteristics */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>
            <BulbOutlined style={{ color: '#fa8c16', marginRight: 8 }} />
            依恋特征
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {result.characteristics?.map((char, index) => (
              <Tag key={index} color={styleColor}>{char}</Tag>
            ))}
          </div>
        </Card>

        {/* Relationship Tips */}
        {result.relationship_tips && (
          <Card
            style={{ marginBottom: 24 }}
            headStyle={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #adc6ff 100%)' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <HeartOutlined style={{ fontSize: 32, color: '#1890ff', marginTop: 4 }} />
              <div>
                <h3 style={{ margin: '0 0 12px' }}>关系提升建议</h3>
                <p style={{ lineHeight: 2, color: '#595959', margin: 0 }}>
                  {result.relationship_tips}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Self Growth Tips */}
        {result.self_growth_tips && (
          <Card
            style={{ marginBottom: 24 }}
            headStyle={{ background: 'linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%)' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <BulbOutlined style={{ fontSize: 32, color: '#52c41a', marginTop: 4 }} />
              <div>
                <h3 style={{ margin: '0 0 12px' }}>个人成长建议</h3>
                <p style={{ lineHeight: 2, color: '#595959', margin: 0 }}>
                  {result.self_growth_tips}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Actions */}
        <div style={{ textAlign: 'center', marginTop: 32, display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/chat">
            <Button type="primary" size="large" style={{ background: '#eb2f96' }}>
              开始聊天
            </Button>
          </Link>
          <Link to="/attachment/test">
            <Button size="large">重新测评</Button>
          </Link>
          <Link to="/profile/deep">
            <Button size="large" type="primary" style={{ background: '#722ed1' }}>
              查看深度画像
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
