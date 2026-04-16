import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { Card, Form, Input, Button, Avatar, App, Divider, Modal, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'

export default function Settings() {
  const navigate = useNavigate()
  const { message: antMessage } = App.useApp()
  const { user, updateUser, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [passwordModalVisible, setPasswordModalVisible] = useState(false)
  const [passwordForm] = Form.useForm()
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

  // 未登录时重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
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

  const handlePasswordChange = async (values: { old_password: string; new_password: string; confirm_password: string }) => {
    if (values.new_password !== values.confirm_password) {
      antMessage.error('两次输入的密码不一致')
      return
    }
    if (values.new_password.length < 6) {
      antMessage.error('新密码长度不能少于6位')
      return
    }
    setLoading(true)
    try {
      await api.user.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      })
      antMessage.success('密码修改成功')
      setPasswordModalVisible(false)
      passwordForm.resetFields()
    } catch (error: any) {
      antMessage.error(error.response?.data?.detail || '密码修改失败')
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

      {/* 修改密码 */}
      <Card style={{ marginTop: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <LockOutlined style={{ fontSize: 20, color: '#722ed1' }} />
          <span style={{ fontSize: 16, fontWeight: 500 }}>安全设置</span>
        </div>
        <Button
          block
          onClick={() => setPasswordModalVisible(true)}
          style={{ height: 44 }}
        >
          修改密码
        </Button>
      </Card>

      {/* 修改密码弹窗 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onCancel={() => {
          setPasswordModalVisible(false)
          passwordForm.resetFields()
        }}
        footer={null}
        destroyOnClose
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handlePasswordChange}
        >
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password placeholder="请输入当前密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[{ required: true, message: '请输入新密码' }, { min: 6, message: '新密码长度不能少于6位' }]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            rules={[{ required: true, message: '请再次输入新密码' }]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'center' }}>
            <Space>
              <Button onClick={() => {
                setPasswordModalVisible(false)
                passwordForm.resetFields()
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                确定修改
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}