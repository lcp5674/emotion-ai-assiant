/**
 * 首次使用引导页
 * 帮助新用户快速了解产品功能，完成首次测评
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Card, Steps, Space, Typography, Avatar, Result, Progress } from 'antd'
import {
  UserOutlined,
  TrophyOutlined,
  BookOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../stores'
import { apiClient } from '../../api/request'
import './index.css'

const { Title, Text, Paragraph } = Typography

const steps = [
  {
    title: '欢迎加入',
    description: '情感AI助手，陪伴你探索内心世界',
    icon: <UserOutlined />,
    content: (
      <div className="onboarding-welcome">
        <div className="welcome-icon">💖</div>
        <Title level={2}>欢迎来到情感AI助手</Title>
        <Paragraph>
          这是一个专注于情感陪伴和个人成长的AI助手。我们将帮助你：
        </Paragraph>
        <ul>
          <li>🗓️ 记录每日心情，追踪情绪变化</li>
          <li>🤖 随时倾诉，获得专业的情感支持</li>
          <li>📊 三大测评，全面了解自己</li>
          <li>🌱 在交流中持续成长，成为更好的自己</li>
        </ul>
      </div>
    ),
  },
  {
    title: 'MBTI测评',
    description: '完成48道人格测试',
    icon: <TrophyOutlined />,
    content: (
      <div className="onboarding-step">
        <BookOutlined className="step-icon" />
        <Title level={3}>MBTI人格测评</Title>
        <Paragraph>
          通过48道题目，了解你的性格特点，为你匹配最适合的AI助手风格。
        </Paragraph>
        <Text type="secondary">
          约5分钟，准备好了吗？
        </Text>
      </div>
    ),
  },
  {
    title: 'SBTI测评',
    description: '完成48道才干测试',
    icon: <TrophyOutlined />,
    content: (
      <div className="onboarding-step">
        <BookOutlined className="step-icon" />
        <Title level={3}>SBTI才干测评</Title>
        <Paragraph>
          发现你的核心才干，了解自己在关系中的优势与成长点。
        </Paragraph>
        <Text type="secondary">
          约5分钟，这是了解自己的第二步
        </Text>
      </div>
    ),
  },
  {
    title: '依恋测评',
    description: '完成10道依恋测试',
    icon: <TrophyOutlined />,
    content: (
      <div className="onboarding-step">
        <BookOutlined className="step-icon" />
        <Title level={3}>依恋风格测评</Title>
        <Paragraph>
          了解你在亲密关系中的依恋风格，帮你更好地理解和经营关系。
        </Paragraph>
        <Text type="secondary">
          约3分钟，这是了解自己的第三步
        </Text>
      </div>
    ),
  },
  {
    title: '开始倾诉',
    description: '写下你的第一篇日记',
    icon: <BookOutlined />,
    content: (
      <div className="onboarding-step">
        <MessageOutlined className="step-icon" />
        <Title level={3}>记录你的心情</Title>
        <Paragraph>
          养成记录情绪的习惯，是自我觉察的第一步。写下你今天的感受。
        </Paragraph>
        <Text type="secondary">
          日记内容完全私密，只有你自己可以查看。
        </Text>
      </div>
    ),
  },
  {
    title: '开始对话',
    description: '与AI助手开始对话',
    icon: <MessageOutlined />,
    content: (
      <div className="onboarding-step">
        <MessageOutlined className="step-icon" />
        <Title level={3}>开始对话</Title>
        <Paragraph>
          现在，你可以随时和AI助手聊天了。无论是开心还是难过，我们都在这里。
        </Paragraph>
        <Text type="secondary">
          真诚的交流，带来真实的成长。
        </Text>
      </div>
    ),
  },
  {
    title: '完成',
    description: '准备好了，开始你的旅程',
    icon: <CheckCircleOutlined />,
    content: (
      <Result
        status="success"
        title="引导完成！"
        subTitle="你已完成全部三大测评，现在可以开始使用情感AI助手了。"
        extra={
          <Button type="primary" size="large" icon={<ArrowRightOutlined />}>
            开始使用
          </Button>
        }
      />
    ),
  },
]

export default function OnboardingPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [current, setCurrent] = useState(0)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<any>(null)

  useEffect(() => {
    // 获取当前引导状态
    if (user) {
      fetchOnboardingStatus()
    }
  }, [user])

  const fetchOnboardingStatus = async () => {
    try {
      const res = await apiClient.get('/user/onboarding-status')
      setStatus(res.data)
      if (res.data.has_completed_onboarding) {
        // 如果已经完成，直接跳转到首页
        navigate('/')
      }
    } catch (error) {
      console.error('获取引导状态失败', error)
    }
  }

  const next = () => {
    if (current === steps.length - 1) {
      // 完成引导
      completeOnboarding()
    } else {
      setCurrent(current + 1)
    }
  }

  const prev = () => {
    setCurrent(current - 1)
  }

  const completeOnboarding = async () => {
    setLoading(true)
    try {
      await apiClient.post('/user/mark-onboarding-step', { step: 'completed' })
      navigate('/')
    } catch (error) {
      console.error('完成引导失败', error)
    } finally {
      setLoading(false)
    }
  }

  const goToMbti = () => {
    navigate('/mbti')
  }

  const goToSbti = () => {
    navigate('/sbti')
  }

  const goToAttachment = () => {
    navigate('/attachment')
  }

  const goToCreateDiary = () => {
    navigate('/diary/create')
  }

  const goToChat = () => {
    navigate('/chat')
  }

  const isLastStep = current === steps.length - 1

  const getActionButtons = () => {
    if (current === 1) {
      return (
        <Space>
          {current > 0 && (
            <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
              上一步
            </Button>
          )}
          <Button type="primary" size="large" onClick={goToMbti}>
            开始MBTI {<ArrowRightOutlined />}
          </Button>
        </Space>
      )
    }

    if (current === 2) {
      return (
        <Space>
          {current > 0 && (
            <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
              上一步
            </Button>
          )}
          <Button type="primary" size="large" onClick={goToSbti}>
            开始SBTI {<ArrowRightOutlined />}
          </Button>
        </Space>
      )
    }

    if (current === 3) {
      return (
        <Space>
          {current > 0 && (
            <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
              上一步
            </Button>
          )}
          <Button type="primary" size="large" onClick={goToAttachment}>
            开始依恋 {<ArrowRightOutlined />}
          </Button>
        </Space>
      )
    }

    if (current === 4) {
      return (
        <Space>
          {current > 0 && (
            <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
              上一步
            </Button>
          )}
          <Button type="primary" size="large" onClick={goToCreateDiary}>
            写日记 {<ArrowRightOutlined />}
          </Button>
        </Space>
      )
    }

    if (current === 5) {
      return (
        <Space>
          {current > 0 && (
            <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
              上一步
            </Button>
          )}
          <Button type="primary" size="large" onClick={goToChat}>
            开始聊天 {<ArrowRightOutlined />}
          </Button>
        </Space>
      )
    }

    return (
      <Space>
        {current > 0 && (
          <Button size="large" onClick={prev} icon={<ArrowLeftOutlined />}>
            上一步
          </Button>
        )}
        <Button
          type="primary"
          size="large"
          onClick={next}
          loading={loading}
          icon={isLastStep ? <CheckCircleOutlined /> : <ArrowRightOutlined />}
        >
          {isLastStep ? '完成' : '下一步'}
        </Button>
      </Space>
    )
  }

  return (
    <div className="onboarding-container">
      <Card className="onboarding-card">
        <div className="onboarding-header">
          <Avatar size={64} icon={<UserOutlined />} />
          <Title level={2} style={{ margin: '16px 0 0 0' }}>
            欢迎新旅程
          </Title>
          {status && (
            <div className="progress-wrapper">
              <Text>完成进度</Text>
              <Progress
                percent={status && status.steps ? 
                  Object.values(status.steps).filter(Boolean).length * (100 / 4) : 0}
                format={(percent) => `${Math.round(percent)}%`}
              />
            </div>
          )}
        </div>

        <Steps
          current={current}
          items={steps.map(item => ({
            title: item.title,
            description: item.description,
            icon: item.icon,
          }))}
          direction="horizontal"
          className="onboarding-steps"
        />

        <div className="onboarding-content">
          {steps[current].content}
        </div>

        <div className="onboarding-footer">
          {getActionButtons()}
        </div>
      </Card>
    </div>
  )
}
