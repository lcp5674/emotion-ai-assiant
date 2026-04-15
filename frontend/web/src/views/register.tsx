import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, App } from 'antd'
import { UserOutlined, LockOutlined, PhoneOutlined, MailOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import { useTheme } from '../hooks/useTheme'

export default function Register() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { setAuth } = useAuthStore()
  const { themeColors, themeColor } = useTheme()
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [countdown, setCountdown] = useState(0)

  const sendCode = async (phone: string) => {
    setSending(true)
    try {
      await api.auth.sendCode(phone)
      message.success('验证码已发送')
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
      message.error(error.response?.data?.detail || '发送失败')
    } finally {
      setSending(false)
    }
  }

  const onFinish = async (values: { phone: string; password: string; code: string; nickname?: string }) => {
    setLoading(true)
    try {
      const res = await api.auth.register(values)
      setAuth(res.user, res.access_token, res.refresh_token)
      message.success('注册成功')
      navigate('/mbti')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
    }}>
      <Card style={{ 
        width: 400, 
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        borderRadius: '12px',
        border: 'none'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, color: themeColors[themeColor], marginBottom: 8, fontWeight: 700 }}>注册</h1>
          <p style={{ color: '#8c8c8c' }}>加入心灵伴侣AI</p>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="phone"
            rules={[
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' },
            ]}
          >
            <Input
              prefix={<PhoneOutlined style={{ color: themeColors[themeColor] }} />}
              placeholder="手机号"
            />
          </Form.Item>

          <Form.Item
            name="code"
            rules={[
              { required: true, message: '请输入验证码' },
              { len: 6, message: '验证码为6位' },
            ]}
          >
            <Input
              prefix={<LockOutlined style={{ color: themeColors[themeColor] }} />}
              placeholder="验证码"
              suffix={
                <Button
                  type="link"
                  size="small"
                  style={{ color: themeColors[themeColor] }}
                  onClick={() => {
                    const phone = document.querySelector('input[name="phone"]')?.getAttribute('value')
                    if (phone && /^1[3-9]\d{9}$/.test(phone)) {
                      sendCode(phone)
                    } else {
                      message.warning('请先输入正确的手机号')
                    }
                  }}
                  disabled={countdown > 0}
                >
                  {countdown > 0 ? `${countdown}s` : '获取验证码'}
                </Button>
              }
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
              { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码需包含字母和数字' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: themeColors[themeColor] }} />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="nickname"
          >
            <Input
              prefix={<UserOutlined style={{ color: themeColors[themeColor] }} />}
              placeholder="昵称（可选）"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ 
                background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                border: 'none',
                borderRadius: '8px',
                height: 48,
                fontSize: 16,
                fontWeight: 600
              }}
            >
              注册
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            已有账号？<Link to="/login">立即登录</Link>
          </div>
        </Form>
      </Card>
    </div>
  )
}