import { Card } from 'antd'
import { useTheme } from '../../../hooks/useTheme'

interface MoodData {
  date: string
  mood_score?: number
  score?: number
}

interface UserAssessment {
  mbti_type?: string
  type?: string
  personality?: string
}

interface DiaryStats {
  total_diaries?: number
  total_words?: number
  streak_days?: number
  avg_mood_score?: number
  most_common_emotion?: string
  top_themes?: string[]
  first_diary_date?: string
  recent_diary_date?: string
}

interface CheckinRecord {
  id: number
  checkin_date: string
  note?: string
}

interface Milestone {
  id: string
  date: string
  title: string
  desc: string
  story?: string
  icon: string
  isActive?: boolean
}

interface Props {
  moodData?: MoodData[]
  mbtiResult?: UserAssessment | null
  diaryStats?: DiaryStats | null
  checkinRecords?: CheckinRecord[]
}

// 基于用户数据生成里程碑
function generateMilestones(mbtiResult: UserAssessment | null, diaryStats: DiaryStats | null, checkinRecords: CheckinRecord[]): { milestones: Milestone[], latestStory: string } {
  const milestones: Milestone[] = []
  let latestStory = '记录你的每一次成长，见证心灵的每一次蜕变。'

  // 1. 首次使用（MBTI测评）
  if (mbtiResult?.mbti_type) {
    milestones.push({
      id: 'mbti_start',
      date: '开始',
      title: '开启测评',
      desc: `完成${mbtiResult.mbti_type}人格测评`,
      icon: '🌱',
    })
    latestStory = `完成${mbtiResult.mbti_type}人格测评，开启自我探索之旅。`
  }

  // 2. 第一次写日记
  if (diaryStats?.first_diary_date) {
    const firstDate = new Date(diaryStats.first_diary_date)
    const dateStr = `${firstDate.getMonth() + 1}月${firstDate.getDate()}日`
    milestones.push({
      id: 'first_diary',
      date: diaryStats.first_diary_date,
      title: '第一次倾诉',
      desc: `${dateStr} 写下第一篇日记`,
      icon: '💫',
    })
    latestStory = `${dateStr}，你第一次勇敢地敞开心扉。那天的文字充满勇气，是你心灵成长的起点。`
  }

  // 3. 连续记录里程碑
  if (diaryStats?.streak_days && diaryStats.streak_days >= 3) {
    milestones.push({
      id: 'streak',
      date: '坚持',
      title: '连续记录',
      desc: `连续${diaryStats.streak_days}天写日记`,
      icon: '🔥',
    })
    latestStory = `你已连续记录 ${diaryStats.streak_days} 天！每一次坚持都在累积成更好的自己。`
  }

  // 4. 写作成就
  if (diaryStats?.total_diaries && diaryStats.total_diaries >= 5) {
    milestones.push({
      id: 'diary_count',
      date: '成就',
      title: '写作达人',
      desc: `已写${diaryStats.total_diaries}篇日记`,
      icon: '📖',
    })
  }

  // 5. 打卡记录
  if (checkinRecords && checkinRecords.length > 0) {
    const lastCheckin = checkinRecords[0]
    if (lastCheckin) {
      const lastDate = new Date(lastCheckin.checkin_date)
      const today = new Date()
      const isToday = lastDate.toDateString() === today.toDateString()

      milestones.push({
        id: 'checkin',
        date: lastCheckin.checkin_date,
        title: isToday ? '今日打卡' : '最近打卡',
        desc: isToday ? '今天已完成打卡' : `上次打卡${lastDate.getMonth() + 1}/${lastDate.getDate()}`,
        icon: '✅',
      })
    }
  }

  // 添加"现在"节点
  milestones.push({
    id: 'now',
    date: 'now',
    title: '现在',
    desc: '你已经走了这么远',
    icon: '✨',
    isActive: true,
  })

  return { milestones, latestStory }
}

