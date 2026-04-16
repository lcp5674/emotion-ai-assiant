import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, useEffect } from 'react'
import { Button, App as AntApp, Spin } from 'antd'
import { SunOutlined, MoonOutlined } from '@ant-design/icons'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ProtectedRoute } from './components/ProtectedRoute'
import { useTheme } from './hooks/useTheme'
import { useAuthStore } from './stores'
import { lazy } from 'react'
import { useNavigate } from 'react-router-dom'
import { setNavigate } from './api/request'

// 直接导入组件（避免复杂的路由配置）
const Home = lazy(() => import('./views/home'))
const Login = lazy(() => import('./views/login'))
const Register = lazy(() => import('./views/register'))
const MbtiTest = lazy(() => import('./views/mbti'))
const MbtiResult = lazy(() => import('./views/mbti/result'))
const Chat = lazy(() => import('./views/chat'))
const AssistantSquare = lazy(() => import('./views/assistant'))
const Profile = lazy(() => import('./views/profile'))
const Knowledge = lazy(() => import('./views/knowledge'))
const ArticleDetail = lazy(() => import('./views/knowledge/detail'))
const KnowledgeCollections = lazy(() => import('./views/knowledge/collections'))
const Admin = lazy(() => import('./views/admin'))
const DiaryList = lazy(() => import('./views/diary'))
const DiaryDetail = lazy(() => import('./views/diary/detail'))
const DiaryCreate = lazy(() => import('./views/diary/create'))
const DiaryStats = lazy(() => import('./views/diary/stats'))
const Onboarding = lazy(() => import('./views/onboarding'))
const PrivacyPage = lazy(() => import('./views/privacy'))
const CrisisPage = lazy(() => import('./views/crisis'))
const AchievementsPage = lazy(() => import('./views/achievements'))
const CheckInPage = lazy(() => import('./views/checkin'))
// SBTI
const SbtiIndex = lazy(() => import('./views/sbti'))
const SbtiTest = lazy(() => import('./views/sbti/test'))
const SbtiResult = lazy(() => import('./views/sbti/result'))
// 依恋风格
const AttachmentIndex = lazy(() => import('./views/attachment'))
const AttachmentTest = lazy(() => import('./views/attachment/test'))
const AttachmentResult = lazy(() => import('./views/attachment/result'))
// 深度画像
const DeepProfile = lazy(() => import('./views/profile/deep'))
// 三位一体综合测评
const ComprehensiveTest = lazy(() => import('./views/comprehensive'))
// 账户设置
const Settings = lazy(() => import('./views/settings'))

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
    </>
  )
}

function AppRoutes() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <Routes>
      {/* 公开路由 - 无需登录 */}
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <Register />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/crisis" element={<CrisisPage />} />

      {/* 首页 - 需要登录 */}
      <Route path="/" element={
        <ProtectedRoute>
          <Home />
        </ProtectedRoute>
      } />

      {/* 知识库 - 需要登录 */}
      <Route path="/knowledge" element={
        <ProtectedRoute>
          <Knowledge />
        </ProtectedRoute>
      } />
      <Route path="/knowledge/:id" element={
        <ProtectedRoute>
          <ArticleDetail />
        </ProtectedRoute>
      } />

      {/* 测评相关 - 需要登录才能访问 */}
      <Route path="/mbti" element={
        <ProtectedRoute>
          <MbtiTest />
        </ProtectedRoute>
      } />
      <Route path="/mbti/quick" element={
        <ProtectedRoute>
          <MbtiTest />
        </ProtectedRoute>
      } />
      <Route path="/sbti" element={
        <ProtectedRoute>
          <SbtiIndex />
        </ProtectedRoute>
      } />
      <Route path="/sbti/test" element={
        <ProtectedRoute>
          <SbtiTest />
        </ProtectedRoute>
      } />
      <Route path="/attachment" element={
        <ProtectedRoute>
          <AttachmentIndex />
        </ProtectedRoute>
      } />
      <Route path="/attachment/test" element={
        <ProtectedRoute>
          <AttachmentTest />
        </ProtectedRoute>
      } />
      <Route path="/comprehensive" element={
        <ProtectedRoute>
          <ComprehensiveTest />
        </ProtectedRoute>
      } />

      {/* 受保护的路由 - 需要登录 */}
      <Route path="/mbti/result" element={
        <ProtectedRoute>
          <MbtiResult />
        </ProtectedRoute>
      } />
      <Route path="/chat" element={
        <ProtectedRoute>
          <Chat />
        </ProtectedRoute>
      } />
      <Route path="/chat/:sessionId" element={
        <ProtectedRoute>
          <Chat />
        </ProtectedRoute>
      } />
      <Route path="/assistants" element={
        <ProtectedRoute>
          <AssistantSquare />
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      } />
      <Route path="/profile/deep" element={
        <ProtectedRoute>
          <DeepProfile />
        </ProtectedRoute>
      } />
      <Route path="/knowledge/collections" element={
        <ProtectedRoute>
          <KnowledgeCollections />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute>
          <Admin />
        </ProtectedRoute>
      } />
      <Route path="/diary" element={
        <ProtectedRoute>
          <DiaryList />
        </ProtectedRoute>
      } />
      <Route path="/diary/create" element={
        <ProtectedRoute>
          <DiaryCreate />
        </ProtectedRoute>
      } />
      <Route path="/diary/:id" element={
        <ProtectedRoute>
          <DiaryDetail />
        </ProtectedRoute>
      } />
      <Route path="/diary/:id/edit" element={
        <ProtectedRoute>
          <DiaryCreate />
        </ProtectedRoute>
      } />
      <Route path="/diary/stats" element={
        <ProtectedRoute>
          <DiaryStats />
        </ProtectedRoute>
      } />
      <Route path="/onboarding" element={
        <ProtectedRoute>
          <Onboarding />
        </ProtectedRoute>
      } />
      <Route path="/achievements" element={
        <ProtectedRoute>
          <AchievementsPage />
        </ProtectedRoute>
      } />
      <Route path="/checkin" element={
        <ProtectedRoute>
          <CheckInPage />
        </ProtectedRoute>
      } />
      <Route path="/sbti/result" element={
        <ProtectedRoute>
          <SbtiResult />
        </ProtectedRoute>
      } />
      <Route path="/attachment/result" element={
        <ProtectedRoute>
          <AttachmentResult />
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default function App() {
  const navigate = useNavigate()

  // 设置全局 navigate 函数，用于 401 时跳转到登录页
  useEffect(() => {
    setNavigate(navigate)
  }, [navigate])

  return (
    <AntApp>
      <Layout>
        <ErrorBoundary>
          <Suspense fallback={
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh'
            }}>
              <Spin size="large" />
            </div>
          }>
            <AppRoutes />
          </Suspense>
        </ErrorBoundary>
      </Layout>
    </AntApp>
  )
}
