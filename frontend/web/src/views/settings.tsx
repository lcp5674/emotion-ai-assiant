import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Avatar, App, Spin } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'

export default function Settings() {
  const navigate = useNavigate()
  const { message: antMessage } = App.useApp()
  const { user, updateUser, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  // 处理用户数据，确保是字符串类型
  const getUserValue = (key: string, defaultValue: string = '') => {
    if (!user) return defaultValue
    const value = (user as any)[key]
    return typeof value === 'string' ? value : defaultValue
  }

  const nickname = getUserValue('nickname', '')
  const phone = getUserValue('phone', '')
  const mbtiType = getUserValue('mbti_type', '未测试')

  // 未登录时显示加载状态
  if (!isAuthenticated) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  const handleSubmit = async (values: { nickname: string }) => {
    setLoading(true)
    try {
      await api.user.updateProfile(values)
      updateUser(values)
      antMessage.success('信息更新成功')
      navigate('/profile')
    } catch (error: any) {
      antMessage.error(error.response?.data?.detail || '更新失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '24px 16px' }}>
      <h1 style={{ fontSize: 24, marginBottom: 24 }}>账户设置</h1>

      <Card>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Avatar size={80} icon={<UserOutlined />} style={{ background: '#722ed1' }} />
          <div style={{ marginTop: 8, color: '#8c8c8c' }}>点击头像更换</div>
        </div>

        <Form
          form={form}
          layout="vertical"
          initialValues={{ nickname }}
          onFinish={handleSubmit}
        >
          <Form.Item
            name="nickname"
            label="昵称"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="请输入昵称" maxLength={50} />
          </Form.Item>

          <Form.Item label="手机号">
            <Input value={phone} disabled />
          </Form.Item>

          <Form.Item label="MBTI类型">
            <Input value={mbtiType} disabled />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              保存修改
            </Button>
          </Form.Item>

          <Form.Item>
            <Button block onClick={() => navigate('/profile')}>
              返回个人资料
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}