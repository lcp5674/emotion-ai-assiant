import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Progress, Spin, App } from 'antd'
import { api } from '../../api/request'
import { useMbtiStore, useAuthStore } from '../../stores'

export default function MbtiResult() {
  const navigate = useNavigate()
  const { result, setResult } = useMbtiStore()
  const { message } = App.useApp()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(!result)
  const [assistants, setAssistants] = useState<any[]>([])

  useEffect(() => {
    if (!result) {
      loadResult()
    }
    loadAssistants()
  }, [])

  const loadResult = async () => {
    setLoading(true)
    try {
      const res = await api.mbti.result()
      setResult(res)
    } catch (error: any) {
      if (error.response?.status === 404) {
        message.info('请先完成MBTI测试')
        navigate('/mbti')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadAssistants = async () => {
    try {
      const res = await api.mbti.assistants({ mbti_type: result?.mbti_type })
      setAssistants(res.list?.slice(0, 3) || [])
    } catch (error) {
      console.error(error)
    }
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
        <h2>请先完成MBTI测试</h2>
        <Link to="/mbti">
          <Button type="primary" style={{ marginTop: 16, background: '#722ed1' }}>
            开始测试
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <h1 style={{ fontSize: 36, marginBottom: 8 }}>你的MBTI类型</h1>
          <div style={{
            fontSize: 72,
            fontWeight: 'bold',
            color: '#ffffff',
            textShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}>
            {result.mbti_type}
          </div>
          <p style={{ fontSize: 18, marginTop: 8, opacity: 0.9 }}>
            {result.personality}
          </p>
        </div>
      </header>

      <div className="container" style={{ marginTop: -30 }}>
        {/* Dimensions */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 24 }}>各维度分析</h3>
          <Row gutter={[24, 24]}>
            {result.dimensions.map((dim: any, index: number) => (
              <Col xs={24} sm={12} key={index}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span>{dim.dimension === 'EI' ? '外向-内向' : dim.dimension === 'SN' ? '感觉-直觉' : dim.dimension === 'TF' ? '思维-情感' : '判断-知觉'}</span>
                    <Tag color="purple">{dim.tendency}</Tag>
                  </div>
                  <Progress
                    percent={Math.min(Math.abs(dim.score) * 5 + 50, 100)}
                    strokeColor="#722ed1"
                    format={percent => `${percent}%`}
                  />
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Strengths & Weaknesses */}
        <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
          <Col xs={24} md={12}>
            <Card title="性格优势">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {result.strengths.map((s: string, i: number) => (
                  <Tag color="green" key={i}>{s}</Tag>
                ))}
              </div>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="性格盲点">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {result.weaknesses.map((w: string, i: number) => (
                  <Tag color="orange" key={i}>{w}</Tag>
                ))}
              </div>
            </Card>
          </Col>
        </Row>

        {/* Advice */}
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>人际关系建议</h3>
          <p style={{ lineHeight: 2, color: '#595959' }}>{result.relationship_tips}</p>
        </Card>

        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>职业发展建议</h3>
          <p style={{ lineHeight: 2, color: '#595959' }}>{result.career_advice}</p>
          <div style={{ marginTop: 16 }}>
            <strong>适合的职业：</strong>
            {result.suitable_jobs.map((j: string, i: number) => (
              <Tag color="blue" key={i} style={{ marginLeft: 8 }}>{j}</Tag>
            ))}
          </div>
        </Card>

        {/* Recommended Assistants */}
        {assistants.length > 0 && (
          <Card title="为你推荐的AI助手">
            <Row gutter={[16, 16]}>
              {assistants.map((assistant: any) => (
                <Col xs={24} sm={8} key={assistant.id}>
                  <Card
                    hoverable
                    onClick={() => navigate(`/chat?assistant_id=${assistant.id}`)}
                    style={{ textAlign: 'center' }}
                  >
                    <div style={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
                      margin: '0 auto 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                      fontSize: 32,
                    }}>
                      {assistant.name[0]}
                    </div>
                    <h4>{assistant.name}</h4>
                    <Tag color="purple">{assistant.mbti_type}</Tag>
                    <p style={{ marginTop: 8, color: '#8c8c8c', fontSize: 14 }}>
                      {assistant.speaking_style?.slice(0, 50)}...
                    </p>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* Actions */}
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Link to="/chat">
            <Button type="primary" size="large" style={{ marginRight: 16, background: '#722ed1' }}>
              开始聊天
            </Button>
          </Link>
          <Link to="/mbti">
            <Button size="large">重新测试</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}