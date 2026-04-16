import { Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuthStore } from '../stores'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isHydrated = useAuthStore((state) => state.isHydrated)

  // 如果auth状态尚未从localStorage恢复，显示加载动画
  // 这样可以避免在认证状态确定之前渲染子组件导致401错误
  if (!isHydrated) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <Spin size="large" />
      </div>
    )
  }

  // auth状态已恢复，如果未登录则重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