export function GrowthMilestone({
  mbtiResult = null,
  diaryStats = null,
  checkinRecords = [],
}: Props) {
  const { themeColor, themeColors } = useTheme()

  const { milestones, latestStory } = generateMilestones(mbtiResult, diaryStats, checkinRecords)

  // 计算进度条宽度（基于完成的里程碑）
  const completedCount = milestones.filter(m => !m.isActive && m.id !== 'now').length
  const progressWidth = Math.min((completedCount / Math.max(milestones.length - 2, 1)) * 70 + 10, 80)

  return (
    <Card
      style={{
        borderRadius: 24,
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
        marginBottom: 32,
      }}
      bodyStyle={{ padding: 24 }}
    >
      {/* 标题 */}
      <div style={{ marginBottom: 32 }}>
        <h3
          style={{
            fontSize: 20,
            fontWeight: 700,
            margin: 0,
            color: '#1f2937',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span style={{ fontSize: 22 }}>🎯</span> 你的成长里程碑
        </h3>
        <p
          style={{
            fontSize: 13,
            color: '#9ca3af',
            margin: '4px 0 0',
          }}
        >
          每一个足迹，都是你成长的证明
        </p>
      </div>

      {/* 时间轴 */}
      <div style={{ position: 'relative', marginBottom: 32 }}>
        {/* 连接线背景 */}
        <div
          style={{
            position: 'absolute',
            top: 24,
            left: '12%',
            right: '12%',
            height: 4,
            background: 'linear-gradient(90deg, #e5e7eb 0%, #d1d5db 50%, #e5e7eb 100%)',
            borderRadius: 2,
          }}
        />

        {/* 渐变覆盖层 */}
        <div
          style={{
            position: 'absolute',
            top: 24,
            left: '12%',
            width: `${progressWidth}%`,
            height: 4,
            background: `linear-gradient(90deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}80 100%)`,
            borderRadius: 2,
            transition: 'width 1s ease-out',
          }}
        />

        {/* 节点 */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            position: 'relative',
          }}
        >
          {milestones.map((m, i) => (
            <div
              key={m.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                width: '22%',
              }}
            >
              {/* 节点图标 */}
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  background: m.isActive ? themeColors[themeColor] : '#ffffff',
                  border: `3px solid ${m.isActive ? themeColors[themeColor] : '#d1d5db'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 22,
                  marginBottom: 12,
                  boxShadow: m.isActive
                    ? `0 0 20px ${themeColors[themeColor]}40`
                    : '0 2px 8px rgba(0,0,0,0.08)',
                  transition: 'all 0.3s ease',
                  animation: m.isActive ? 'glow 2s ease-in-out infinite' : 'none',
                }}
              >
                {m.icon}
              </div>

              {/* 文字 */}
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: 14,
                    fontWeight: 600,
                    color: m.isActive ? themeColors[themeColor] : '#374151',
                    marginBottom: 2,
                  }}
                >
                  {m.title}
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: '#9ca3af',
                    lineHeight: 1.4,
                  }}
                >
                  {m.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 最新故事卡片 */}
      <div
        style={{
          padding: 20,
          background: `linear-gradient(135deg, ${themeColors[themeColor]}08 0%, ${themeColors[themeColor]}05 100%)`,
          borderRadius: 16,
          border: `1px solid ${themeColors[themeColor]}20`,
          animation: 'fadeIn 0.5s ease-out',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
          }}
        >
          <span style={{ fontSize: 24 }}>💬</span>
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: '#374151',
                marginBottom: 6,
              }}
            >
              里程碑故事
            </div>
            <p
              style={{
                fontSize: 14,
                fontStyle: 'italic',
                color: '#6b7280',
                margin: 0,
                lineHeight: 1.7,
              }}
            >
              "{latestStory}"
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 20px ${themeColors[themeColor]}40; }
          50% { box-shadow: 0 0 30px ${themeColors[themeColor]}60; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </Card>
  )
}

export default GrowthMilestone