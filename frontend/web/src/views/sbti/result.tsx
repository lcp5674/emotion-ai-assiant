import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Tag, Row, Col, Progress, Spin, App, List, Avatar } from 'antd'
import { CrownOutlined, HeartOutlined, RocketOutlined, CheckCircleOutlined, RadarChartOutlined, ArrowLeftOutlined, RightOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useSbtiStore } from '../../stores'

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

// 柱状图组件
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

// 才干主题详细描述
const THEME_DESCRIPTIONS: Record<string, { description: string; strengths: string[]; career: string }> = {
  "成就": { description: "追求卓越，享受完成任务和达成目标的成就感", strengths: ["高绩效", "自我驱动", "持续进步"], career: "项目管理、销售、创业" },
  "行动": { description: "喜欢立即行动，快速将想法付诸实践", strengths: ["执行力强", "果断", "高效"], career: "企业家、应急响应、销售" },
  "适应": { description: "灵活变通，能够快速适应变化的环境和情况", strengths: ["灵活", "务实", "抗压"], career: "咨询、媒体、公关" },
  "统筹": { description: "善于组织和协调资源，能够高效管理系统和流程", strengths: ["组织力", "协调力", "系统性"], career: "运营管理、物流、人力资源" },
  "信仰": { description: "重视传统和价值观，寻求做事方式背后的意义", strengths: ["坚定", "有原则", "使命感"], career: "非营利组织、教育、宗教服务" },
  "公平": { description: "重视公正和平等，对不一致和不公平非常敏感", strengths: ["正义感", "诚信", "公正"], career: "法律、人力资源、审计" },
  "审慎": { description: "行事谨慎，在行动前会充分考虑风险", strengths: ["风险意识", "深思熟虑", "稳健"], career: "风险管理、金融、合规" },
  "纪律": { description: "做事有章法，喜欢按照计划和流程进行", strengths: ["自律", "可靠", "细致"], career: "会计、质量管理、行政" },
  "专注": { description: "能够排除干扰，全身心投入重要的事情", strengths: ["专注", "深入", "耐心"], career: "研究、编程、写作" },
  "责任": { description: "言出必行，对承诺的事情负责到底", strengths: ["可靠", "敬业", "诚信"], career: "医疗、教育、咨询" },
  "排难": { description: "善于解决问题，能够在困难面前保持冷静", strengths: ["问题解决", "冷静", "技术能力"], career: "工程、技术支持、咨询" },
  "统率": { description: "具有领导才能，能够掌控局面并做出决定", strengths: ["领导力", "决策力", "影响力"], career: "管理、创业、政治" },
  "沟通": { description: "善于表达和交流，能够激发他人的热情和想法", strengths: ["表达力", "说服力", "感染力"], career: "销售、市场、营销" },
  "竞争": { description: "有进取心，喜欢与他人比较并追求领先", strengths: ["进取", "目标导向", "不服输"], career: "销售、金融、竞技行业" },
  "完美": { description: "追求卓越，欣赏美好和优秀的人和事物", strengths: ["追求卓越", "高品质", "审美"], career: "设计、咨询、质量管理" },
  "自信": { description: "对自己有清晰的认识，相信自己有能力做好事情", strengths: ["自信", "果断", "自主"], career: "管理、创业、演讲" },
  "追求": { description: "渴望被认可，希望自己的贡献被重视", strengths: ["上进", "有目标", "积极"], career: "销售、市场、表演" },
  "取悦": { description: "喜欢结交朋友，善于赢得他人的好感和认可", strengths: ["友好", "善于交际", "受欢迎"], career: "销售、客服、人力资源" },
  "关联": { description: "相信万事皆有关联，重视人际之间的联系和共同点", strengths: ["全局思维", "善于联系", "包容"], career: "咨询、研究、战略规划" },
  "伯乐": { description: "善于发现他人的潜能，乐于培养和指导他人", strengths: ["识人", "培养人", "耐心"], career: "人力资源、培训、管理" },
  "体谅": { description: "善于理解他人，能够设身处地为别人着想", strengths: ["同理心", "敏感", "支持性"], career: "咨询、护理、社工" },
  "和谐": { description: "寻求共识和一致，避免冲突和争议", strengths: ["调解", "平和", "合作"], career: "人力资源、外交、调解" },
  "包容": { description: "接纳并欣赏人与人之间的差异，尊重不同观点", strengths: ["开放", "接纳", "多元化"], career: "人力资源、教育、国际事务" },
  "个别": { description: "善于识别每个人的独特之处，关注个体差异", strengths: ["洞察力", "个性化", "关注细节"], career: "销售、咨询、治疗" },
  "积极": { description: "充满活力，善于激励自己和他人", strengths: ["活力", "乐观", "激励他人"], career: "培训、销售、表演" },
  "交往": { description: "喜欢结交和维护朋友，享受深度的人际交流", strengths: ["社交能力", "忠诚", "深度连接"], career: "销售、咨询、公关" },
  "分析": { description: "善于深入分析问题，寻找事物背后的逻辑和规律", strengths: ["逻辑思维", "理性", "数据驱动"], career: "研究、金融、咨询" },
  "回顾": { description: "善于从过去的经验中学习，理解当前的情境", strengths: ["经验导向", "务实", "历史视角"], career: "历史、教育、顾问" },
  "前瞻": { description: "善于预见未来可能性，对长远发展有敏锐的直觉", strengths: ["预见力", "战略思维", "愿景"], career: "战略规划、创业、投资" },
  "理念": { description: "追求深层意义，喜欢思考抽象和哲学问题", strengths: ["抽象思维", "理想主义", "深度思考"], career: "哲学、教育、研究" },
  "搜集": { description: "好奇心强，喜欢收集信息和资源", strengths: ["好奇心", "研究能力", "知识广博"], career: "研究、新闻、图书管理" },
  "思维": { description: "善于独立思考，喜欢深入分析问题", strengths: ["独立思考", "批判性", "智慧"], career: "研究、咨询、学术" },
  "学习": { description: "热爱学习，享受获取新知识和技能的过程", strengths: ["学习能力", "好奇心", "成长心态"], career: "研究、教育、咨询" },
  "战略": { description: "善于制定长远计划，能够看到全局和可能性", strengths: ["战略思维", "全局观", "规划能力"], career: "战略规划、咨询、管理" },
}

