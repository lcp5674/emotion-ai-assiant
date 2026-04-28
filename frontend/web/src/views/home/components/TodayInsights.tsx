import { Card, Space } from 'antd'
import { useNavigate } from 'react-router-dom'
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

interface Insight {
  id: string
  type: 'pattern' | 'positive' | 'curiosity' | 'milestone'
  icon: string
  title: string
  desc: string
  aiDesc: string
  actionLabel: string
  actionPath: string
  bgColor: string
  borderColor: string
}

interface Props {
  moodData?: MoodData[]
  mbtiResult?: UserAssessment | null
  diaryStats?: DiaryStats | null
}

// 基于用户数据生成洞察
function generateInsights(moodData: MoodData[], mbtiResult: UserAssessment | null, diaryStats: DiaryStats | null): Insight[] {
  const insights: Insight[] = []

  // 1. 基于情绪数据分析洞察
  if (moodData && moodData.length > 0) {
    const recentMood = moodData.slice(-7)
    const avgScore = recentMood.reduce((sum, d) => sum + (d.mood_score || d.score || 3), 0) / recentMood.length

    if (avgScore >= 4) {
      insights.push({
        id: 'mood_up',
        type: 'positive',
        icon: '💜',
        title: '情绪提升',
        desc: `近期积极情绪较高，平均能量值 ${avgScore.toFixed(1)}/5`,
        aiDesc: '继续保持！你的心态正在发光，照亮自己也温暖他人 🌟',
        actionLabel: '写日记记录美好 →',
        actionPath: '/diary/create',
        bgColor: '#fdf2f8',
        borderColor: '#fce7f3',
      })
    } else if (avgScore <= 2) {
      insights.push({
        id: 'mood_low',
        type: 'curiosity',
        icon: '🌙',
        title: '情绪波动',
        desc: `近期情绪有些低落，平均能量值 ${avgScore.toFixed(1)}/5`,
        aiDesc: '情绪起伏是正常的，也许有些事情需要被看见和倾听。我在这里陪你。',
        actionLabel: '与AI聊聊 →',
        actionPath: '/chat',
        bgColor: '#f5f3ff',
        borderColor: '#ddd6fe',
      })
    }

    // 检测深夜记录模式
    const lateNightEntries = moodData.filter(d => {
      const hour = new Date(d.date).getHours()
      return hour >= 22 || hour <= 4
    })
    if (lateNightEntries.length >= 3) {
      insights.push({
        id: 'late_night',
        type: 'curiosity',
        icon: '🌙',
        title: '深夜时刻',
        desc: `你有 ${lateNightEntries.length} 次在深夜记录心情`,
        aiDesc: '深夜的你似乎有更多想说的话... 那些安静的夜晚，文字是你最好的倾听者。',
        actionLabel: '探索深夜心事 →',
        actionPath: '/diary/stats',
        bgColor: '#f5f3ff',
        borderColor: '#ddd6fe',
      })
    }
  }

  // 2. 基于日记统计生成洞察
  if (diaryStats) {
    if (diaryStats.streak_days && diaryStats.streak_days >= 7) {
      insights.push({
        id: 'streak',
        type: 'milestone',
        icon: '🔥',
        title: '连续记录',
        desc: `已连续记录 ${diaryStats.streak_days} 天`,
        aiDesc: '坚持的力量是巨大的！每一天的书写都在累积成更好的自己 💪',
        actionLabel: '查看打卡记录 →',
        actionPath: '/diary/stats',
        bgColor: '#fef7f0',
        borderColor: '#fed7aa',
      })
    }

    if (diaryStats.total_diaries && diaryStats.total_diaries >= 10) {
      insights.push({
        id: 'diary_count',
        type: 'milestone',
        icon: '📖',
        title: '写作达人',
        desc: `已写下 ${diaryStats.total_diaries} 篇日记，共 ${diaryStats.total_words?.toLocaleString() || 0} 字`,
        aiDesc: '文字是你心灵的地图，回头看看，每一笔都是成长的印记。',
        actionLabel: '回顾我的日记 →',
        actionPath: '/diary/list',
        bgColor: '#f0fdf4',
        borderColor: '#bbf7d0',
      })
    }

    if (diaryStats.top_themes && diaryStats.top_themes.length > 0) {
      insights.push({
        id: 'top_theme',
        type: 'pattern',
        icon: '🧡',
        title: '思考主题',
        desc: `你最近在思考"${diaryStats.top_themes[0]}"`,
        aiDesc: '这个主题似乎对你很重要。也许值得深入探索一下？',
        actionLabel: '倾听AI的分析 →',
        actionPath: '/chat',
        bgColor: '#fef7f0',
        borderColor: '#fed7aa',
      })
    }
  }

  // 3. 基于MBTI类型生成洞察
  if (mbtiResult?.mbti_type) {
    const mbtiType = mbtiResult.mbti_type
    const mbtiInsights: Record<string, { title: string; desc: string }> = {
      'INTJ': { title: '战略家特质', desc: '你倾向于深度思考，制定长期计划' },
      'INTP': { title: '探索者特质', desc: '你对知识和理解有强烈的渴望' },
      'ENTJ': { title: '领导者特质', desc: '你善于决策和组织，有很强的执行力' },
      'ENTP': { title: '创新者特质', desc: '你喜欢探索可能性，思维活跃' },
      'INFJ': { title: '理想主义者特质', desc: '你有深刻的洞察力，关注他人感受' },
      'INFP': { title: '调停者特质', desc: '你重视内心价值观，追求意义' },
      'ENFJ': { title: '倡导者特质', desc: '你善于激励他人，创造积极改变' },
      'ENFP': { title: '活动家特质', desc: '你对世界充满好奇，热爱探索' },
      'ISTJ': { title: '物流师特质', desc: '你脚踏实地，重视责任和承诺' },
      'ISFJ': { title: '守护者特质', desc: '你忠诚可靠，默默付出' },
      'ESTJ': { title: '总经理特质', desc: '你注重效率，善于管理' },
      'ESFJ': { title: '执政官特质', desc: '你热心友善，重视人际关系' },
      'ISTP': { title: '鉴赏家特质', desc: '你善于分析，动手能力强' },
      'ISFP': { title: '探险家特质', desc: '你有艺术气质，享受当下' },
      'ESTP': { title: '企业家特质', desc: '你充满活力，喜欢冒险' },
      'ESFP': { title: '表演者特质', desc: '你乐观开朗，享受生活' },
    }

    const mbtiInfo = mbtiInsights[mbtiType]
    if (mbtiInfo && insights.length < 3) {
      insights.push({
        id: 'mbti',
        type: 'pattern',
        icon: '💡',
        title: mbtiInfo.title,
        desc: mbtiInfo.desc,
        aiDesc: `了解自己的性格特点，可以帮助你更好地发挥优势。`,
        actionLabel: '探索更多 →',
        actionPath: '/mbti',
        bgColor: '#eff6ff',
        borderColor: '#bfdbfe',
      })
    }
  }

  // 如果没有足够的数据，返回默认提示
  if (insights.length === 0) {
    insights.push({
      id: 'welcome',
      type: 'positive',
      icon: '🌟',
      title: '欢迎开始记录',
      desc: '开始写日记，开启你的情绪追踪之旅',
      aiDesc: '每一次记录都是对自己的关爱。从今天开始，记录你的心情吧！',
      actionLabel: '写第一篇日记 →',
      actionPath: '/diary/create',
      bgColor: '#fdf2f8',
      borderColor: '#fce7f3',
    })
  }

  return insights.slice(0, 3) // 最多返回3个洞察
}

