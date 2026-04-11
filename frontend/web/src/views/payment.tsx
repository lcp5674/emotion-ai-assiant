/**
 * 会员支付页面
 * 展示会员套餐，支持购买
 */
import { useEffect, useState } from 'react'
import { Card, Button, List, Tag, Radio, Space, message, Spin } from 'antd'
import { CheckOutlined, CrownOutlined } from '@ant-design/icons'
import { apiClient } from '../utils/api'
import './payment.css'

interface Plan {
  id: string
  name: string
  display_name: string
  description: string
  price: number
  duration_days: number
  features: string[]
  popular?: boolean
}

export default function PaymentPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [currentMembership, setCurrentMembership] = useState<any>(null)

  useEffect(() => {
    loadPlans()
    loadCurrentMembership()
  }, [])

  const loadPlans = async () => {
    try {
      const res = await apiClient.get('/payment/plans')
      setPlans(res.data.plans)
      if (res.data.plans.length > 0) {
        setSelectedPlan(res.data.plans[0].id)
      }
    } catch (error) {
      console.error('加载套餐失败', error)
      message.error('加载套餐失败')
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentMembership = async () => {
    try {
      const res = await apiClient.get('/payment/current-membership')
      setCurrentMembership(res.data)
    } catch (error) {
      console.error('获取当前会员信息失败', error)
    }
  }

  const handlePurchase = async () => {
    if (!selectedPlan) {
      message.warning('请选择一个套餐')
      return
    }

    const plan = plans.find(p => p.id === selectedPlan)
    if (!plan) {
      message.error('未找到该套餐')
      return
    }

    try {
      // 这里实际项目中可以跳转到支付页面或调用支付接口
      message.info(`即将购买${plan.display_name}，价格 ¥${plan.price}`)
      // TODO: 实际支付逻辑需要对接支付网关
      // 比如微信支付、支付宝等，这里先留空
    } catch (error) {
      console.error('购买失败', error)
      message.error('购买失败，请重试')
    }
  }

  if (loading) {
    return (
      <div className="payment-loading">
        <Spin size="large" />
        <div>正在加载套餐...</div>
      </div>
    )
  }

  return (
    <div className="payment-container">
      {currentMembership && currentMembership.level !== 'free' && (
        <Card className="current-membership" size="small">
          <div className="current-info">
            <span className="member-tag">当前会员</span>
            <h3>{currentMembership.plan_name}</h3>
            <p className="expire-date">
              有效期至：{currentMembership.expires_at}
            </p>
          </div>
        </Card>
      )}

      <div className="plans-container">
        <h2 className="section-title">选择会员套餐</h2>
        <div className="plans-list">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`plan-card ${selectedPlan === plan.id ? 'selected' : ''} ${plan.popular ? 'popular' : ''}`}
              hoverable
              onClick={() => setSelectedPlan(plan.id)}
            >
              {plan.popular && (
                <Tag color="orange" className="popular-tag">
                推荐
              </Tag>
              )}
              <div className="plan-header">
                <CrownOutlined className="plan-icon" />
                <h3>{plan.display_name}</h3>
                <div className="price">
                  <span className="currency">¥</span>
                  <span className="amount">{plan.price}</span>
                </div>
                <div className="duration">
                  {plan.duration_days >= 365 ? '全年' :
                   plan.duration_days >= 30 ? `${Math.round(plan.duration_days / 30)}月 : `${plan.duration_days}天`}
                </div>
              </div>

              <List
                dataSource={plan.features}
                size="small"
                renderItem={(feature) => (
                  <List.Item>
                    <CheckOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                    {feature}
                  </List.Item>
                )}
              />

              {selectedPlan === plan.id && (
                <div className="selected-indicator">
                  <CheckOutlined /> 已选择
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>

      <div className="payment-footer">
        {selectedPlan && (
          <Button
            type="primary"
            size="large"
            block
            onClick={handlePurchase}
          >
            立即开通 {plans.find(p => p.id === selectedPlan)?.price > 0 ?
              `¥${plans.find(p => p.id === selectedPlan)?.price}` : ''}
          </Button>
        )}
        {selectedPlan && plans.find(p => p.id === selectedPlan)?.price > 0 && (
          <p className="payment-note">
            开通即表示你同意我们的服务条款和隐私政策
          </p>
        )}
      </div>
    </div>
  )
}