export default function SbtiResult() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { result, setResult } = useSbtiStore()
  const [loading, setLoading] = useState(!result)
  const [assistants, setAssistants] = useState<any[]>([])
  const [attachmentCompleted, setAttachmentCompleted] = useState(false)

  useEffect(() => {
    if (!result) {
      loadResult()
    }
    loadAssistants()
    checkAttachmentCompletion()
  }, [])

  const loadResult = async () => {
    setLoading(true)
    try {
      const res = await api.sbti.result()
      setResult(res)
    } catch (error: any) {
      if (error.response?.status === 404) {
        message.info('请先完成SBTI测试')
        navigate('/sbti')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadAssistants = async () => {
    try {
      const res = await api.mbti.assistants({ recommended: true })
      setAssistants(res.list?.slice(0, 3) || [])
    } catch (error) {
      console.error(error)
    }
  }

  const checkAttachmentCompletion = async () => {
    try {
      const res = await api.attachment.result()
      setAttachmentCompleted(!!res)
    } catch {
      setAttachmentCompleted(false)
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
        <h2>请先完成SBTI测试</h2>
        <Link to="/sbti">
          <Button type="primary" style={{ marginTop: 16, background: '#722ed1' }}>
            开始测试
          </Button>
        </Link>
      </div>
    )
  }

  // 构建雷达图数据（四大领域）
  const domainData = [
    { label: '执行力', value: result.domain_scores?.执行力 || 0 },
    { label: '影响力', value: result.domain_scores?.影响力 || 0 },
    { label: '关系建立', value: result.domain_scores?.关系建立 || 0 },
    { label: '战略思维', value: result.domain_scores?.战略思维 || 0 },
  ]

  // 构建柱状图数据（Top5才干）
  const top5Data = result.top5_themes?.map((theme, i) => ({
    label: theme.slice(0, 2),
    value: result.top5_scores?.[i] || 0,
    color: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][i],
  })) || []

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
            <CrownOutlined style={{ fontSize: 40, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 8, color: '#fff' }}>你的五大才干主题</h1>
          <p style={{ fontSize: 16, opacity: 0.9 }}>
            主导领域：<strong>{result.dominant_domain}</strong>
          </p>
        </div>
      </header>

      <div className="container" style={{ marginTop: -20 }}>
        {/* Back Button */}
        <div style={{ marginBottom: 16 }}>
          <Link to="/sbti">
            <Button icon={<ArrowLeftOutlined />}>返回测试</Button>
          </Link>
        </div>

        {/* Top 5 Themes */}
        <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
          {result.top5_themes?.map((theme, index) => {
            const themeInfo = THEME_DESCRIPTIONS[theme] || {
              description: '暂无详细描述',
              strengths: [],
              career: '待定'
            }
            return (
              <Col xs={24} sm={12} md={8} key={theme}>
                <Card
                  style={{
                    height: '100%',
                    borderTop: `4px solid ${['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][index]}`,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      background: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][index],
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      marginRight: 12,
                    }}>
                      {index + 1}
                    </div>
                    <h3 style={{ margin: 0, fontSize: 18 }}>{theme}</h3>
                  </div>

                  <p style={{ color: '#595959', marginBottom: 12, fontSize: 14 }}>
                    {themeInfo.description}
                  </p>

                  <div style={{ marginBottom: 8 }}>
                    <strong style={{ fontSize: 12, color: '#8c8c8c' }}>核心优势</strong>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                      {themeInfo.strengths.map((s, i) => (
                        <Tag key={i} color={['purple', 'magenta', 'green'][i % 3]} style={{ fontSize: 12 }}>{s}</Tag>
                      ))}
                    </div>
                  </div>

                  <div>
                    <strong style={{ fontSize: 12, color: '#8c8c8c' }}>适合领域</strong>
                    <p style={{ margin: '4px 0 0', fontSize: 13 }}>{themeInfo.career}</p>
                  </div>

                  <div style={{ marginTop: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 12, color: '#8c8c8c' }}>得分</span>
                      <span style={{ fontWeight: 'bold', color: ['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][index] }}>
                        {result.top5_scores?.[index] || 0}
                      </span>
                    </div>
                    <Progress
                      percent={Math.min((result.top5_scores?.[index] || 0), 100)}
                      showInfo={false}
                      strokeColor={['#722ed1', '#eb2f96', '#52c41a', '#fa8c16', '#1890ff'][index]}
                      trailColor="#f0f0f0"
                    />
                  </div>
                </Card>
              </Col>
            )
          })}
        </Row>

        {/* Domain Distribution */}
        <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
          <Col xs={24} md={12}>
            <Card title="四大领域分布">
              <RadarChart data={domainData} />
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="Top 5 才干得分">
              <BarChart data={top5Data} />
            </Card>
          </Col>
        </Row>

        {/* Relationship Insights */}
        {result.report?.relationship_insights && (
          <Card
            style={{ marginBottom: 24 }}
            headStyle={{ background: 'linear-gradient(135deg, #fff7e6 0%, #ffd591 100%)' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <HeartOutlined style={{ fontSize: 32, color: '#fa8c16', marginTop: 4 }} />
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 12px' }}>关系优势分析</h3>
                <div style={{ marginBottom: 12 }}>
                  <strong>沟通风格：</strong>
                  <span>{result.report.relationship_insights.communication_style}</span>
                </div>
                <div>
                  <strong>关系优势：</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                    {result.report.relationship_insights.strengths?.map((s, i) => (
                      <Tag key={i} color="green">{s}</Tag>
                    ))}
                  </div>
                </div>
                <div style={{ marginTop: 12 }}>
                  <strong>成长方向：</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                    {result.report.relationship_insights.growth_areas?.map((s, i) => (
                      <Tag key={i} color="orange">{s}</Tag>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Career Suggestions */}
        {result.report?.career_suggestions && (
          <Card
            style={{ marginBottom: 24 }}
            headStyle={{ background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <RocketOutlined style={{ fontSize: 32, color: '#52c41a', marginTop: 4 }} />
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 12px' }}>职业发展建议</h3>
                <List
                  size="small"
                  dataSource={result.report.career_suggestions}
                  renderItem={(item) => (
                    <List.Item style={{ padding: '8px 0' }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                      {item}
                    </List.Item>
                  )}
                />
              </div>
            </div>
          </Card>
        )}

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
                    <Avatar
                      size={64}
                      src={assistant.avatar}
                      style={{
                        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
                        margin: '0 auto 16px',
                        fontSize: 28,
                      }}
                    >
                      {assistant.name?.[0]}
                    </Avatar>
                    <h4>{assistant.name}</h4>
                    <p style={{ color: '#8c8c8c', fontSize: 14, marginBottom: 8 }}>
                      {assistant.personality?.slice(0, 50)}...
                    </p>
                    <Tag color="purple">{assistant.mbti_type}</Tag>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* Actions */}
        <div style={{ textAlign: 'center', marginTop: 32, display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          {/* 继续下一测评入口 */}
          {!attachmentCompleted && (
            <Button
              type="primary"
              size="large"
              icon={<RightOutlined />}
              onClick={() => navigate('/attachment/test')}
              style={{ background: 'linear-gradient(135deg, #eb2f96 0%, #b37feb 100%)', height: 56, fontSize: 16, paddingInline: 32 }}
            >
              完成依恋风格测评，探索你的情感模式
            </Button>
          )}
          <Link to="/chat">
            <Button type="primary" size="large" style={{ background: '#722ed1' }}>
              开始聊天
            </Button>
          </Link>
          <Link to="/sbti/test">
            <Button size="large">重新测评</Button>
          </Link>
          <Link to="/profile/deep">
            <Button size="large" type="primary" style={{ background: '#eb2f96' }}>
              查看深度画像
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
