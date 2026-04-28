import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface MoodRecord {
  id: number
  mood_score: number
  mood_level?: string
  emotion?: string
  note?: string
  location?: string
  activity?: string
  created_at: string
}

interface DiaryTag {
  id: number
  name: string
  color?: string
  use_count: number
  created_at: string
}

interface DiarySummary {
  id: number
  date: string
  mood_score: number
  mood_level?: string
  primary_emotion?: string
  secondary_emotions?: string[]
  summary?: string
  tags?: string
  category?: string
  created_at: string
  updated_at: string
}

interface DiaryDetail extends DiarySummary {
  content?: string
  ai_analysis?: string
  ai_suggestion?: string
  analysis_status: string
  is_shared: boolean
  share_public: boolean
}

interface DiaryStats {
  total_count: number
  current_streak: number
  max_streak: number
  avg_mood: number
  most_common_emotion?: string
  avg_words_per_day: number
  categories: Record<string, number>
  this_month_count: number
  last_month_count: number
  period_count: number
}

interface MoodTrendPoint {
  date: string
  mood_score: number
  mood_level?: string
  primary_emotion?: string
  count: number
}

interface MoodTrend {
  time_range: string
  start_date: string
  end_date: string
  avg_score: number
  trend_data: MoodTrendPoint[]
  emotion_distribution: Record<string, number>
  mood_distribution: Record<string, number>
}

interface DiaryState {
  // 日记相关
  diaries: DiarySummary[]
  currentDiary: DiaryDetail | null
  totalCount: number
  currentPage: number
  pageSize: number
  loading: boolean

  // 心情记录
  moodRecords: MoodRecord[]

  // 标签
  tags: DiaryTag[]

  // 统计
  stats: DiaryStats | null
  trend: MoodTrend | null

  // 配置
  emotionConfig: any[]
  moodConfig: any[]

  // 操作方法
  setDiaries: (diaries: DiarySummary[]) => void
  setCurrentDiary: (diary: DiaryDetail | null | ((prev: DiaryDetail | null) => DiaryDetail | null)) => void
  setTotalCount: (count: number) => void
  setCurrentPage: (page: number) => void
  setPageSize: (size: number) => void
  setLoading: (loading: boolean) => void

  setMoodRecords: (records: MoodRecord[]) => void
  addMoodRecord: (record: MoodRecord) => void

  setTags: (tags: DiaryTag[]) => void
  addTag: (tag: DiaryTag) => void
  updateTag: (id: number, updates: Partial<DiaryTag>) => void
  deleteTag: (id: number) => void

  setStats: (stats: DiaryStats | null) => void
  setTrend: (trend: MoodTrend | null) => void

  setEmotionConfig: (config: any[]) => void
  setMoodConfig: (config: any[]) => void

  // 辅助方法
  reset: () => void
}

export const useDiaryStore = create<DiaryState>()(
  persist(
    (set) => ({
      diaries: [],
      currentDiary: null,
      totalCount: 0,
      currentPage: 1,
      pageSize: 10,
      loading: false,

      moodRecords: [],
      tags: [],
      stats: null,
      trend: null,
      emotionConfig: [],
      moodConfig: [],

      setDiaries: (diaries) => set({ diaries }),
      setCurrentDiary: (diary) => set((state) => ({
        currentDiary: typeof diary === 'function' ? diary(state.currentDiary) : diary,
      })),
      setTotalCount: (count) => set({ totalCount: count }),
      setCurrentPage: (page) => set({ currentPage: page }),
      setPageSize: (size) => set({ pageSize: size }),
      setLoading: (loading) => set({ loading }),

      setMoodRecords: (records) => set({ moodRecords: records }),
      addMoodRecord: (record) => set((state) => ({
        moodRecords: [record, ...state.moodRecords],
      })),

      setTags: (tags) => set({ tags }),
      addTag: (tag) => set((state) => ({ tags: [...state.tags, tag] })),
      updateTag: (id, updates) => set((state) => ({
        tags: state.tags.map((tag) =>
          tag.id === id ? { ...tag, ...updates } : tag
        ),
      })),
      deleteTag: (id) => set((state) => ({
        tags: state.tags.filter((tag) => tag.id !== id),
      })),

      setStats: (stats) => set({ stats }),
      setTrend: (trend) => set({ trend }),
      setEmotionConfig: (config) => set({ emotionConfig: config }),
      setMoodConfig: (config) => set({ moodConfig: config }),

      reset: () => set({
        diaries: [],
        currentDiary: null,
        totalCount: 0,
        currentPage: 1,
        pageSize: 10,
        loading: false,
        moodRecords: [],
        tags: [],
        stats: null,
        trend: null,
      }),
    }),
    {
      name: 'diary-storage',
      partialize: (state) => ({
        diaries: state.diaries,
        tags: state.tags,
        emotionConfig: state.emotionConfig,
        moodConfig: state.moodConfig,
      }),
    }
  )
)
