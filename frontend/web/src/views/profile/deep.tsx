import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Spin, App, Tabs, List, Avatar, Empty, Progress, Badge, Statistic } from 'antd'
import { UserOutlined, CrownOutlined, HeartOutlined, RobotOutlined, CheckCircleOutlined, ArrowLeftOutlined, SolutionOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useDeepProfileStore, useAuthStore } from '../../stores'

// 雷达图组件 - 响应式版本
const RadarChart = ({ data, width = 350, height = 350 }: { data: { label: string; value: number }[]; width?: number; height?: number }) => {
  const maxValue = 100
  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(centerX, centerY) - 50

  const angleStep = (2 * Math.PI) / data.length
  const startAngle = -Math.PI / 2

  const points = data.map((d, i) => {
    const angle = startAngle + i * angleStep
    const distance = (d.value / maxValue) * radius
    return {
      x: centerX + distance * Math.cos(angle),
      y: centerY + distance * Math.sin(angle),
    }
  })

  const labels = data.map((d, i) => {
    const angle = startAngle + i * angleStep
    const labelRadius = radius + 35
    return {
      x: centerX + labelRadius * Math.cos(angle),
      y: centerY + labelRadius * Math.sin(angle),
      label: d.label,
    }
  })

  const grids = [0.25, 0.5, 0.75, 1].map(scale => {
    const r = radius * scale
    return data.map((_, i) => {
      const angle = startAngle + i * angleStep
      return `${centerX + r * Math.cos(angle)},${centerY + r * Math.sin(angle)}`
    }).join(' ')
  })

  return (
    <div style={{ width: '100%', maxWidth: width, margin: '0 auto', overflow: 'hidden', aspectRatio: `${width} / ${height}` }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet" style={{ display: 'block' }}>
        {grids.map((p, i) => (
          <polygon key={i} points={p} fill="none" stroke="#e8e8e8" strokeWidth="1" />
        ))}
        {data.map((_, i) => {
          const angle = startAngle + i * angleStep
          return (
            <line
              key={i}
              x1={centerX}
              y1={centerY}
              x2={centerX + radius * Math.cos(angle)}
              y2={centerY + radius * Math.sin(angle)}
              stroke="#e8e8e8"
              strokeWidth="1"
            />
          )
        })}
        <polygon
          points={points.map(p => `${p.x},${p.y}`).join(' ')}
          fill="rgba(114, 46, 209, 0.3)"
          stroke="#722ed1"
          strokeWidth="2"
        />
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="4" fill="#722ed1" />
        ))}
        {labels.map((l, i) => (
          <text key={i} x={l.x} y={l.y} textAnchor="middle" dominantBaseline="middle" fontSize="12" fill="#595959">
            {l.label}
          </text>
        ))}
      </svg>
    </div>
  )
}

