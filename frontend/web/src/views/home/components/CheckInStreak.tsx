import { Card, Progress, Tag } from 'antd'
import { Link } from 'react-router-dom'
import { useTheme } from '../../../hooks/useTheme'
import { useEffect, useState } from 'react'

interface Props {
  streak?: number
  level?: number
  levelName?: string
  nextMilestone?: number
  nextReward?: string
}

const defaultStreak = 12
const defaultLevel = 8
const defaultLevelName = '8级探索者'
const defaultNextMilestone = 14
const defaultNextReward = '「深夜倾诉者」成就'

// 动画数字组件
function AnimatedNumber({ value, duration = 1000 }: { value: number; duration?: number }) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    let startTime: number
    let animationFrame: number

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      const easeProgress = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      setDisplayValue(Math.round(easeProgress * value))

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])

  return <span>{displayValue}</span>
}

export function CheckInStreak({
  streak = defaultStreak,
  level = defaultLevel,
  levelName = defaultLevelName,
  nextMilestone = defaultNextMilestone,
  nextReward = defaultNextReward,
}: Props) {
  const { themeColor, themeColors } = useTheme()
  const progress = Math.min((streak / nextMilestone) * 100, 100)
  const remaining = Math.max(nextMilestone - streak, 0)

  return (
    <Card
      style={{
        borderRadius: 24,
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
        marginBottom: 32,
        background:
          streak > 0
            ? 'linear-gradient(135deg, #fef3f2 0%, #fff7f0 100%)'
            : 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
        border: 'none',
        animation: 'slideUp 0.6s ease-out',
      }}
      bodyStyle={{ padding: 24 }}
    >
      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>

      {/* 头部 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 20,
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        <div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              marginBottom: 4,
            }}
          >
            <span
              style={{
                fontSize: 28,
                animation: streak > 0 ? 'pulse 2s ease-in-out infinite' : 'none',
              }}
            >
              🔥
            </span>
            <span
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: '#1f2937',
              }}
            >
              连续打卡{' '}
              <span
                style={{
                  color: themeColors[themeColor],
                  fontSize: 28,
                  display: 'inline-block',
                }}
              >
                <AnimatedNumber value={streak} duration={1200} />
              </span>{' '}
              天
            </span>
          </div>
          <p
            style={{
              fontSize: 14,
              color: '#6b7280',
              margin: 0,
            }}
          >
            再连续{remaining}天，解锁{nextReward}
          </p>
        </div>

        <Tag
          style={{
            borderRadius: 20,
            padding: '6px 16px',
            fontSize: 14,
            fontWeight: 600,
            background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}cc 100%)`,
            color: '#ffffff',
            border: 'none',
            boxShadow: `0 4px 12px ${themeColors[themeColor]}30`,
            backgroundSize: '200% 100%',
            animation: 'shimmer 3s ease-in-out infinite',
          }}
        >
          🌟 {levelName}
        </Tag>
      </div>

      {/* 进度条 */}
      <div style={{ marginBottom: 16 }}>
        <Progress
          percent={progress}
          showInfo={false}
          strokeColor={{
            '0%': themeColors[themeColor],
            '100%': `${themeColors[themeColor]}80`,
          }}
          trailColor="#f0f0f0"
          strokeWidth={12}
          success={{ percent: 0 }}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: 8,
            fontSize: 13,
            color: '#9ca3af',
          }}
        >
          <span>第{streak}天</span>
          <span style={{ fontWeight: 600, color: '#6b7280' }}>
            目标: {nextMilestone}天
          </span>
        </div>
      </div>

      {/* 提示信息 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 16px',
          background: '#ffffff',
          borderRadius: 14,
          marginTop: 16,
          transition: 'all 0.3s ease',
          cursor: 'pointer',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateX(4px)'
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateX(0)'
          e.currentTarget.style.boxShadow = 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 20 }}>🎁</span>
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: '#374151',
              }}
            >
              里程碑奖励
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#9ca3af',
              }}
            >
              连续{nextMilestone}天即可解锁
            </div>
          </div>
        </div>
        <Link
          to="/achievements"
          style={{
            fontSize: 13,
            fontWeight: 600,
            color: themeColors[themeColor],
            textDecoration: 'none',
          }}
        >
          查看全部 →
        </Link>
      </div>
    </Card>
  )
}

export default CheckInStreak