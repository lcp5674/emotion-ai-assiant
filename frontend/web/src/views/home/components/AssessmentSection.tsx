import { Card, Row, Col } from 'antd'
import { Link } from 'react-router-dom'
import { useTheme } from '../../../hooks/useTheme'
import { quickAssessments } from '../../home/data/features'

interface Props {
  mbtiResult?: { mbti_type?: string } | null
}

export function AssessmentSection({ mbtiResult }: Props) {
  const { themeColor, themeColors } = useTheme()

  return (
    <div className="container" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <h2 style={{ fontSize: 'clamp(28px, 4vw, 36px)', fontWeight: 700, marginBottom: 16, color: '#1f2937' }}>
          {mbtiResult ? '🌟 专属内容推荐' : '🔮 三大测评入口'}
        </h2>
        <p style={{ fontSize: 18, color: '#6b7280', maxWidth: 600, margin: '0 auto' }}>
          {mbtiResult
            ? `基于你的${mbtiResult.mbti_type}人格特质，为你推荐最合适的成长内容`
            : '从MBTI人格、SBTI恋爱风格、依恋类型三个维度\n全面解析你的性格特点'}
        </p>
      </div>

      <Row gutter={[24, 24]} justify="center">
        {quickAssessments.map((item, index) => (
          <Col xs={24} sm={12} lg={7} key={index}>
            <Link to={item.path} style={{ textDecoration: 'none' }}>
              <Card
                hoverable
                style={{
                  borderRadius: 24,
                  border: 'none',
                  boxShadow: `0 8px 24px ${item.gradient[0]}20`,
                  background: `linear-gradient(135deg, ${item.gradient[0]} 0%, ${item.gradient[1]} 100%)`,
                  overflow: 'hidden',
                }}
                bodyStyle={{ padding: 0 }}
              >
                <div style={{
                  position: 'absolute',
                  top: '-30%',
                  right: '-20%',
                  width: '60%',
                  height: '150%',
                  background: 'radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%)',
                }} />
                <div style={{ textAlign: 'center', color: '#fff', padding: '40px 24px 32px', position: 'relative' }}>
                  <div style={{
                    width: 72,
                    height: 72,
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    fontSize: 36,
                  }}>
                    {item.icon}
                  </div>
                  <h3 style={{ margin: '0 0 8px', fontSize: 20, fontWeight: 600 }}>{item.title}</h3>
                  <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>{item.desc}</p>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>
    </div>
  )
}

export default AssessmentSection