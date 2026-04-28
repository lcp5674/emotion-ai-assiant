import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Progress, Spin, Empty, Button, List, Tag, Modal, Form, Input, DatePicker, message, Space } from 'antd'
import { CalendarOutlined, TrophyOutlined, FireOutlined, GiftOutlined, ArrowLeftOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { api } from '../api/request'
import { useAuthStore } from '../stores'
import dayjs from 'dayjs'

interface CheckInRecord {
  id: number
  check_in_date: string
  check_in_time: string
  streak_days: number
  xp_reward: number
  note?: string
}

interface CheckInStats {
  total_checkins: number
  current_streak: number
  max_streak: number
  total_xp_earned: number
  this_month_checkins: number
  last_checkin_date?: string
  checkin_history: CheckInRecord[]
}

interface TodayStatus {
  checked_in: boolean
  checkin?: CheckInRecord
}

export default function CheckInPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<CheckInStats | null>(null)
  const [todayStatus, setTodayStatus] = useState<TodayStatus | null>(null)
  const [checkinLoading, setCheckinLoading] = useState(false)
  const [reminderVisible, setReminderVisible] = useState(false)
  const [reminderLoading, setReminderLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, todayRes] = await Promise.all([
        api.checkin.stats(),
        api.checkin.todayStatus(),
      ])
      setStats(statsRes)
      setTodayStatus(todayRes)
    } catch (error) {
      console.error('获取打卡数据失败', error)
      message.error('获取打卡数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCheckin = async () => {
    setCheckinLoading(true)
    try {
      const result = await api.checkin.daily()
      message.success(`打卡成功！连续${result.streak_days}天，获得${result.xp_reward}经验`)
      loadData()
    } catch (error: any) {
      if (error.message?.includes('已打卡')) {
        message.info('今日已打卡')
      } else {
        message.error(error.message || '打卡失败')
      }
    } finally {
      setCheckinLoading(false)
    }
  }

const handleCreateReminder = async (values: any) => {
      setReminderLoading(true)
      try {
        await api.checkin.createReminder({
          reminder_type: 'daily_checkin',
          title: values.title,
          message: values.message || '',
          scheduled_time: dayjs(values.scheduled_time).format('YYYY-MM-DDTHH:mm:ss'),
        })
        message.success('提醒创建成功')
        setReminderVisible(false)
        form.resetFields()
      } catch (error) {
        console.error('创建提醒失败', error)
        message.error('创建提醒失败')
      } finally {
        setReminderLoading(false)
      }
    }

  const getStreakEmoji = (streak: number) => {
    if (streak >= 30) return '🔥'
    if (streak >= 7) return '⭐'
    if (streak >= 3) return '✨'
    return '🌱'
  }

  const getStreakColor = (streak: number) => {
    if (streak >= 30) return '#ff4d4f'
    if (streak >= 7) return '#fa8c16'
    if (streak >= 3) return '#52c41a'
    return '#1890ff'
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      <header style={{
        background: 'linear-gradient(135deg, #fa8c16 0%, #faad14 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <Button
            icon={<ArrowLeftOutlined />}
            type="text"
            style={{ color: '#fff', position: 'absolute', left: 16, top: 20 }}
            onClick={() => navigate(-1)}
          >
            返回
          </Button>
          <CalendarOutlined style={{ fontSize: 48, marginBottom: 16 }} />
          <h1 style={{ fontSize: 28, marginBottom: 8 }}>每日打卡</h1>
          <p>坚持打卡，获得更多成就与奖励</p>
        </div>
      </header>

      <div className="container" style={{ marginTop: -20 }}>
        {/* 打卡卡片 */}
        <Card style={{ marginBottom: 24, borderRadius: 16 }}>
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            {/* 打卡按钮 */}
            <div style={{
              width: 160,
              height: 160,
              borderRadius: '50%',
              background: todayStatus?.checked_in
                ? 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)'
                : 'linear-gradient(135deg, #fa8c16 0%, #faad14 100%)',
              display: 'inline-flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              boxShadow: todayStatus?.checked_in
                ? '0 8px 25px rgba(82, 196, 26, 0.4)'
                : '0 8px 25px rgba(250, 140, 22, 0.4)',
              cursor: todayStatus?.checked_in ? 'default' : 'pointer',
              transition: 'all 0.3s ease',
              marginBottom: 24,
            }}
              onClick={() => !todayStatus?.checked_in && handleCheckin()}
            >
              {todayStatus?.checked_in ? (
                <>
                  <CheckCircleOutlined style={{ fontSize: 48, marginBottom: 8 }} />
                  <span style={{ fontSize: 16, fontWeight: 'bold' }}>已打卡</span>
                </>
              ) : (
                <>
                  <span style={{ fontSize: 48 }}>+</span>
                  <span style={{ fontSize: 16, fontWeight: 'bold' }}>打卡</span>
                </>
              )}
            </div>

            {checkinLoading ? (
              <Spin />
            ) : !todayStatus?.checked_in && (
              <Button
                type="primary"
                size="large"
                onClick={handleCheckin}
                style={{
                  background: 'linear-gradient(135deg, #fa8c16 0%, #faad14 100%)',
                  border: 'none',
                  borderRadius: 24,
                  padding: '8px 40px',
                  fontSize: 16,
                }}
              >
                立即打卡
              </Button>
            )}

            {/* 当前连续天数 */}
            {stats && (
              <div style={{ marginTop: 32 }}>
                <Tag
                  icon={<FireOutlined />}
                  color={getStreakColor(stats.current_streak)}
                  style={{
                    fontSize: 16,
                    padding: '8px 20px',
                    borderRadius: 20,
                    marginRight: 12,
                  }}
                >
                  连续 {stats.current_streak} 天 {getStreakEmoji(stats.current_streak)}
                </Tag>
                <Tag
                  icon={<TrophyOutlined />}
                  style={{ fontSize: 16, padding: '8px 20px', borderRadius: 20 }}
                >
                  历史最高 {stats.max_streak} 天
                </Tag>
              </div>
            )}
          </div>
        </Card>

        {/* 统计数据 */}
        {stats && (
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card style={{ textAlign: 'center', borderRadius: 16 }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fa8c16' }}>
                  {stats.total_checkins}
                </div>
                <div style={{ color: '#8c8c8c', fontSize: 12 }}>总打卡次数</div>
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card style={{ textAlign: 'center', borderRadius: 16 }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#52c41a' }}>
                  {stats.this_month_checkins}
                </div>
                <div style={{ color: '#8c8c8c', fontSize: 12 }}>本月打卡</div>
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card style={{ textAlign: 'center', borderRadius: 16 }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#722ed1' }}>
                  {stats.total_xp_earned}
                </div>
                <div style={{ color: '#8c8c8c', fontSize: 12 }}>累计经验</div>
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card style={{ textAlign: 'center', borderRadius: 16 }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#1890ff' }}>
                  {stats.current_streak}
                </div>
                <div style={{ color: '#8c8c8c', fontSize: 12 }}>当前连续</div>
              </Card>
            </Col>
          </Row>
        )}

        {/* 打卡记录 */}
        <Card
          title="打卡记录"
          extra={
            <Button
              icon={<ClockCircleOutlined />}
              onClick={() => setReminderVisible(true)}
            >
              设置回访提醒
            </Button>
          }
          style={{ marginBottom: 24 }}
        >
          {stats?.checkin_history && stats.checkin_history.length > 0 ? (
            <List
              dataSource={stats.checkin_history}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: 8,
                        background: 'linear-gradient(135deg, #fa8c16 0%, #faad14 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 'bold',
                      }}>
                        {dayjs(item.check_in_date).format('DD')}
                      </div>
                    }
                    title={dayjs(item.check_in_date).format('YYYY年MM月DD日')}
                    description={
                      <Space>
                        <Tag color="orange">连续 {item.streak_days} 天</Tag>
                        <Tag color="green">+{item.xp_reward} 经验</Tag>
                        {item.note && <span style={{ color: '#8c8c8c' }}>{item.note}</span>}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty description="还没有打卡记录" />
          )}
        </Card>

        {/* 打卡奖励说明 */}
        <Card title="打卡奖励" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center' }}>
            {[
              { days: 1, xp: 5, color: '#1890ff' },
              { days: 3, xp: 8, color: '#52c41a' },
              { days: 7, xp: 15, color: '#fa8c16' },
              { days: 14, xp: 25, color: '#722ed1' },
              { days: 30, xp: 50, color: '#eb2f96' },
              { days: 60, xp: 80, color: '#fa8c16' },
              { days: 90, xp: 120, color: '#ff4d4f' },
            ].map((reward) => (
              <div
                key={reward.days}
                style={{
                  padding: '12px 20px',
                  borderRadius: 12,
                  background: `${reward.color}10`,
                  border: `1px solid ${reward.color}30`,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 20, fontWeight: 'bold', color: reward.color }}>
                  {reward.xp} XP
                </div>
                <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                  连续 {reward.days} 天
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 回访提醒弹窗 */}
      <Modal
        title="设置回访提醒"
        open={reminderVisible}
        onCancel={() => setReminderVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateReminder}
        >
          <Form.Item
            name="title"
            label="提醒标题"
            rules={[{ required: true, message: '请输入提醒标题' }]}
          >
            <Input placeholder="例如：每日心情记录提醒" />
          </Form.Item>

              <Form.Item
                name="message"
                label="提醒内容"
                rules={[{ required: false }]} // 提醒内容不是必填的
              >
                <Input.TextArea placeholder="请输入提醒内容..." rows={3} />
              </Form.Item>

          <Form.Item
            name="scheduled_time"
            label="提醒时间"
            rules={[{ required: true, message: '请选择提醒时间' }]}
          >
            <DatePicker
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              style={{ width: '100%' }}
              disabledDate={(current) => current && current < dayjs().startOf('day')}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={reminderLoading}>
                创建提醒
              </Button>
              <Button onClick={() => setReminderVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
