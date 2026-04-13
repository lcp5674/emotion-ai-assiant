import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Spin, App, Tabs, List, Avatar, Empty, Progress, Badge } from 'antd'
import { UserOutlined, CrownOutlined, HeartOutlined, RobotOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useDeepProfileStore, useAuthStore } from '../../stores'

// 雷达图组件
const RadarChart = ({ data, width = 280, height = 280 }: { data: { label: string; value: number }[]; width?: number; height?: number }) => {
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
    <svg width={width} height={height} style={{ display: 'block', margin: '0 auto' }}>
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
  )
}

// 柱状图组件
const BarChart = ({ data, width = 350, height = 180 }: { data: { label: string; value: number; color?: string }[]; width?: number; height?: number }) => {
  const maxValue = Math.max(...data.map(d => d.value), 100)
  const barWidth = (width - 40) / data.length - 8
  const chartHeight = height - 40

  return (
    <svg width={width} height={height} style={{ display: 'block', margin: '0 auto' }}>
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
      const [mbti, sbti, attachment, partners] = await Promise.allSettled([
        api.mbti.result().catch(() => null),
        api.sbti.result().catch(() => null),
        api.attachment.result().catch(() => null),
        api.profile.aiPartners().catch(() => ({ list: [] })),
      ])

      if (mbti.status === 'fulfilled') setMbtiResult(mbti.value)
      if (sbti.status === 'fulfilled') setSbtiResult(sbti.value)
      if (attachment.status === 'fulfilled') setAttachmentResult(attachment.value)
      if (partners.status === 'fulfilled') setAiPartners(partners.value.list || [])
    } catch (error) {
      console.error(error)
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
                    <Card style={{ textAlign: 'center', height: '100%' }}>
                      <div style={{ fontSize: 64, fontWeight: 'bold', color: '#722ed1', marginBottom: 16 }}>
                        {mbtiResult.mbti_type}
                      </div>
                      <p style={{ color: '#595959', marginBottom: 16 }}>{mbtiResult.personality}</p>
                      <Tag color="purple">{mbtiResult.personality?.split('，')[0]}</Tag>
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
                            percent={Math.min(Math.abs(dim.score) * 5 + 50, 100)}
                            strokeColor="#722ed1"
                            size="small"
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
                    <Card title="关系建议">
                      <p style={{ color: '#595959', lineHeight: 1.8 }}>
                        {mbtiResult.relationship_tips}
                      </p>
                    </Card>
                  </Col>
                </Row>
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无MBTI测评结果">
                  <Link to="/mbti/test">
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
                          <span style={{ color: '#eb2f96', fontWeight: 'bold' }}>{attachmentResult.anxiety_score}%</span>
                        </div>
                        <Progress percent={attachmentResult.anxiety_score} strokeColor="#eb2f96" trailColor="#f0f0f0" />
                      </div>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span>回避程度</span>
                          <span style={{ color: '#1890ff', fontWeight: 'bold' }}>{attachmentResult.avoidance_score}%</span>
                        </div>
                        <Progress percent={attachmentResult.avoidance_score} strokeColor="#1890ff" trailColor="#f0f0f0" />
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
          {!hasMbti && <Link to="/mbti/test"><Button type="primary" style={{ background: '#722ed1' }}>测评MBTI</Button></Link>}
          {!hasSbti && <Link to="/sbti/test"><Button type="primary" style={{ background: '#722ed1' }}>测评SBTI</Button></Link>}
          {!hasAttachment && <Link to="/attachment/test"><Button type="primary" style={{ background: '#eb2f96' }}>测评依恋风格</Button></Link>}
          <Link to="/chat"><Button size="large">开始聊天</Button></Link>
        </div>
      </div>
    </div>
  )
}
