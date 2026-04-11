import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense } from 'react'
import { Button, App as AntApp, Spin } from 'antd'
import { SunOutlined, MoonOutlined } from '@ant-design/icons'
import { ErrorBoundary } from './components/ErrorBoundary'
import { useTheme } from './hooks/useTheme'
import { useAuthStore } from './stores'
import { lazy } from 'react'

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
const Admin = lazy(() => import('./views/admin'))
const DiaryList = lazy(() => import('./views/diary'))
const DiaryDetail = lazy(() => import('./views/diary/detail'))
const DiaryCreate = lazy(() => import('./views/diary/create'))
const DiaryStats = lazy(() => import('./views/diary/stats'))
const Onboarding = lazy(() => import('./views/onboarding'))
const PrivacyPage = lazy(() => import('./views/privacy'))
const CrisisPage = lazy(() => import('./views/crisis'))
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

function Layout({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme()

  return (
    <>
      <div style={{
        position: 'fixed',
        top: 12,
        right: 16,
        zIndex: 1000,
      }}>
        <Button
          type="text"
          icon={theme === 'light' ? <MoonOutlined /> : <SunOutlined />}
          onClick={toggleTheme}
        />
      </div>
      {children}
    </>
  )
}

function AppRoutes() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <Register />} />
      <Route path="/mbti" element={<MbtiTest />} />
      <Route path="/mbti/result" element={<MbtiResult />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/chat/:sessionId" element={<Chat />} />
      <Route path="/assistants" element={<AssistantSquare />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/knowledge" element={<Knowledge />} />
      <Route path="/knowledge/:id" element={<ArticleDetail />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/diary" element={<DiaryList />} />
      <Route path="/diary/create" element={<DiaryCreate />} />
      <Route path="/diary/:id" element={<DiaryDetail />} />
      <Route path="/diary/:id/edit" element={<DiaryCreate />} />
      <Route path="/diary/stats" element={<DiaryStats />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/crisis" element={<CrisisPage />} />

      {/* SBTI */}
      <Route path="/sbti" element={<SbtiIndex />} />
      <Route path="/sbti/test" element={<SbtiTest />} />
      <Route path="/sbti/result" element={<SbtiResult />} />

      {/* 依恋风格 */}
      <Route path="/attachment" element={<AttachmentIndex />} />
      <Route path="/attachment/test" element={<AttachmentTest />} />
      <Route path="/attachment/result" element={<AttachmentResult />} />

      {/* 深度画像 */}
      <Route path="/profile/deep" element={<DeepProfile />} />
    </Routes>
  )
}

export default function App() {
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
