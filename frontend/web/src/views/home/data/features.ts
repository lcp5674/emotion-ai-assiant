export const quickAssessments = [
  { icon: '🔮', title: 'MBTI人格', desc: '发现你的性格优势', path: '/mbti', gradient: ['#6366f1', '#a855f7'] as [string, string] },
  { icon: '💕', title: '恋爱风格', desc: '解读你的爱情模式', path: '/sbti', gradient: ['#f472b6', '#ec4899'] as [string, string] },
  { icon: '💝', title: '依恋风格', desc: '认识你的依恋模式', path: '/attachment', gradient: ['#34d399', '#14b8a6'] as [string, string] },
]

export const moodEmojis = ['', '😢', '😔', '😐', '😊', '😄']
export const moodColors = ['', '#ef4444', '#f97316', '#fbbf24', '#22c55e', '#10b981']

export const getMoodEmoji = (score: number) => moodEmojis[Math.min(Math.max(Math.round(score), 1), 5)]
export const getMoodColor = (score: number) => moodColors[Math.min(Math.max(Math.round(score), 1), 5)]