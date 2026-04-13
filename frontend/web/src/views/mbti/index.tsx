import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Radio, Progress, Spin, App } from 'antd'
import { api } from '../../api/request'
import { useMbtiStore } from '../../stores'
import { useTheme } from '../../hooks/useTheme'

export default function MbtiTest() {
  const navigate = useNavigate()
  const { message } = App.useApp()
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
    
    const currentQuestion = questions[currentQuestionIndex]
    if (currentQuestion) {
      const isLastQuestion = currentQuestionIndex === questions.length - 1
      
      // 先添加答案到store
      addAnswer({ question_id: currentQuestion.id, answer })
      
      if (isLastQuestion) {
        // 直接调用handleSubmit，让它从store获取最新的answers
        handleSubmit()
      }
    }
  }

  const handleSubmit = async (_event?: any, submitAnswers?: typeof answers) => {
    if (questions.length === 0) return
    
    // 总是从store获取最新的answers
    const store = useMbtiStore.getState()
    const answersToSubmit = submitAnswers || store.answers
    
    // 去重，确保每个题目只有一个答案
    const uniqueAnswers = answersToSubmit.reduce((acc: typeof answers, answer) => {
      if (!acc.some(a => a.question_id === answer.question_id)) {
        acc.push(answer)
      }
      return acc
    }, [])
    
    if (uniqueAnswers.length < questions.length) {
      console.warn('请完成所有题目')
      return
    }

    setSubmitting(true)
    try {
      const res = await api.mbti.submit(uniqueAnswers)
      if (res && res.id) {
        setResult(res)
        navigate('/mbti/result')
      } else {
        // 如果没有返回结果，可能是未登录或其他错误
        console.warn('提交失败，可能是未登录或服务器错误')
        // 检查是否已登录
        const authStore = useAuthStore.getState()
        if (!authStore.isAuthenticated) {
          navigate('/login')
        }
      }
    } catch (error: any) {
      console.error('提交失败:', error)
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

  const currentQuestion = questions[currentQuestionIndex]
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0

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
                  A. {currentQuestion.option_a}
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
                  B. {currentQuestion.option_b}
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