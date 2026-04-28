import { useAuthStore } from '../../../stores'
import { useTheme } from '../../../hooks/useTheme'
import { useEffect, useState } from 'react'

// MBTI类型对应的语录库
const mbtiQuotes: Record<string, string[]> = {
  INTJ: [
    '不要害怕内向，那是深度思考的礼物。',
    '你的孤独不是缺陷，而是洞察力的源泉。',
    '累了就休息，战略家也需要停机时间。',
    '独处是你最强大的武器，不要浪费它。',
  ],
  INTP: [
    '保持好奇心，是智者的本能。',
    '你的脑袋里藏着整个宇宙，值得被探索。',
    '不要急于给出答案，问题本身就很美。',
    '逻辑是工具，创意是目的。',
  ],
  ENTJ: [
    '你的野心不是傲慢，是改变世界的燃料。',
    '果断不是鲁莽，是看清后的选择。',
    '领导力不是控制，是赋能。',
    '失败只是通往成功的必经之路。',
  ],
  ENTP: [
    '你的点子价值连城，记得把它们写下来。',
    '争论是思想的碰撞，不是敌意。',
    '可能性永远比障碍多。',
    '创新者的道路是孤独的，但也是精彩的。',
  ],
  INFJ: [
    '你的同理心是这个世界的光。',
    '倾听他人很重要，但也要倾听自己。',
    '你比你想象的更有影响力。',
    '梦想家也能成为现实的建设者。',
  ],
  INFP: [
    '你的敏感不是软弱，是天赋。',
    '理想主义不是天真，是坚持。',
    '给自己许可去犯错、去成长。',
    '你的文字有治愈的力量。',
  ],
  ENFJ: [
    '你的热情正在感染身边的每一个人。',
    '帮助他人的同时，也要照顾好自己。',
    '今天试试把灵感变成行动，你会惊讶于自己的潜力。',
    '领袖不是站在前面，而是站在旁边。',
  ],
  ENFP: [
    '你的笑容能点亮整个房间。',
    '保持那份对世界的好奇和热爱。',
    '今天有无限可能，尽情探索吧。',
    '你的能量值得被最好的事情点燃。',
  ],
  ISTJ: [
    '责任感到很强，这是你的超能力。',
    '稳定是基石，但也要给自己留些弹性。',
    '你的可靠是这个社会的锚点。',
    '记得偶尔停下来欣赏一下自己的成就。',
  ],
  ISFJ: [
    '你的细心和温暖正在治愈周围的人。',
    '照顾他人之前，先照顾好自己。',
    '你的付出不会被遗忘。',
    '安静的守护者同样值得被守护。',
  ],
  ESTJ: [
    '你的执行力是改变的推动力。',
    '高效很好，但不要忘了享受过程。',
    '你是他人的依靠，谁来支撑你？',
    '秩序带来自由，而不是限制。',
  ],
  ESFJ: [
    '你的关怀是人际关系的粘合剂。',
    '给予温暖的同时，也要学会说不。',
    '你值得被珍惜，不只是付出。',
    '照顾好他人之前，先照顾好自己。',
  ],
  ISTP: [
    '你解决问题的直觉非常精准。',
    '动手实践是最好的学习方式。',
    '给自己空间去探索和实验。',
    '沉默不是冷漠，是专注。',
  ],
  ISFP: [
    '你的艺术感是你灵魂的表达。',
    '活在当下，享受这一刻的美好。',
    '你的敏感让你看到别人看不到的美。',
    '不要压抑自己的情感，它们是你的一部分。',
  ],
  ESTP: [
    '你的行动力是梦想的翅膀。',
    '活在当下，尽情体验生活的精彩。',
    '冒险精神让你的人生丰富多彩。',
    '冲劲十足，但也别忘了偶尔暂停。',
  ],
  ESFP: [
    '你是派对的灵魂人物，也是真诚的朋友。',
    '你的热情有感染力，能带动周围的人。',
    '尽情闪耀吧，这是你的天赋。',
    '在热闹之余，也给自己一些安静的时间。',
  ],
}