export function TodayInsights({ moodData = [], mbtiResult = null, diaryStats = null }: Props) {
  const navigate = useNavigate()
  const { themeColor, themeColors } = useTheme()

  const insights = generateInsights(moodData, mbtiResult, diaryStats)

  return (
    <div style={{ marginBottom: 32 }}>
      {/* 标题区 */}
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
          <span>✨</span> 今日专属发现
        </h2>
        <p
          style={{
            fontSize: 14,
            color: '#9ca3af',
            margin: '8px 0 0',
          }}
        >
          基于你近期的记录，为你准备的个性化洞察
        </p>
      </div>

      {/* 洞察卡片列表 */}
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        {insights.map((insight) => (
          <Card
            key={insight.id}
            size="small"
            style={{
              borderRadius: 20,
              background: insight.bgColor,
              border: `1px solid ${insight.borderColor}`,
              boxShadow: 'none',
              overflow: 'hidden',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
            }}
            bodyStyle={{ padding: 0 }}
            onClick={() => navigate(insight.actionPath)}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = `0 8px 24px ${insight.borderColor}40`
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div
              style={{
                padding: 20,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  gap: 16,
                  alignItems: 'flex-start',
                }}
              >
                {/* 图标 */}
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 14,
                    background: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 24,
                    flexShrink: 0,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                    animation: 'pulse 2s ease-in-out infinite',
                  }}
                >
                  {insight.icon}
                </div>

                {/* 内容 */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h4
                    style={{
                      fontSize: 15,
                      fontWeight: 600,
                      margin: '0 0 4px',
                      color: '#1f2937',
                    }}
                  >
                    {insight.desc}
                  </h4>
                  <p
                    style={{
                      fontSize: 13,
                      color: '#6b7280',
                      margin: '0 0 12px',
                      lineHeight: 1.6,
                    }}
                  >
                    {insight.aiDesc}
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(insight.actionPath)
                    }}
                    style={{
                      padding: '6px 14px',
                      background: '#ffffff',
                      border: 'none',
                      borderRadius: 10,
                      fontSize: 13,
                      fontWeight: 500,
                      color: themeColors[themeColor],
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(114, 46, 209, 0.15)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)'
                    }}
                  >
                    {insight.actionLabel}
                  </button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </Space>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </div>
  )
}

export default TodayInsights