import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, App, Tabs } from 'antd'
import { UserOutlined, LockOutlined, HeartOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import { useTheme } from '../hooks/useTheme'

// Animated Background Component
function AnimatedBackground({ gradient }: { gradient: string[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const shapes: { x: number; y: number; size: number; vx: number; vy: number; alpha: number }[] = []
    for (let i = 0; i < 20; i++) {
      shapes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 100 + 50,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        alpha: Math.random() * 0.1 + 0.05
      })
    }

    let animationId: number
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw gradient background
      const gradient_bg = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
      gradient_bg.addColorStop(0, gradient[0] + '20')
      gradient_bg.addColorStop(1, gradient[1] + '20')
      ctx.fillStyle = gradient_bg
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw floating shapes
      shapes.forEach(shape => {
        shape.x += shape.vx
        shape.y += shape.vy
        if (shape.x < -shape.size) shape.x = canvas.width + shape.size
        if (shape.x > canvas.width + shape.size) shape.x = -shape.size
        if (shape.y < -shape.size) shape.y = canvas.height + shape.size
        if (shape.y > canvas.height + shape.size) shape.y = -shape.size

        ctx.beginPath()
        const grd = ctx.createRadialGradient(shape.x, shape.y, 0, shape.x, shape.y, shape.size)
        grd.addColorStop(0, gradient[0] + Math.floor(shape.alpha * 255).toString(16).padStart(2, '0'))
        grd.addColorStop(1, 'transparent')
        ctx.fillStyle = grd
        ctx.arc(shape.x, shape.y, shape.size, 0, Math.PI * 2)
        ctx.fill()
      })

      animationId = requestAnimationFrame(animate)
    }
    animate()

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    window.addEventListener('resize', handleResize)
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', handleResize)
    }
  }, [gradient])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none'
      }}
    />
  )
}

