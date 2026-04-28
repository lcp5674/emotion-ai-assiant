import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../../stores'
import { useTheme } from '../../../hooks/useTheme'
import { useEffect, useState } from 'react'

// 根据时间段获取问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return { time: 'morning', icon: '🌅', text: '早安' }
  if (hour >= 12 && hour < 18) return { time: 'afternoon', icon: '☀️', text: '下午好' }
  if (hour >= 18 && hour < 23) return { time: 'evening', icon: '🌙', text: '晚上好' }
  return { time: 'lateNight', icon: '🌌', text: '夜深了' }
}

// 每日语录库
const dailyQuotes = [
  '今晚的月色很美，适合静心思考。',
  '有时候，停下脚步才是最快的成长。',
  '你今天经历了什么？这里愿意倾听。',
  '情绪没有对错，它们都是你的信使。',
  '给自己一首歌的时间，暂停忙碌。',
  '今天的你，已经很努力了。',
]

const getDailyQuote = () => {
  const dayOfYear = Math.floor(
    (Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000
  )
  return dailyQuotes[dayOfYear % dailyQuotes.length]
}

// MBTI类型对应的描述
const mbtiDescriptions: Record<string, string> = {
  INTJ: '孤独的思考者',
  INTP: '深邃的探索家',
  ENTJ: '无畏的领导者',
  ENTP: '灵动的创新者',
  INFJ: '温暖的光行者',
  INFP: '理想主义的梦想家',
  ENFJ: '魅力的引导者',
  ENFP: '热情的探险家',
  ISTJ: '沉默的守护者',
  ISFJ: '温暖的陪伴者',
  ESTJ: '坚定的执行者',
  ESFJ: '热忱的关怀者',
  ISTP: '冷静的观察者',
  ISFP: '敏感的灵魂',
  ESTP: '活力的行动派',
  ESFP: '快乐的制造者',
}

// 动画文字组件
function AnimatedText({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <span
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(10px)',
        transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'inline-block',
      }}
    >
      {children}
    </span>
  )
}

export function HeroWelcome() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { themeColor, themeColors } = useTheme()

  const greeting = getGreeting()
  const mbtiType = user?.mbti_type || ''
  const mbtiDesc = mbtiType ? (mbtiDescriptions[mbtiType] || '独特的灵魂') : '独特的灵魂'
  const nickname = user?.nickname || '朋友'
  const dailyQuote = getDailyQuote()

  return (
    <div
      style={{
        position: 'relative',
        borderRadius: 28,
        padding: '48px 40px',
        marginBottom: 32,
        overflow: 'hidden',
        background: `linear-gradient(135deg, #fef3f2 0%, #fdf2f8 50%, #f5f3ff 100%)`,
        boxShadow: '0 8px 32px rgba(114, 46, 209, 0.08)',
        animation: 'fadeInUp 0.8s ease-out',
      }}
    >
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-15px) scale(1.05); }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>

      {/* 装饰性背景元素 */}
      <div
        style={{
          position: 'absolute',
          top: -60,
          right: -60,
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(114, 46, 209, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
          animation: 'float 6s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: -40,
          left: -40,
          width: 160,
          height: 160,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(244, 114, 182, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
          animation: 'float 8s ease-in-out infinite reverse',
        }}
      />
      {/* 额外的装饰星星 */}
      <div
        style={{
          position: 'absolute',
          top: '20%',
          right: '15%',
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: themeColors[themeColor],
          opacity: 0.6,
          animation: 'pulse 2s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '30%',
          right: '25%',
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: '#f472b6',
          opacity: 0.5,
          animation: 'pulse 3s ease-in-out infinite reverse',
        }}
      />

      {/* 主内容 */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* 问候语 */}
        <div style={{ marginBottom: 16 }}>
          <h1
            style={{
              fontSize: 'clamp(28px, 5vw, 36px)',
              fontWeight: 700,
              margin: 0,
              color: '#1f2937',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              flexWrap: 'wrap',
            }}
          >
            <AnimatedText delay={200}>
              <span
                style={{
                  fontSize: 36,
                  display: 'inline-block',
                  animation: 'float 4s ease-in-out infinite',
                }}
              >
                {greeting.icon}
              </span>
            </AnimatedText>
            <AnimatedText delay={400}>
              <span>
                {greeting.text}，<span style={{ color: themeColors[themeColor] }}>{mbtiType}</span>的
                <span style={{ color: themeColors[themeColor] }}>{mbtiDesc}</span>
              </span>
            </AnimatedText>
          </h1>
        </div>

        {/* 每日语录 */}
        <AnimatedText delay={600}>
          <p
            style={{
              fontSize: 18,
              fontStyle: 'italic',
              color: '#6b7280',
              margin: '0 0 32px',
              paddingLeft: 16,
              borderLeft: `3px solid ${themeColors[themeColor]}`,
              lineHeight: 1.8,
            }}
          >
            "{dailyQuote}"
          </p>
        </AnimatedText>

        {/* 三个行动按钮 */}
        <div
          style={{
            display: 'flex',
            gap: 16,
            flexWrap: 'wrap',
          }}
        >
          <AnimatedActionButton
            delay={800}
            icon="🌙"
            title="倾诉今夜"
            desc="聊聊此刻的心情"
            gradient="linear-gradient(135deg, #722ed1 0%, #b37feb 100%)"
            onClick={() => navigate('/chat')}
          />
          <AnimatedActionButton
            delay={1000}
            icon="🔮"
            title="探索今日"
            desc="今日专属发现"
            gradient="linear-gradient(135deg, #1890ff 0%, #69c0ff 100%)"
            onClick={() => navigate('/knowledge')}
          />
          <AnimatedActionButton
            delay={1200}
            icon="✍️"
            title="记录心情"
            desc="写下你的故事"
            gradient="linear-gradient(135deg, #f472b6 0%, #ec4899 100%)"
            onClick={() => navigate('/diary/create')}
          />
        </div>
      </div>
    </div>
  )
}

interface ActionButtonProps {
  icon: string
  title: string
  desc: string
  gradient: string
  onClick: () => void
  delay?: number
}

function AnimatedActionButton({ icon, title, desc, gradient, onClick, delay = 0 }: ActionButtonProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '16px 24px',
        background: gradient,
        border: 'none',
        borderRadius: 16,
        cursor: 'pointer',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
        minWidth: 180,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.95)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px) scale(1.02)'
        e.currentTarget.style.boxShadow = '0 12px 32px rgba(0,0,0,0.2)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0) scale(1)'
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)'
      }}
    >
      <span style={{ fontSize: 28, filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}>{icon}</span>
      <div style={{ textAlign: 'left' }}>
        <div
          style={{
            fontSize: 15,
            fontWeight: 600,
            color: '#ffffff',
            lineHeight: 1.3,
            textShadow: '0 1px 2px rgba(0,0,0,0.2)',
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontSize: 12,
            color: 'rgba(255,255,255,0.85)',
            lineHeight: 1.3,
            marginTop: 2,
          }}
        >
          {desc}
        </div>
      </div>
    </button>
  )
}

export default HeroWelcome