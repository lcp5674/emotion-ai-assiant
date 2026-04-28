import { useState, useEffect, useCallback } from 'react'
import { api } from '../../../api/request'
import { useAuthStore } from '../../../stores'

interface MoodData {
  date: string
  mood_score?: number
  score?: number
}

interface UserAssessment {
  mbti_type?: string
  type?: string
  personality?: string
  dimensions?: Array<{ value: string }>
  selected_theme?: string
  top_theme_1?: string
  theme?: string
}

interface DiaryStats {
  total_diaries?: number
  total_words?: number
  streak_days?: number
  current_streak?: number
  max_streak?: number
  avg_mood_score?: number
  avg_mood?: number
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

interface CheckinStats {
  current_streak?: number
  max_streak?: number
  total_checkins?: number
}

interface UseHomeUserDataReturn {
  moodData: MoodData[]
  mbtiResult: UserAssessment | null
  sbtiResult: UserAssessment | null
  attachmentResult: UserAssessment | null
  diaryStats: DiaryStats | null
  checkinRecords: CheckinRecord[]
  checkinStats: CheckinStats | null
  loading: boolean
  timeRange: string
  refreshMoodData: (timeRange: string) => void
}

export function useHomeUserData(): UseHomeUserDataReturn {
  const { isAuthenticated, isHydrated } = useAuthStore()
  const [moodData, setMoodData] = useState<MoodData[]>([])
  const [mbtiResult, setMbtiResult] = useState<UserAssessment | null>(null)
  const [sbtiResult, setSbtiResult] = useState<UserAssessment | null>(null)
  const [attachmentResult, setAttachmentResult] = useState<UserAssessment | null>(null)
  const [diaryStats, setDiaryStats] = useState<DiaryStats | null>(null)
  const [checkinRecords, setCheckinRecords] = useState<CheckinRecord[]>([])
  const [checkinStats, setCheckinStats] = useState<CheckinStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('month')

  const loadMoodData = useCallback(async (range: string) => {
    try {
      const moodRes = await api.diary.trend(range)
      if (moodRes?.trend_data) {
        setMoodData(moodRes.trend_data)
      }
    } catch (e) {
      console.error('Failed to load mood data:', e)
    }
  }, [])

  const load = useCallback(async (range: string) => {
    try {
      const [mbtiRes, sbtiRes, attachRes, statsRes, checkinRes, checkinStatsRes] = await Promise.allSettled([
        api.mbti.result(),
        api.sbti.result(),
        api.attachment.result(),
        api.diary.stats(range),
        api.checkin.records(30),
        api.checkin.stats(),
      ])

      if (mbtiRes.status === 'fulfilled' && mbtiRes.value) {
        setMbtiResult(mbtiRes.value)
      }
      if (sbtiRes.status === 'fulfilled' && sbtiRes.value) {
        setSbtiResult(sbtiRes.value)
      }
      if (attachRes.status === 'fulfilled' && attachRes.value) {
        setAttachmentResult(attachRes.value)
      }
      if (statsRes.status === 'fulfilled' && statsRes.value) {
        setDiaryStats(statsRes.value)
      }
      if (checkinRes.status === 'fulfilled' && checkinRes.value?.list) {
        setCheckinRecords(checkinRes.value.list)
      }
      if (checkinStatsRes.status === 'fulfilled' && checkinStatsRes.value) {
        setCheckinStats(checkinStatsRes.value)
      } else if (checkinStatsRes.status === 'rejected') {
        console.error('checkinStats fetch failed:', checkinStatsRes.reason)
      }
    } catch (e) {
      console.error('Failed to load user data:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // 只有在 hydration 完成且已认证时才加载数据
    if (!isHydrated || !isAuthenticated) {
      setLoading(false)
      return
    }

    // 同时加载心情数据和用户数据
    loadMoodData(timeRange)
    load(timeRange)
  }, [isAuthenticated, isHydrated, timeRange, loadMoodData, load])

  const refreshMoodData = useCallback((range: string) => {
    setTimeRange(range)
    loadMoodData(range)
  }, [loadMoodData])

  return { moodData, mbtiResult, sbtiResult, attachmentResult, diaryStats, checkinRecords, checkinStats, loading, timeRange, refreshMoodData }
}

export default useHomeUserData