export default function Login() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { setAuth } = useAuthStore()
  const { themeColors, themeColor } = useTheme()
  const [loading, setLoading] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [loginType, setLoginType] = useState<'username' | 'phone' | 'email'>('username')

  const themeGradient = themeColors[themeColor]

  const onFinish = async (values: { identifier: string; password: string }) => {
    setLoading(true)
    try {
      const res = await api.auth.login(values)
      setAuth(res.user, res.access_token, res.refresh_token)
      message.success('登录成功')
      const redirectPath = localStorage.getItem('redirectPath') || '/'
      localStorage.removeItem('redirectPath')
      navigate(redirectPath)
    } catch (error: any) {
      let errorMsg = '登录失败，请稍后重试'

      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail
      } else if (error.message) {
        errorMsg = error.message
      } else if (error.status === 401) {
        errorMsg = '账号或密码错误'
      }

      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // 根据登录类型获取输入框提示和图标
  const getPlaceholder = () => {
    switch (loginType) {
      case 'phone':
        return '请输入手机号'
      case 'email':
        return '请输入邮箱'
      default:
        return '请输入用户名 / 手机号 / 邮箱'
    }
  }

  const getPrefixIcon = () => {
    switch (loginType) {
      case 'phone':
        return <PhoneOutlined style={{ color: themeGradient }} />
      case 'email':
        return <MailOutlined style={{ color: themeGradient }} />
      default:
        return <UserOutlined style={{ color: themeGradient }} />
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}dd 100%)`,
      position: 'relative',
      overflow: 'hidden',
    }}>
      <AnimatedBackground gradient={[themeGradient, themeGradient]} />

      {/* Decorative Elements */}
      <div style={{
        position: 'fixed',
        top: '10%',
        left: '10%',
        width: 200,
        height: 200,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%)`,
        animation: 'float 6s ease-in-out infinite',
      }} />
      <div style={{
        position: 'fixed',
        bottom: '15%',
        right: '10%',
        width: 300,
        height: 300,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)`,
        animation: 'float 8s ease-in-out infinite reverse',
      }} />

      <Card
        style={{
          width: '100%',
          maxWidth: 420,
          boxShadow: '0 25px 80px rgba(0,0,0,0.25)',
          borderRadius: '24px',
          border: 'none',
          margin: '0 16px',
          position: 'relative',
          zIndex: 1,
          backdropFilter: 'blur(20px)',
          background: 'rgba(255, 255, 255, 0.95)',
        }}
        bodyStyle={{ padding: '48px 40px' }}
      >
        {/* Logo */}
        <div style={{
          textAlign: 'center',
          marginBottom: 32,
        }}>
          <div style={{
            width: 72,
            height: 72,
            borderRadius: '20px',
            background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            boxShadow: `0 12px 40px ${themeGradient}40`,
          }}>
            <HeartOutlined style={{ fontSize: 32, color: '#fff' }} />
          </div>
          <h1 style={{
            fontSize: 28,
            color: '#1f2937',
            marginBottom: 8,
            fontWeight: 700,
            fontFamily: 'Inter, sans-serif',
          }}>
            欢迎回来
          </h1>
          <p style={{ color: '#6b7280', fontSize: 15, margin: 0 }}>
            与懂你的AI助手开始心灵之旅
          </p>
        </div>

        {/* 登录方式切换 */}
        <Tabs
          activeKey={loginType}
          onChange={(key) => setLoginType(key as any)}
          centered
          style={{ marginBottom: 24 }}
          items={[
            {
              key: 'username',
              label: '用户名登录',
            },
            {
              key: 'phone',
              label: '手机登录',
            },
            {
              key: 'email',
              label: '邮箱登录',
            },
          ]}
        />

        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="identifier"
            rules={[
              { required: true, message: '请输入账号' },
            ]}
          >
            <Input
              prefix={getPrefixIcon()}
              placeholder={getPlaceholder()}
              style={{
                borderRadius: '12px',
                height: 52,
                border: focusedField === 'identifier' ? `2px solid ${themeGradient}` : '1px solid #e5e7eb',
                transition: 'all 0.3s ease',
              }}
              onFocus={() => setFocusedField('identifier')}
              onBlur={() => setFocusedField(null)}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: themeGradient }} />}
              placeholder="密码"
              style={{
                borderRadius: '12px',
                height: 52,
                border: focusedField === 'password' ? `2px solid ${themeGradient}` : '1px solid #e5e7eb',
                transition: 'all 0.3s ease',
              }}
              onFocus={() => setFocusedField('password')}
              onBlur={() => setFocusedField(null)}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{
                background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
                border: 'none',
                borderRadius: '14px',
                height: 52,
                fontSize: 16,
                fontWeight: 600,
                boxShadow: `0 8px 30px ${themeGradient}40`,
                transition: 'all 0.3s ease',
              }}
            >
              登录
            </Button>
          </Form.Item>

          <div style={{
            textAlign: 'center',
            marginTop: 24,
            color: '#6b7280',
            fontSize: 14,
          }}>
            还没有账号？
            <Link
              to="/register"
              style={{
                color: themeGradient,
                fontWeight: 600,
                marginLeft: 4,
              }}
            >
              立即注册
            </Link>
          </div>
        </Form>

        {/* Features Preview */}
        <div style={{
          marginTop: 32,
          paddingTop: 24,
          borderTop: '1px solid #f3f4f6',
          display: 'flex',
          justifyContent: 'space-around',
          textAlign: 'center',
        }}>
          {[
            { icon: '🔮', text: 'MBTI测评' },
            { icon: '💝', text: 'AI陪伴' },
            { icon: '📚', text: '心理知识' },
          ].map((item, idx) => (
            <div key={idx} style={{ flex: 1 }}>
              <div style={{ fontSize: 24, marginBottom: 4 }}>{item.icon}</div>
              <div style={{ fontSize: 12, color: '#9ca3af' }}>{item.text}</div>
            </div>
          ))}
        </div>
      </Card>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
      `}</style>
    </div>
  )
}
