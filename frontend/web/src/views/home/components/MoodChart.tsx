import { Card } from 'antd'
import { Link } from 'react-router-dom'
import { useTheme } from '../../../hooks/useTheme'
import { getMoodColor } from '../../home/data/features'

interface MoodData {
  date: string
  mood_score?: number
  score?: number
}

interface Props {
  moodData: MoodData[]
}

export function MoodChart({ moodData }: Props) {
  const { themeColor, themeColors } = useTheme()

  if (!moodData || moodData.length === 0) return null

  const chartData = moodData.slice(-30)
  const avgScore = (moodData.reduce((s, i) => s + (i.mood_score || i.score || 3), 0) / moodData.length).toFixed(1)

  const points = chartData.map((item, i) => {
    const score = item.mood_score || item.score || 3
    return {
      x: (i / (chartData.length - 1)) * 100,
      y: 100 - (score / 5) * 80,
      score,
      day: new Date(item.date).getDate(),
    }
  })

  const areaPath = `M 0,100 ` + points.map((p, i) => `L ${p.x},${p.y}`).join(' ') + ` L 100,100 Z`
  const linePath = `M ` + points.map((p, i) => i === 0 ? `${p.x},${p.y}` : ` L ${p.x},${p.y}`).join('')

  return (
    <Card style={{ borderRadius: 20, overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }} bodyStyle={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 20 }}>✨</span> 情绪能量波浪
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: '#6b7280' }}>
            平均能量 · {avgScore} · {chartData.length}天
          </p>
        </div>
        <Link to="/diary/stats" style={{ fontSize: 13, color: themeColors[themeColor], fontWeight: 500 }}>
          详情 →
        </Link>
      </div>

      <div style={{ position: 'relative', height: 180 }}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
          <defs>
            <linearGradient id="waveGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={themeColors[themeColor]} stopOpacity="0.6" />
              <stop offset="100%" stopColor={themeColors[themeColor]} stopOpacity="0.1" />
            </linearGradient>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="0.3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <path d={areaPath} fill="url(#waveGrad)" />
          <path d={linePath} fill="none" stroke={themeColors[themeColor]} strokeWidth="0.6" strokeLinecap="round" filter="url(#glow)" />
          {points.filter((_, i) => i % 5 === 0).map((p) => (
            <circle key={p.x} cx={p.x} cy={p.y} r={p.score >= 4 ? 1.8 : p.score >= 3 ? 1.4 : 1} fill={getMoodColor(p.score)} stroke="#fff" strokeWidth="0.25" />
          ))}
          {points.filter((_, i) => i % 5 === 0).map((p) => (
            <text key={`t${p.x}`} x={p.x} y="94" textAnchor="middle" fill="#9ca3af" fontSize="2.5">{p.day}日</text>
          ))}
        </svg>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: 28, marginTop: 16, paddingTop: 12, borderTop: '1px dashed #e5e7eb' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 16 }}>😄</span>
          <span style={{ fontSize: 11, color: '#10b981' }}>高涨</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 16 }}>😐</span>
          <span style={{ fontSize: 11, color: '#f59e0b' }}>平稳</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 16 }}>😔</span>
          <span style={{ fontSize: 11, color: '#ef4444' }}>低落</span>
        </div>
      </div>
    </Card>
  )
}

export default MoodChart