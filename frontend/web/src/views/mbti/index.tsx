import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Radio, Progress, Spin, App } from 'antd'
import { api } from '../../api/request'
import { useMbtiStore, useAuthStore } from '../../stores'
import { useTheme } from '../../hooks/useTheme'

export default function MbtiTest() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const { isAuthenticated } = useAuthStore()
  const {
    questions,
    currentQuestionIndex,
    answers,
    result,
    loading,
    setQuestions,
    addAnswer,
    setResult,
    setLoading,
    reset,
  } = useMbtiStore()
  const { themeColors, themeColor } = useTheme()

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const res = await api.mbti.questions()
      setQuestions(res.questions || [])
    } catch (error) {
      console.error('加载题目失败:', error)
      // 后端服务不可用时，使用空数组作为默认题目数据
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = (answer: string) => {
    if (questions.length === 0) return
    
    // 确保currentQuestionIndex在有效范围内
    if (currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
      console.error('无效的题目索引:', currentQuestionIndex)
      return
    }
    
    const currentQuestion = questions[currentQuestionIndex]
    if (currentQuestion) {
      const isLastQuestion = currentQuestionIndex === questions.length - 1
      
      // 先添加答案到store
      addAnswer({ question_id: currentQuestion.id, answer })
      
      if (isLastQuestion) {
        // 先检查是否已登录
        if (!isAuthenticated) {
          message.warning('请先登录')
          // 保存当前路径，登录成功后重定向回来
          localStorage.setItem('redirectPath', '/mbti')
          navigate('/login')
          return
        }
        // 延迟调用handleSubmit，确保状态已更新
        setTimeout(() => {
          handleSubmit()
        }, 0)
      }
    }
  }

  const handleSubmit = async (_event?: any, submitAnswers?: typeof answers) => {
    if (questions.length === 0) return
    
    // 先检查是否已登录
    if (!isAuthenticated) {
      message.warning('请先登录')
      // 保存当前路径，登录成功后重定向回来
      localStorage.setItem('redirectPath', '/mbti')
      navigate('/login')
      return
    }
    
    // 直接使用组件中从store获取的answers
    const answersToSubmit = submitAnswers || answers
    
    // 去重，确保每个题目只有一个答案
    const uniqueAnswers = answersToSubmit.reduce((acc: typeof answers, answer) => {
      if (!acc.some(a => a.question_id === answer.question_id)) {
        acc.push(answer)
      }
      return acc
    }, [])
    
    if (uniqueAnswers.length < questions.length) {
      console.warn('请完成所有题目')
      message.warning('请完成所有题目')
      return
    }

    setSubmitting(true)
    try {
      const res = await api.mbti.submit(uniqueAnswers)
      console.log('提交结果:', res)
      // 检查响应是否有效
      if (res && typeof res === 'object') {
        if (res.id) {
          setResult(res)
          navigate('/mbti/result')
        } else if (res.detail) {
          // 服务器返回错误信息
          console.error('提交失败，服务器返回错误:', res.detail)
          message.error(`提交失败: ${res.detail}`)
        } else {
          console.error('提交失败，服务器返回无效结果:', res)
          message.error('提交失败，请稍后重试')
        }
      } else {
        console.error('提交失败，服务器返回无效响应:', res)
        message.error('提交失败，请稍后重试')
      }
    } catch (error: any) {
      console.error('提交失败:', error)
      // 检查是否是网络错误
      if (error.message && error.message.includes('Network Error')) {
        message.error('网络连接失败，请检查网络设置后重试')
      } else if (error.response) {
        // 服务器返回错误
        console.error('服务器错误:', error.response)
        message.error(`提交失败: ${error.response.data?.detail || '服务器内部错误'}`)
      } else {
        message.error('提交失败，请稍后重试')
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  // 当题目列表为空时，显示友好提示
  if (questions.length === 0) {
    return (
      <div style={{ minHeight: '100vh', background: '#f5f5f5', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Card style={{ 
          maxWidth: 600, 
          margin: '0 auto',
          borderRadius: '12px',
          border: 'none',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
          textAlign: 'center',
          padding: '40px'
        }}>
          <h2 style={{ fontSize: 24, marginBottom: 16, color: themeColors[themeColor] }}>
            服务暂时不可用
          </h2>
          <p style={{ fontSize: 16, color: '#6b7280', marginBottom: 32 }}>
            抱歉，MBTI测试服务暂时无法使用，请稍后再试
          </p>
          <Link to="/">
            <Button
              type="primary"
              style={{ 
                background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                border: 'none',
                borderRadius: '8px',
                padding: '0 24px'
              }}
            >
              返回首页
            </Button>
          </Link>
        </Card>
      </div>
    )
  }

  // 确保currentQuestionIndex在有效范围内
  const safeQuestionIndex = Math.max(0, Math.min(currentQuestionIndex, questions.length - 1))
  const currentQuestion = questions[safeQuestionIndex]
  const progress = questions.length > 0 ? ((safeQuestionIndex + 1) / questions.length) * 100 : 0

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        background: '#fff',
        padding: '16px 0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/" style={{ fontSize: 20, color: themeColors[themeColor], fontWeight: 'bold' }}>
            心灵伴侣AI
          </Link>
          <div>
            <span style={{ color: '#8c8c8c', marginRight: 16 }}>
              第 {currentQuestionIndex + 1} / {questions.length} 题
            </span>
          </div>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        <Card style={{ 
          maxWidth: 600, 
          margin: '0 auto',
          borderRadius: '12px',
          border: 'none',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)'
        }}>
          {/* Progress */}
          <Progress
            percent={progress}
            showInfo={false}
            strokeColor={themeColors[themeColor]}
            trailColor="#f0f0f0"
            style={{ marginBottom: 32 }}
          />

          {/* Question */}
          {currentQuestion && (
            <div className="fade-in">
              <h2 style={{ fontSize: 20, marginBottom: 32, textAlign: 'center', lineHeight: 1.6 }}>
                {currentQuestion.question_text}
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Button
                  size="large"
                  style={{
                    height: 60,
                    fontSize: 16,
                    borderColor: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'A' ? themeColors[themeColor] : '#d9d9d9',
                    background: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'A' ? `${themeColors[themeColor]}10` : '#fff',
                    borderRadius: '8px',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => handleAnswer('A')}
                >
                  A. {currentQuestion.option_a || ''}
                </Button>
                <Button
                  size="large"
                  style={{
                    height: 60,
                    fontSize: 16,
                    borderColor: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'B' ? themeColors[themeColor] : '#d9d9d9',
                    background: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'B' ? `${themeColors[themeColor]}10` : '#fff',
                    borderRadius: '8px',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => handleAnswer('B')}
                >
                  B. {currentQuestion.option_b || ''}
                </Button>
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={currentQuestionIndex === 0}
              onClick={() => {
                const store = useMbtiStore.getState()
                store.setCurrentIndex(currentQuestionIndex - 1)
              }}
              style={{ borderRadius: '8px' }}
            >
              上一题
            </Button>
            {currentQuestionIndex === questions.length - 1 && (
              <Button
                type="primary"
                loading={submitting}
                onClick={() => handleSubmit()}
                style={{ 
                  background: `linear-gradient(135deg, ${themeColors[themeColor]} 0%, ${themeColors[themeColor]}dd 100%)`,
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0 24px'
                }}
              >
                提交结果
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}