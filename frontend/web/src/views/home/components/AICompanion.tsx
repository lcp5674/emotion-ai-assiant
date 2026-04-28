import { Card, Button, Row, Col, Tag } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../../../hooks/useTheme'
import { useEffect, useState } from 'react'

interface Assistant {
  id: string
  name: string
  emoji: string
  tagline: string
  desc: string
  color: string
  gradient: string
  specialty: string[]
}

interface Props {
  assistants?: Assistant[]
}

// 浮动动画组件
const FloatingCard: React.FC<{ children: React.ReactNode; delay: number; assistant: Assistant }> = ({
  children,
  delay,
  assistant,
}) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
        transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {children}
    </div>
  )
}

const defaultAssistants: Assistant[] = [
  {
    id: 'zen',
    name: '静心',
    emoji: '💜',
    tagline: '倾听你每一个细微的声音',
    desc: '适合深夜独处、情绪波动时的陪伴',
    color: '#722ed1',
    gradient: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
    specialty: ['情绪疏导', '深夜倾听', '压力释放'],
  },
  {
    id: 'aware',
    name: '觉察',
    emoji: '💙',
    tagline: '帮你看清内心的迷雾',
    desc: '引导你发现潜意识中的真实想法',
    color: '#1890ff',
    gradient: 'linear-gradient(135deg, #1890ff 0%, #69c0ff 100%)',
    specialty: ['自我探索', '模式发现', '认知重构'],
  },
  {
    id: 'bloom',
    name: '绽放',
    emoji: '🧡',
    tagline: '陪伴你成为更好的自己',
    desc: '基于你的特质定制的成长建议',
    color: ' #fa8c16',
    gradient: 'linear-gradient(135deg, #fa8c16 0%, #ffc069 100%)',
    specialty: ['优势发展', '弱点克服', '成长路径'],
  },
  {
    id: 'courage',
    name: '勇气',
    emoji: '✨',
    tagline: '在你需要勇敢的时刻',
    desc: '给你力量去面对困难的决定',
    color: '#52c41a',
    gradient: 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)',
    specialty: ['决策支持', '恐惧面对', '行动激励'],
  },
]

export function AICompanion({ assistants = defaultAssistants }: Props) {
  const navigate = useNavigate()
  const { themeColor, themeColors } = useTheme()

  return (
    <div style={{ marginBottom: 32 }}>
      {/* 标题 */}
      <div style={{ marginBottom: 20 }}>
        <h2
          style={{
            fontSize: 22,
            fontWeight: 700,
            margin: 0,
            color: '#1f2937',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span>💝</span> 为你精选的陪伴
        </h2>
        <p
          style={{
            fontSize: 14,
            color: '#9ca3af',
            margin: '8px 0 0',
          }}
        >
          每一个都是独特的灵魂，选择你最想要的对话方式
        </p>
      </div>

      {/* 助手卡片网格 */}
      <Row gutter={[16, 16]}>
        {assistants.map((assistant, index) => (
          <Col xs={12} sm={12} md={6} key={assistant.id}>
            <FloatingCard delay={index * 150} assistant={assistant}>
              <Card
                hoverable
                style={{
                  borderRadius: 20,
                  border: `2px solid ${assistant.color}15`,
                  overflow: 'hidden',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
                bodyStyle={{ padding: 0 }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)'
                  e.currentTarget.style.boxShadow = `0 20px 40px ${assistant.color}25`
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)'
                  e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.06)'
                }}
              >
                {/* 头部渐变 */}
                <div
                  style={{
                    background: assistant.gradient,
                    padding: 24,
                    textAlign: 'center',
                    color: '#ffffff',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {/* 装饰圆 - 浮动动画 */}
                  <div
                    style={{
                      position: 'absolute',
                      top: -30,
                      right: -30,
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.15)',
                      animation: 'float 3s ease-in-out infinite',
                    }}
                  />
                  <div
                    style={{
                      position: 'absolute',
                      bottom: -20,
                      left: -20,
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.1)',
                      animation: 'float 4s ease-in-out infinite reverse',
                    }}
                  />
                  {/* 额外的装饰 */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '10%',
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.08)',
                      animation: 'float 5s ease-in-out infinite',
                      animationDelay: '0.5s',
                    }}
                  />

                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div
                      style={{
                        fontSize: 48,
                        marginBottom: 12,
                        animation: 'bounce 2s ease-in-out infinite',
                      }}
                    >
                      {assistant.emoji}
                    </div>
                    <h3
                      style={{
                        fontSize: 20,
                        fontWeight: 700,
                        margin: 0,
                        color: '#ffffff',
                      }}
                    >
                      {assistant.name}
                    </h3>
                    <p
                      style={{
                        fontSize: 13,
                        margin: '6px 0 0',
                        opacity: 0.9,
                      }}
                    >
                      {assistant.tagline}
                    </p>
                  </div>
                </div>

                {/* 内容区域 */}
                <div style={{ padding: 16 }}>
                  <p
                    style={{
                      fontSize: 13,
                      color: '#6b7280',
                      margin: '0 0 12px',
                      lineHeight: 1.5,
                      minHeight: 40,
                    }}
                  >
                    {assistant.desc}
                  </p>

                  {/* 专长标签 */}
                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: 6,
                      marginBottom: 14,
                    }}
                  >
                    {assistant.specialty.map((s, i) => (
                      <Tag
                        key={i}
                        style={{
                          borderRadius: 8,
                          fontSize: 11,
                          padding: '2px 8px',
                          margin: 0,
                          border: `1px solid ${assistant.color}30`,
                          color: assistant.color,
                          background: `${assistant.color}08`,
                          transition: 'all 0.2s ease',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'scale(1.1)'
                          e.currentTarget.style.background = `${assistant.color}15`
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'scale(1)'
                          e.currentTarget.style.background = `${assistant.color}08`
                        }}
                      >
                        {s}
                      </Tag>
                    ))}
                  </div>

                  {/* 开始对话按钮 */}
                  <Button
                    type="primary"
                    block
                    onClick={() => navigate('/chat', { state: { assistantId: assistant.id, assistant: assistant.name, assistantEmoji: assistant.emoji } })}
                    style={{
                      borderRadius: 12,
                      height: 40,
                      fontWeight: 600,
                      background: assistant.gradient,
                      border: 'none',
                      boxShadow: `0 4px 12px ${assistant.color}30`,
                      transition: 'all 0.3s ease',
                      overflow: 'hidden',
                      position: 'relative',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = `0 6px 20px ${assistant.color}40`
                      e.currentTarget.style.transform = 'scale(1.02)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = `0 4px 12px ${assistant.color}30`
                      e.currentTarget.style.transform = 'scale(1)'
                    }}
                  >
                    开始对话
                  </Button>
                </div>
              </Card>
            </FloatingCard>
          </Col>
        ))}
      </Row>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(5deg); }
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }
      `}</style>
    </div>
  )
}

export default AICompanion