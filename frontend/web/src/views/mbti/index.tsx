import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Radio, Progress, Spin, App } from 'antd'
import { api } from '../../api/request'
import { useMbtiStore } from '../../stores'

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

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const res = await api.mbti.questions()
      setQuestions(res.questions)
    } catch (error) {
      message.error('加载题目失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = (answer: string) => {
    const currentQuestion = questions[currentQuestionIndex]
    if (currentQuestion) {
      const isLastQuestion = currentQuestionIndex === questions.length - 1
      
      if (isLastQuestion) {
        const finalAnswers = [...answers, { question_id: currentQuestion.id, answer }]
        handleSubmit(finalAnswers)
      } else {
        addAnswer({ question_id: currentQuestion.id, answer })
      }
    }
  }

  const handleSubmit = async (_event?: any, submitAnswers?: typeof answers) => {
    const answersToSubmit = submitAnswers || answers
    
    // 去重，确保每个题目只有一个答案
    const uniqueAnswers = answersToSubmit.reduce((acc: typeof answers, answer) => {
      if (!acc.some(a => a.question_id === answer.question_id)) {
        acc.push(answer)
      }
      return acc
    }, [])
    
    if (uniqueAnswers.length < questions.length) {
      message.warning('请完成所有题目')
      return
    }

    setSubmitting(true)
    try {
      const res = await api.mbti.submit(uniqueAnswers)
      setResult(res)
      message.success('测试完成！')
      navigate('/mbti/result')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '提交失败')
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
          <Link to="/" style={{ fontSize: 20, color: '#722ed1', fontWeight: 'bold' }}>
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
        <Card style={{ maxWidth: 600, margin: '0 auto' }}>
          {/* Progress */}
          <Progress
            percent={progress}
            showInfo={false}
            strokeColor="#722ed1"
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
                    borderColor: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'A' ? '#722ed1' : '#d9d9d9',
                    background: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'A' ? '#f0f5ff' : '#fff',
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
                    borderColor: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'B' ? '#722ed1' : '#d9d9d9',
                    background: answers.find(a => a.question_id === currentQuestion.id)?.answer === 'B' ? '#f0f5ff' : '#fff',
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
            >
              上一题
            </Button>
            {currentQuestionIndex === questions.length - 1 && (
              <Button
                type="primary"
                loading={submitting}
                onClick={() => handleSubmit()}
                style={{ background: '#722ed1' }}
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