// 柱状图组件 - 响应式版本
const BarChart = ({ data, width = 350, height = 180 }: { data: { label: string; value: number; color?: string }[]; width?: number; height?: number }) => {
  const maxValue = Math.max(...data.map(d => d.value), 100)
  const barWidth = (width - 40) / data.length - 8
  const chartHeight = height - 40

  return (
    <div style={{ width: '100%', maxWidth: width, margin: '0 auto', overflow: 'hidden', aspectRatio: `${width} / ${height}` }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet" style={{ display: 'block' }}>
        {[0, 25, 50, 75, 100].map(pct => (
          <line
            key={pct}
            x1="30"
            y1={chartHeight - (pct / 100) * chartHeight}
            x2={width - 10}
            y2={chartHeight - (pct / 100) * chartHeight}
            stroke="#f0f0f0"
            strokeDasharray="4"
          />
        ))}
        {data.map((d, i) => {
          const barHeight = (d.value / maxValue) * chartHeight
          const x = 35 + i * (barWidth + 8)
          const y = chartHeight - barHeight
          return (
            <g key={i}>
              <rect x={x} y={y} width={barWidth} height={barHeight} fill={d.color || '#722ed1'} rx="4" />
              <text x={x + barWidth / 2} y={chartHeight + 15} textAnchor="middle" fontSize="10" fill="#8c8c8c">
                {d.label}
              </text>
              <text x={x + barWidth / 2} y={y - 5} textAnchor="middle" fontSize="10" fill="#595959" fontWeight="bold">
                {d.value}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

export default function DeepProfile() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { user } = useAuthStore()
  const { aiPartners, setAiPartners } = useDeepProfileStore()

  const [localLoading, setLocalLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('mbti')
  const [mbtiResult, setMbtiResult] = useState<any>(null)
  const [sbtiResult, setSbtiResult] = useState<any>(null)
  const [attachmentResult, setAttachmentResult] = useState<any>(null)

  useEffect(() => {
    loadAllResults()
  }, [])

  const loadAllResults = async () => {
    setLocalLoading(true)
    try {
      // 使用 Promise.all 配合 try-catch，每个 API 独立处理错误
      let mbtiData = null
      let sbtiData = null
      let attachmentData = null
      let partnersData: any[] = []

      try {
        const res = await api.mbti.result()
        mbtiData = res
      } catch (e) {
        // 404 表示未测评，忽略错误
        mbtiData = null
      }

      try {
        const res = await api.sbti.result()
        sbtiData = res
      } catch (e) {
        sbtiData = null
      }

      try {
        const res = await api.attachment.result()
        attachmentData = res
      } catch (e) {
        attachmentData = null
      }

      try {
        const res = await api.profile.aiPartners()
        partnersData = res?.list || []
      } catch (e) {
        partnersData = []
      }

      setMbtiResult(mbtiData)
      setSbtiResult(sbtiData)
      setAttachmentResult(attachmentData)
      setAiPartners(partnersData)
    } catch (error) {
      console.error('加载测评结果失败:', error)
    } finally {
      setLocalLoading(false)
    }
  }

  if (localLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  const hasMbti = !!mbtiResult
  const hasSbti = !!sbtiResult
  const hasAttachment = !!attachmentResult
  const hasAnyResult = hasMbti || hasSbti || hasAttachment

  // 生成综合洞察
  const generateInsights = () => {
    const insights: string[] = []

    if (hasMbti && mbtiResult?.mbti_type) {
      insights.push(`你的人格类型是 ${mbtiResult.mbti_type}，属于${mbtiResult.personality?.split('，')[0] || '独特人格'}`)
    }
    if (hasSbti && sbtiResult?.top5_themes?.length > 0 && sbtiResult.top5_themes[0]) {
      insights.push(`你最强的才干主题是「${sbtiResult.top5_themes[0]}」，这是你独特的优势所在`)
      insights.push(`主导领域：${sbtiResult.dominant_domain || '待分析'}`)
    }
    if (hasAttachment && attachmentResult?.style) {
      insights.push(`在亲密关系中，你呈现${attachmentResult.style}的特点`)
    }

    if (hasMbti && hasSbti && mbtiResult?.mbti_type && sbtiResult?.top5_themes?.[0]) {
      insights.push(`${mbtiResult.mbti_type}人格结合「${sbtiResult.top5_themes[0]}」才干，你在人际交往中具有独特魅力`)
    }

    return insights
  }

  const insights = generateInsights()

  // 雷达图数据 - 使用后端返回的 percentage 字段
  const radarData = hasMbti && mbtiResult?.dimensions ? [
    { label: '外向', value: mbtiResult.dimensions[0]?.percentage || 50 },
    { label: '直觉', value: mbtiResult.dimensions[1]?.percentage || 50 },
    { label: '情感', value: mbtiResult.dimensions[2]?.percentage || 50 },
    { label: '知觉', value: mbtiResult.dimensions[3]?.percentage || 50 },
  ] : []

  // 才干柱状图数据 - 添加空值检查
  const themeData = (sbtiResult?.top5_themes || [])
    .filter((t: string) => t)  // 过滤空值
    .map((t: string, i: number) => ({
      label: t.slice(0, 2) || '未知',
      value: sbtiResult.top5_scores?.[i] || 0,
      color: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][i],
    }))

  // 领域分布数据
  const domainData = hasSbti && sbtiResult.domain_scores ? [
    { label: '执行力', value: sbtiResult.domain_scores.执行力 || 0 },
    { label: '影响力', value: sbtiResult.domain_scores.影响力 || 0 },
    { label: '关系建立', value: sbtiResult.domain_scores.关系建立 || 0 },
    { label: '战略思维', value: sbtiResult.domain_scores.战略思维 || 0 },
  ] : []

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 50%, #fa8c16 100%)',
        padding: '40px 24px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        zIndex: 1,
      }}>
        <div className="container">
          <div style={{ position: 'relative' }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(-1)}
              type="text"
              style={{ color: '#fff', position: 'absolute', left: 0, top: 0 }}
              size="large"
            />
          </div>
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
            <UserOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 8, color: '#fff' }}>深度人格画像</h1>
          <p style={{ fontSize: 16, opacity: 0.9 }}>
            MBTI + SBTI + 依恋风格，三位一体深度分析
          </p>
          <div style={{ marginTop: 16, display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            {hasMbti && <Tag style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff' }}>{mbtiResult.mbti_type}</Tag>}
            {hasSbti && <Tag style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff' }}>{sbtiResult.top5_themes?.[0]}</Tag>}
            {hasAttachment && <Tag style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff' }}>{attachmentResult.style}</Tag>}
          </div>
        </div>
      </header>

      <div className="container" style={{ marginTop: -20 }}>
        {/* 未测评用户的引导页面 */}
        {!hasAnyResult && (
          <Card style={{ marginBottom: 24, textAlign: 'center' }}>
            <div style={{ padding: '20px 0' }}>
              <SolutionOutlined style={{ fontSize: 48, color: '#722ed1', marginBottom: 16 }} />
              <h2 style={{ color: '#595959', marginBottom: 8 }}>开启你的深度人格探索之旅</h2>
              <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
                完成 MBTI、SBTI、依恋风格 三大测评，获得专属的AI伴侣匹配
              </p>
              <Row gutter={[16, 16]} justify="center">
                <Col xs={24} sm={8}>
                  <Card hoverable style={{ height: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <UserOutlined style={{ fontSize: 32, color: '#722ed1' }} />
                      <h4 style={{ marginTop: 12 }}>MBTI人格测试</h4>
                      <p style={{ fontSize: 12, color: '#8c8c8c' }}>16种人格类型，找出真实的自己</p>
                      <Link to="/mbti">
                        <Button type="primary" style={{ background: '#722ed1', marginTop: 8 }}>开始测评</Button>
                      </Link>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card hoverable style={{ height: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <CrownOutlined style={{ fontSize: 32, color: '#eb2f96' }} />
                      <h4 style={{ marginTop: 12 }}>SBTI才干测试</h4>
                      <p style={{ fontSize: 12, color: '#8c8c8c' }}>34个才干主题，发现你的核心优势</p>
                      <Link to="/sbti/test">
                        <Button type="primary" style={{ background: '#eb2f96', marginTop: 8 }}>开始测评</Button>
                      </Link>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card hoverable style={{ height: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <HeartOutlined style={{ fontSize: 32, color: '#fa8c16' }} />
                      <h4 style={{ marginTop: 12 }}>依恋风格测试</h4>
                      <p style={{ fontSize: 12, color: '#8c8c8c' }}>4种依恋类型，了解你的情感模式</p>
                      <Link to="/attachment/test">
                        <Button type="primary" style={{ background: '#fa8c16', marginTop: 8 }}>开始测评</Button>
                      </Link>
                    </div>
                  </Card>
                </Col>
              </Row>
              <div style={{ marginTop: 24 }}>
                <Link to="/comprehensive">
                  <Button type="primary" size="large" style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)' }}>
                    一键完成三大测评
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        )}

        {/* Comprehensive Insights */}
        {hasAnyResult && insights.length > 0 && (
          <Card
            style={{ marginBottom: 24 }}
            headStyle={{ background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)', color: '#fff' }}
            title={<span style={{ color: '#fff' }}><CrownOutlined style={{ marginRight: 8 }} />综合洞察</span>}
          >
            <List
              dataSource={insights}
              renderItem={(item, index) => (
                <List.Item>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: '#722ed1',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 12,
                      fontWeight: 'bold',
                    }}>
                      {index + 1}
                    </div>
                    <span>{item}</span>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* Tab Navigation */}
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          style={{ position: 'relative', zIndex: 10 }}
          items={[
            {
              key: 'mbti',
              label: (
                <span>
                  <UserOutlined /> MBTI人格
                </span>
              ),
              children: hasMbti ? (
                <Row gutter={[24, 24]}>
                  <Col xs={24} md={8}>
                    <Card style={{ textAlign: 'center', height: '100%', overflow: 'hidden' }}>
                      <div style={{ fontSize: 'clamp(36px, 8vw, 64px)', fontWeight: 'bold', color: '#722ed1', marginBottom: 16, wordBreak: 'break-all', lineHeight: 1.2 }}>
                        {mbtiResult.mbti_type}
                      </div>
                      <p style={{ color: '#595959', marginBottom: 16, wordBreak: 'break-word', overflow: 'hidden', textAlign: 'center' }}>{mbtiResult.personality}</p>
                    </Card>
                  </Col>

                  <Col xs={24} md={8}>
                    <Card style={{ height: '100%' }}>
                      <h4 style={{ textAlign: 'center', marginBottom: 16 }}>维度分析</h4>
                      {radarData.length > 0 && <RadarChart data={radarData} />}
                    </Card>
                  </Col>

                  <Col xs={24} md={8}>
                    <Card style={{ height: '100%' }}>
                      <h4 style={{ marginBottom: 16 }}>各维度得分</h4>
                      {mbtiResult.dimensions?.map((dim: any, i: number) => (
                        <div key={i} style={{ marginBottom: 16 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span>{dim.dimension === 'EI' ? '外向-内向' : dim.dimension === 'SN' ? '感觉-直觉' : dim.dimension === 'TF' ? '思维-情感' : '判断-知觉'}</span>
                            <Tag>{dim.tendency}</Tag>
                          </div>
                          <Progress
                            percent={dim.percentage || 50}
                            strokeColor="#722ed1"
                            size="small"
                            format={percent => `${percent}%`}
                          />
                        </div>
                      ))}
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="性格优势">
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {mbtiResult.strengths?.map((s: string, i: number) => (
                          <Tag key={i} color="green">{s}</Tag>
                        ))}
                      </div>
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="关系建议" style={{ overflow: 'hidden' }}>
                      <p style={{ color: '#595959', lineHeight: 1.8, wordBreak: 'break-word' }}>
                        {mbtiResult.relationship_tips}
                      </p>
                    </Card>
                  </Col>
                </Row>
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无MBTI测评结果">
                  <Link to="/mbti">
                    <Button type="primary" style={{ background: '#722ed1' }}>去测评</Button>
                  </Link>
                </Empty>
              ),
            },
            {
              key: 'sbti',
              label: (
                <span>
                  <CrownOutlined /> SBTI才干
                </span>
              ),
              children: hasSbti && sbtiResult?.top5_themes?.length > 0 ? (
                <Row gutter={[24, 24]}>
                  <Col xs={24}>
                    <Card title="Top 5 才干主题">
                      <Row gutter={[16, 16]}>
                        {sbtiResult.top5_themes.filter((theme: string) => theme).map((theme: string, i: number) => (
                          <Col xs={24} sm={12} md={8} lg={5} key={theme + i}>
                            <Card
                              style={{
                                textAlign: 'center',
                                borderTop: `4px solid ${['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][i] || '#722ed1'}`,
                              }}
                              size="small"
                            >
                              <Badge count={i + 1} style={{ backgroundColor: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][i] || '#722ed1' }} />
                              <h4 style={{ marginTop: 8 }}>{theme}</h4>
                              <div style={{ fontWeight: 'bold', color: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][i] || '#722ed1' }}>
                                {sbtiResult.top5_scores?.[i] || 0}分
                              </div>
                            </Card>
                          </Col>
                        ))}
                      </Row>
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="才干得分分布">
                      {themeData.length > 0 && <BarChart data={themeData} />}
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="四大领域分布">
                      {domainData.length > 0 && <RadarChart data={domainData} />}
                    </Card>
                  </Col>

                  {sbtiResult.report?.relationship_insights && (
                    <Col xs={24}>
                      <Card
                        title="关系优势分析"
                        headStyle={{ background: 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)' }}
                      >
                        <Row gutter={[24, 16]}>
                          <Col xs={24} md={8}>
                            <strong>沟通风格：</strong>
                            <p>{sbtiResult.report.relationship_insights.communication_style}</p>
                          </Col>
                          <Col xs={24} md={8}>
                            <strong>关系优势：</strong>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                              {sbtiResult.report.relationship_insights.strengths?.map((s: string, i: number) => (
                                <Tag key={i} color="green">{s}</Tag>
                              ))}
                            </div>
                          </Col>
                          <Col xs={24} md={8}>
                            <strong>成长方向：</strong>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                              {sbtiResult.report.relationship_insights.growth_areas?.map((s: string, i: number) => (
                                <Tag key={i} color="orange">{s}</Tag>
                              ))}
                            </div>
                          </Col>
                        </Row>
                      </Card>
                    </Col>
                  )}

                  {sbtiResult.report?.career_suggestions && (
                    <Col xs={24}>
                      <Card title="职业发展建议">
                        <Row gutter={[16, 16]}>
                          {sbtiResult.report.career_suggestions?.map((s: string, i: number) => (
                            <Col xs={24} sm={12} md={8} key={i}>
                              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                                <CheckCircleOutlined style={{ color: '#52c41a', marginTop: 4 }} />
                                <span>{s}</span>
                              </div>
                            </Col>
                          ))}
                        </Row>
                      </Card>
                    </Col>
                  )}
                </Row>
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无SBTI测评结果">
                  <Link to="/sbti/test">
                    <Button type="primary" style={{ background: '#722ed1' }}>去测评</Button>
                  </Link>
                </Empty>
              ),
            },
            {
              key: 'attachment',
              label: (
                <span>
                  <HeartOutlined /> 依恋风格
                </span>
              ),
              children: hasAttachment ? (
                <Row gutter={[24, 24]}>
                  <Col xs={24} md={8}>
                    <Card
                      style={{
                        textAlign: 'center',
                        height: '100%',
                        borderTop: `4px solid ${
                          attachmentResult.style === '安全型' ? '#52c41a' :
                          attachmentResult.style === '焦虑型' ? '#fa8c16' :
                          attachmentResult.style === '回避型' ? '#1890ff' : '#eb2f96'
                        }`,
                      }}
                    >
                      <div style={{ marginBottom: 16 }}>
                        <HeartOutlined
                          style={{
                            fontSize: 48,
                            color: attachmentResult.style === '安全型' ? '#52c41a' :
                                   attachmentResult.style === '焦虑型' ? '#fa8c16' :
                                   attachmentResult.style === '回避型' ? '#1890ff' : '#eb2f96',
                          }}
                        />
                      </div>
                      <Tag
                        color={attachmentResult.style === '安全型' ? 'green' :
                               attachmentResult.style === '焦虑型' ? 'orange' :
                               attachmentResult.style === '回避型' ? 'blue' : 'magenta'}
                        style={{ fontSize: 16, padding: '4px 16px' }}
                      >
                        {attachmentResult.style}
                      </Tag>
                    </Card>
                  </Col>

                  <Col xs={24} md={8}>
                    <Card title="维度分析">
                      <div style={{ marginBottom: 24 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span>焦虑程度</span>
                          <span style={{ color: '#eb2f96', fontWeight: 'bold' }}>{Math.round((attachmentResult.anxiety_score / 7) * 100)}%</span>
                        </div>
                        <Progress percent={Math.round((attachmentResult.anxiety_score / 7) * 100)} strokeColor="#eb2f96" trailColor="#f0f0f0" />
                      </div>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span>回避程度</span>
                          <span style={{ color: '#1890ff', fontWeight: 'bold' }}>{Math.round((attachmentResult.avoidance_score / 7) * 100)}%</span>
                        </div>
                        <Progress percent={Math.round((attachmentResult.avoidance_score / 7) * 100)} strokeColor="#1890ff" trailColor="#f0f0f0" />
                      </div>
                    </Card>
                  </Col>

                  <Col xs={24} md={8}>
                    <Card title="依恋特征">
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {attachmentResult.characteristics?.map((c: string, i: number) => (
                          <Tag key={i}>{c}</Tag>
                        ))}
                      </div>
                    </Card>
                  </Col>

                  {attachmentResult.relationship_tips && (
                    <Col xs={24}>
                      <Card
                        title="关系提升建议"
                        headStyle={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #adc6ff 100%)' }}
                      >
                        <p style={{ lineHeight: 2, color: '#595959' }}>{attachmentResult.relationship_tips}</p>
                      </Card>
                    </Col>
                  )}

                  {attachmentResult.self_growth_tips && (
                    <Col xs={24}>
                      <Card
                        title="个人成长建议"
                        headStyle={{ background: 'linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%)' }}
                      >
                        <p style={{ lineHeight: 2, color: '#595959' }}>{attachmentResult.self_growth_tips}</p>
                      </Card>
                    </Col>
                  )}
                </Row>
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无依恋风格测评结果">
                  <Link to="/attachment/test">
                    <Button type="primary" style={{ background: '#eb2f96' }}>去测评</Button>
                  </Link>
                </Empty>
              ),
            },
          ]}
        />

        {/* AI Partner Recommendations */}
        <Card
          style={{ marginTop: 24 }}
          headStyle={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', color: '#fff' }}
          title={<span style={{ color: '#fff' }}><RobotOutlined style={{ marginRight: 8 }} />为你匹配的AI伴侣</span>}
        >
          {aiPartners.length > 0 ? (
            <Row gutter={[16, 16]}>
              {aiPartners.map((partner: any) => (
                <Col xs={24} sm={12} md={8} key={partner.id}>
                  <Card hoverable onClick={() => navigate(`/chat?assistant_id=${partner.id}`)} style={{ height: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <Avatar
                        size={64}
                        src={partner.avatar}
                        style={{ background: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)', marginBottom: 16, fontSize: 28 }}
                      >
                        {partner.name?.[0]}
                      </Avatar>
                      <h4>{partner.name}</h4>
                      <div style={{ marginBottom: 8 }}>
                        {partner.mbti_type && <Tag color="purple">{partner.mbti_type}</Tag>}
                        {partner.attachment_style && <Tag color="green">{partner.attachment_style}</Tag>}
                      </div>
                      <p style={{ color: '#8c8c8c', fontSize: 13, marginBottom: 12 }}>
                        {partner.match_reason || partner.personality?.slice(0, 60)}...
                      </p>
                      <Button type="primary" size="small" style={{ background: '#722ed1' }}>
                        开始聊天
                      </Button>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Empty description="暂无匹配的AI伴侣" />
          )}
        </Card>

        {/* Actions */}
        <div style={{ textAlign: 'center', marginTop: 32, display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/comprehensive"><Button type="primary" size="large" style={{ background: '#722ed1', minWidth: 140 }}>三位一体测评</Button></Link>
          {!hasMbti && <Link to="/mbti"><Button size="large" style={{ minWidth: 120 }}>测评MBTI</Button></Link>}
          {!hasSbti && <Link to="/sbti/test"><Button size="large" style={{ minWidth: 120 }}>测评SBTI</Button></Link>}
          {!hasAttachment && <Link to="/attachment/test"><Button size="large" style={{ minWidth: 140 }}>测评依恋风格</Button></Link>}
          <Link to="/chat"><Button type="primary" size="large" style={{ background: '#722ed1', minWidth: 120 }}>开始聊天</Button></Link>
        </div>
      </div>
    </div>
  )
}
