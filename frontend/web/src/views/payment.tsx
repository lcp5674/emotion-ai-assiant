/**
 * 会员支付页面
 * 展示会员套餐，支持购买
 */
import { useEffect, useState } from 'react'
import { Card, Button, List, Tag, Radio, Space, message, Spin } from 'antd'
import { CheckOutlined, CrownOutlined } from '@ant-design/icons'
import { apiClient } from '../api/request'
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
      // 优先从member接口获取套餐
      let res
      try {
        res = await apiClient.get('/member/prices')
        if (res.list && res.list.length > 0) {
          // 转换为Payment页面需要的格式
          setPlans(res.list.map(p => ({
            id: p.level,
            name: p.name,
            display_name: p.name,
            description: p.description || '',
            price: p.price / 100, // 分转元
            duration_days: p.duration,
            features: p.features || [],
            popular: p.level === 'svip',
          })))
          if (res.list.length > 0) {
            setSelectedPlan(res.list[0].level)
          }
          setLoading(false)
          return
        }
      } catch (e) {
        console.log('member接口不可用，使用payment接口')
      }
      
      // 备用：从payment接口获取
      res = await apiClient.get('/payment/plans')
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
      message.info(`正在创建订单...`)
      
      // 调用支付宝网页支付接口
      const res = await apiClient.post('/payment/alipay/page', {
        level: selectedPlan,
      })
      
      if (res.data.pay_url) {
        // 跳转到支付页面
        window.location.href = res.data.pay_url
      } else {
        message.error('支付页面创建失败')
      }
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

      <div className="benefits-comparison">
        <h3>免费 vs VIP 权益对比</h3>
        <div className="benefit-row">
          <span className="benefit-label">每日对话次数</span>
          <span className="benefit-free">10次/天</span>
          <span className="benefit-vip">无限次</span>
        </div>
        <div className="benefit-row">
          <span className="benefit-label">AI模型</span>
          <span className="benefit-free">基础版</span>
          <span className="benefit-vip">GPT-4/Claude</span>
        </div>
        <div className="benefit-row">
          <span className="benefit-label">深度人格分析</span>
          <span className="benefit-free">-</span>
          <span className="benefit-vip">✅ 完整版</span>
        </div>
        <div className="benefit-row">
          <span className="benefit-label">情感日记分析</span>
          <span className="benefit-free">基础统计</span>
          <span className="benefit-vip">AI智能分析</span>
        </div>
        <div className="benefit-row">
          <span className="benefit-label">专属徽章</span>
          <span className="benefit-free">-</span>
          <span className="benefit-vip">守护天使</span>
        </div>
        <div className="benefit-row">
          <span className="benefit-label">Live2D动画</span>
          <span className="benefit-free">基础</span>
          <span className="benefit-vip">情绪响应</span>
        </div>
      </div>

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
                   plan.duration_days >= 30 ? `${Math.round(plan.duration_days / 30)}月` : `${plan.duration_days}天`}
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
