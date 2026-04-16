import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Progress, Spin, App, Modal, Space } from 'antd'
import { ArrowLeftOutlined, CrownOutlined, HeartOutlined, RocketOutlined, CheckCircleOutlined, ShareAltOutlined, CopyOutlined, CheckOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useMbtiStore, useAuthStore } from '../../stores'

// MBTI类型描述映射
const getMbtiDescription = (mbtiType: string | undefined): string => {
  const descriptions: Record<string, string> = {
    'ISTJ': '沉默务实，注重责任和传统，擅长逻辑分析。',
    'ISFJ': '温柔体贴，忠诚可靠，总是默默照顾他人。',
    'INFJ': '理想主义，有洞察力，追求意义和价值。',
    'INTJ': '独立思考，战略眼光，追求知识和能力。',
    'ISTP': '冷静观察，灵活应变，擅长实际操作。',
    'ISFP': '温柔敏感，追求美感，享受当下。',
    'INFP': '理想主义，内心丰富，寻求真实和意义。',
    'INTP': '理性思考，爱因斯坦型人格，善于分析。',
    'ESTP': '大胆行动，灵活变通，勇于尝试。',
    'ESFP': '热情活力，热爱社交，享受生活。',
    'ENFP': '热情洋溢，创意无限，善于激励他人。',
    'ENTP': '聪明机智，喜欢辩论，敢于挑战。',
    'ESTJ': '务实高效，果断决策，注重结果。',
    'ESFJ': '热情助人，善于社交，照顾他人感受。',
    'ENFJ': '天生的领导者，善于激励和启发他人。',
    'ENTJ': '果断决策，目标导向，擅长战略规划。',
  }
  return descriptions[mbtiType || ''] || '探索中...'
}

export default function MbtiResult() {
  const navigate = useNavigate()
  const { result, setResult } = useMbtiStore()
  const { message } = App.useApp()
  const [shareModalVisible, setShareModalVisible] = useState(false)
  const [copied, setCopied] = useState(false)

  const shareText = `🎯 我的MBTI类型是 ${result?.mbti_type}！
${getMbtiDescription(result?.mbti_type)}
了解更多自己，探索成长 👉 情感AI助手`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareText)
      setCopied(true)
      message.success('复制成功！')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      message.error('复制失败')
    }
  }
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, marginBottom: 16 }}>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(-1)}
              style={{ color: '#fff', position: 'absolute', left: 20 }}
              size="large"
            />
            <h1 style={{ fontSize: 36, margin: 0 }}>你的MBTI类型</h1>
          </div>
          <div style={{
            fontSize: 'clamp(36px, 10vw, 72px)',
            fontWeight: 'bold',
            color: '#ffffff',
            textShadow: '0 2px 4px rgba(0,0,0,0.1)',
            wordBreak: 'break-word',
          }}>
            {result.mbti_type}
          </div>
          <p style={{ fontSize: 18, marginTop: 8, opacity: 0.9, wordBreak: 'break-word' }}>
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
                    percent={
                      dim.percentage != null
                        ? dim.percentage
                        : Math.min(Math.max(Math.round(((dim.score + 12) / 24) * 90 + 5), 5), 95)
                    }
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
          <Space>
            <Link to="/chat">
              <Button type="primary" size="large" style={{ background: '#722ed1' }}>
                开始聊天
              </Button>
            </Link>
            <Button size="large" icon={<ShareAltOutlined />} onClick={() => setShareModalVisible(true)}>
              分享结果
            </Button>
            <Link to="/mbti">
              <Button size="large">重新测试</Button>
            </Link>
          </Space>
        </div>

        <Modal
          title="分享你的MBTI结果"
          open={shareModalVisible}
          onCancel={() => setShareModalVisible(false)}
          footer={null}
          centered
        >
          <div style={{ textAlign: 'center', padding: 24 }}>
            <div style={{
              fontSize: 48,
              fontWeight: 'bold',
              color: '#722ed1',
              marginBottom: 16,
            }}>
              {result?.mbti_type}
            </div>
            <p style={{ marginBottom: 24, color: '#595959' }}>
              {getMbtiDescription(result?.mbti_type)}
            </p>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={copied ? <CheckOutlined /> : <CopyOutlined />}
                onClick={handleCopy}
                block
                style={{ background: '#722ed1' }}
              >
                {copied ? '已复制' : '复制文案'}
              </Button>
            </Space>
          </div>
        </Modal>
      </div>
    </div>
  )
}