// 默认语录（用于未知类型或未登录用户）
const defaultQuotes = [
  '每个人都是独一无二的，值得被理解。',
  '今天的不顺利，会变成明天的故事。',
  '给自己一个微笑，你值得。',
  '情绪是信使，倾听它们有话说。',
]

// 淡入动画组件
function FadeIn({ children, delay = 0, direction = 'up' }: { children: React.ReactNode; delay?: number; direction?: 'up' | 'down' | 'left' | 'right' }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  const getTransform = () => {
    switch (direction) {
      case 'up': return 'translateY(20px)'
      case 'down': return 'translateY(-20px)'
      case 'left': return 'translateX(20px)'
      case 'right': return 'translateX(-20px)'
      default: return 'translateY(20px)'
    }
  }

  return (
    <div
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translate(0, 0) scale(1)' : getTransform(),
        transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {children}
    </div>
  )
}

export function DailyQuote() {
  const { user } = useAuthStore()
  const { themeColor, themeColors } = useTheme()

  const mbtiType = user?.mbti_type || ''
  const quotes = mbtiType ? (mbtiQuotes[mbtiType] || defaultQuotes) : defaultQuotes
  const dayOfYear = Math.floor(
    (Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000
  )
  const todayQuote = quotes[dayOfYear % quotes.length]

  return (
    <div
      style={{
        position: 'relative',
        borderRadius: 24,
        padding: 32,
        marginBottom: 32,
        overflow: 'hidden',
        background: `linear-gradient(135deg, #fef3f2 0%, #fdf2f8 50%, #f5f3ff 100%)`,
        boxShadow: '0 4px 24px rgba(114, 46, 209, 0.08)',
        animation: 'fadeIn 1s ease-out',
      }}
    >
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(3deg); }
        }
        @keyframes sparkle {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.5); }
        }
        @keyframes rotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>

      {/* 装饰元素 */}
      <div
        style={{
          position: 'absolute',
          top: -30,
          right: -30,
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${themeColors[themeColor]}15 0%, transparent 70%)`,
          pointerEvents: 'none',
          animation: 'float 6s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: -20,
          left: -20,
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: `radial-gradient(circle, #f472b615 0%, transparent 70%)`,
          pointerEvents: 'none',
          animation: 'float 8s ease-in-out infinite reverse',
        }}
      />
      {/* 闪烁的星星装饰 */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          left: '10%',
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: themeColors[themeColor],
          animation: 'sparkle 2s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: '25%',
          right: '20%',
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: '#f472b6',
          animation: 'sparkle 3s ease-in-out infinite reverse',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          right: '15%',
          width: 5,
          height: 5,
          borderRadius: '50%',
          background: '#722ed1',
          animation: 'sparkle 2.5s ease-in-out infinite',
          animationDelay: '0.5s',
        }}
      />

      {/* 内容 */}
      <div style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
        <FadeIn delay={200}>
          <div
            style={{
              fontSize: 32,
              marginBottom: 16,
              animation: 'float 4s ease-in-out infinite',
              display: 'inline-block',
            }}
          >
            🌟
          </div>
        </FadeIn>

        <FadeIn delay={400}>
          <p
            style={{
              fontSize: 18,
              fontStyle: 'italic',
              color: '#374151',
              margin: 0,
              lineHeight: 1.8,
              maxWidth: 500,
              marginLeft: 'auto',
              marginRight: 'auto',
            }}
          >
            "{todayQuote}"
          </p>
        </FadeIn>

        <FadeIn delay={600}>
          <p
            style={{
              margin: '20px 0 0',
              fontSize: 14,
              fontWeight: 600,
              color: themeColors[themeColor],
            }}
          >
            {mbtiType ? `—— 致 ${mbtiType}` : '—— 每日语录'}
          </p>
        </FadeIn>
      </div>
    </div>
  )
}

export default DailyQuote