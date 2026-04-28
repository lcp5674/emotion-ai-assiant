import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, App, Tabs, Checkbox, message } from 'antd'
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
    for (let i = 0; i < 25; i++) {
      shapes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 120 + 60,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.12 + 0.03
      })
    }

    let animationId: number
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const gradient_bg = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
      gradient_bg.addColorStop(0, gradient[0] + '15')
      gradient_bg.addColorStop(1, gradient[1] + '25')
      ctx.fillStyle = gradient_bg
      ctx.fillRect(0, 0, canvas.width, canvas.height)

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

export default function Register() {
  const navigate = useNavigate()
  const { message: antMessage } = App.useApp()
  const { setAuth } = useAuthStore()
  const { themeColors, themeColor } = useTheme()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [registerType, setRegisterType] = useState<'username' | 'phone' | 'email'>('username')
  const [agreed, setAgreed] = useState(false)

  const themeGradient = themeColors[themeColor]

  const sendCode = async () => {
    try {
      const phone = form.getFieldValue('phone')
      console.log('获取手机号:', phone, '类型:', typeof phone)

      if (!phone) {
        antMessage.warning('请输入手机号')
        return
      }

      const phoneStr = String(phone).trim()
      if (!/^1[3-9]\d{9}$/.test(phoneStr)) {
        antMessage.warning('请输入正确的手机号')
        return
      }

      setSending(true)
      await api.auth.sendCode(phoneStr)
      antMessage.success('验证码已发送')
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (error: any) {
      console.error('发送验证码错误:', error)
      let errMsg = '发送失败，请稍后重试'
      if (error.response?.data?.detail) {
        errMsg = error.response.data.detail
      } else if (error.message) {
        errMsg = error.message
      }
      antMessage.error(errMsg)
    } finally {
      setSending(false)
    }
  }

  const onFinish = async (values: any) => {
    if (!agreed) {
      antMessage.warning('请先同意用户协议和隐私政策')
      return
    }

    setLoading(true)
    try {
      const res = await api.auth.register(values)
      setAuth(res.user, res.access_token, res.refresh_token)
      antMessage.success('注册成功')
      const redirectPath = localStorage.getItem('redirectPath') || '/'
      localStorage.removeItem('redirectPath')
      navigate(redirectPath)
    } catch (error: any) {
      antMessage.error(error.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取当前注册方式需要填写的字段
  const getFields = () => {
    switch (registerType) {
      case 'phone':
        return [
          {
            name: 'phone',
            label: '手机号',
            placeholder: '请输入手机号',
            prefix: <PhoneOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' },
            ],
            field: 'phone'
          },
          {
            name: 'code',
            label: '验证码',
            placeholder: '验证码',
            prefix: null,
            rules: [
              { required: true, message: '请输入验证码' },
              { len: 6, message: '验证码为6位' },
            ],
            field: 'code',
            hasCodeButton: true
          },
          {
            name: 'password',
            label: '密码',
            placeholder: '密码（至少6位）',
            prefix: <LockOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
            ],
            field: 'password'
          },
          {
            name: 'nickname',
            label: '昵称',
            placeholder: '昵称（可选）',
            prefix: <UserOutlined style={{ color: themeGradient }} />,
            rules: [],
            field: 'nickname'
          }
        ]
      case 'email':
        return [
          {
            name: 'email',
            label: '邮箱',
            placeholder: '请输入邮箱',
            prefix: <MailOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入正确的邮箱格式' },
            ],
            field: 'email'
          },
          {
            name: 'password',
            label: '密码',
            placeholder: '密码（至少6位）',
            prefix: <LockOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
            ],
            field: 'password'
          },
          {
            name: 'nickname',
            label: '昵称',
            placeholder: '昵称（可选）',
            prefix: <UserOutlined style={{ color: themeGradient }} />,
            rules: [],
            field: 'nickname'
          }
        ]
      default: // username
        return [
          {
            name: 'username',
            label: '用户名',
            placeholder: '用户名（3-20位字母、数字或下划线）',
            prefix: <UserOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
            ],
            field: 'username'
          },
          {
            name: 'password',
            label: '密码',
            placeholder: '密码（至少6位）',
            prefix: <LockOutlined style={{ color: themeGradient }} />,
            rules: [
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
            ],
            field: 'password'
          },
          {
            name: 'nickname',
            label: '昵称',
            placeholder: '昵称（可选）',
            prefix: <UserOutlined style={{ color: themeGradient }} />,
            rules: [],
            field: 'nickname'
          }
        ]
    }
  }

  const fields = getFields()

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}dd 100%)`,
      position: 'relative',
      overflow: 'hidden',
      padding: '40px 0',
    }}>
      <AnimatedBackground gradient={[themeGradient, themeGradient]} />

      {/* Decorative Elements */}
      <div style={{
        position: 'fixed',
        top: '15%',
        right: '15%',
        width: 250,
        height: 250,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%)`,
        animation: 'float 7s ease-in-out infinite',
      }} />
      <div style={{
        position: 'fixed',
        bottom: '20%',
        left: '8%',
        width: 180,
        height: 180,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)`,
        animation: 'float 5s ease-in-out infinite reverse',
      }} />

      <Card
        style={{
          width: '100%',
          maxWidth: 440,
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
            开启心灵之旅
          </h1>
          <p style={{ color: '#6b7280', fontSize: 15, margin: 0 }}>
            加入心灵伴侣AI，发现真实的自己
          </p>
        </div>

        {/* 注册方式切换 */}
        <Tabs
          activeKey={registerType}
          onChange={(key) => {
            setRegisterType(key as any)
            form.resetFields()
          }}
          centered
          style={{ marginBottom: 24 }}
          items={[
            {
              key: 'username',
              label: '用户名注册',
            },
            {
              key: 'phone',
              label: '手机注册',
            },
            {
              key: 'email',
              label: '邮箱注册',
            },
          ]}
        />

        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
          initialValues={{ username: '', phone: '', email: '', code: '', password: '', nickname: '' }}
        >
          {fields.map((field) => (
            <Form.Item
              key={field.name}
              name={field.name}
              rules={field.rules as any}
            >
              {field.name === 'code' ? (
                <Input
                  prefix={field.prefix}
                  placeholder={field.placeholder}
                  style={{
                    borderRadius: '12px',
                    height: 52,
                    border: focusedField === field.name ? `2px solid ${themeGradient}` : '1px solid #e5e7eb',
                    transition: 'all 0.3s ease',
                  }}
                  onFocus={() => setFocusedField(field.name)}
                  onBlur={() => setFocusedField(null)}
                  suffix={
                    <Button
                      type="link"
                      size="small"
                      style={{
                        color: themeGradient,
                        fontWeight: 600,
                        padding: '4px 8px',
                      }}
                      onClick={sendCode}
                      disabled={countdown > 0 || sending}
                    >
                      {countdown > 0 ? `${countdown}s` : sending ? '发送中...' : '获取验证码'}
                    </Button>
                  }
                />
              ) : (
                <Input
                  prefix={field.prefix}
                  placeholder={field.placeholder}
                  style={{
                    borderRadius: '12px',
                    height: 52,
                    border: focusedField === field.name ? `2px solid ${themeGradient}` : '1px solid #e5e7eb',
                    transition: 'all 0.3s ease',
                  }}
                  onFocus={() => setFocusedField(field.name)}
                  onBlur={() => setFocusedField(null)}
                />
              )}
            </Form.Item>
          ))}

          {/* 用户协议 */}
          <Form.Item>
            <Checkbox
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              style={{ marginTop: 8 }}
            >
              <span style={{ color: '#6b7280', fontSize: 13 }}>
                我已阅读并同意
                <a href="/terms-of-service" target="_blank" style={{ color: themeGradient }}> 《用户服务条款》</a>
                和
                <a href="/privacy-policy" target="_blank" style={{ color: themeGradient }}> 《隐私政策》</a>
              </span>
            </Checkbox>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              disabled={!agreed}
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
              注册
            </Button>
          </Form.Item>

          <div style={{
            textAlign: 'center',
            marginTop: 24,
            color: '#6b7280',
            fontSize: 14,
          }}>
            已有账号？
            <Link
              to="/login"
              style={{
                color: themeGradient,
                fontWeight: 600,
                marginLeft: 4,
              }}
            >
              立即登录
            </Link>
          </div>
        </Form>

        {/* Benefits */}
        <div style={{
          marginTop: 32,
          paddingTop: 24,
          borderTop: '1px solid #f3f4f6',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-around',
            textAlign: 'center',
          }}>
            {[
              { icon: '✨', text: '免费测评' },
              { icon: '🔒', text: '隐私保护' },
              { icon: '💝', text: '专属陪伴' },
            ].map((item, idx) => (
              <div key={idx} style={{ flex: 1 }}>
                <div style={{ fontSize: 24, marginBottom: 4 }}>{item.icon}</div>
                <div style={{ fontSize: 12, color: '#9ca3af' }}>{item.text}</div>
              </div>
            ))}
          </div>
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
