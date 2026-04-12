import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Progress, Spin, App, Slider } from 'antd'
import { CrownOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useSbtiStore } from '../../stores'

export default function SbtiTest() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const {
    questions,
    currentQuestionIndex,
    answers,
    loading,
    setQuestions,
    addAnswer,
    setResult,
    setLoading,
  } = useSbtiStore()

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const res = await api.sbti.questions()
      setQuestions(res.questions || [])
    } catch (error) {
      message.error('加载题目失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = (answer: string) => {
    const currentQuestion = questions[currentQuestionIndex]
    if (currentQuestion) {
      addAnswer({ question_id: currentQuestion.id, answer })
    }
  }

  const handleSubmit = async () => {
    // 去重，确保每个题目只有一个答案
    const uniqueAnswers = answers.reduce((acc: typeof answers, answer) => {
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
      const res = await api.sbti.submit(uniqueAnswers)
      setResult(res)
      message.success('测评完成！')
      navigate('/sbti/result')
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
  const currentAnswer = answers.find(a => a.question_id === currentQuestion?.id)?.answer

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
          <Link to="/sbti" style={{ fontSize: 20, color: '#722ed1', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 8 }}>
            <CrownOutlined /> SBTI测评
          </Link>
          <div>
            <span style={{ color: '#8c8c8c', marginRight: 16 }}>
              第 {currentQuestionIndex + 1} / {questions.length} 题
            </span>
          </div>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        <Card style={{ maxWidth: 700, margin: '0 auto' }}>
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
                请选择更符合你的选项：
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Card
                  hoverable
                  onClick={() => handleAnswer('A')}
                  style={{
                    padding: 24,
                    borderColor: currentAnswer === 'A' ? '#722ed1' : '#d9d9d9',
                    background: currentAnswer === 'A' ? '#f0f5ff' : '#fff',
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: 16, lineHeight: 1.6 }}>
                    {currentQuestion.statement_a}
                  </div>
                  <div style={{ marginTop: 8, color: '#8c8c8c', fontSize: 12 }}>
                    {currentQuestion.theme_a}倾向
                  </div>
                </Card>

                <div style={{ textAlign: 'center', color: '#8c8c8c', fontSize: 14 }}>
                  或者
                </div>

                <Card
                  hoverable
                  onClick={() => handleAnswer('B')}
                  style={{
                    padding: 24,
                    borderColor: currentAnswer === 'B' ? '#722ed1' : '#d9d9d9',
                    background: currentAnswer === 'B' ? '#f0f5ff' : '#fff',
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: 16, lineHeight: 1.6 }}>
                    {currentQuestion.statement_b}
                  </div>
                  <div style={{ marginTop: 8, color: '#8c8c8c', fontSize: 12 }}>
                    {currentQuestion.theme_b}倾向
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={currentQuestionIndex === 0}
              onClick={() => useSbtiStore.getState().setCurrentIndex(currentQuestionIndex - 1)}
            >
              上一题
            </Button>
            {currentQuestionIndex === questions.length - 1 ? (
              <Button
                type="primary"
                loading={submitting}
                onClick={handleSubmit}
                style={{ background: '#722ed1' }}
                disabled={answers.length < questions.length}
              >
                提交结果
              </Button>
            ) : (
              <Button
                type="primary"
                onClick={() => useSbtiStore.getState().setCurrentIndex(currentQuestionIndex + 1)}
                style={{ background: '#722ed1' }}
              >
                下一题
              </Button>
            )}
          </div>
        </Card>

        {/* Progress Indicator */}
        <div style={{
          marginTop: 24,
          display: 'flex',
          justifyContent: 'center',
          gap: 4,
          flexWrap: 'wrap',
        }}>
          {questions.map((_, index) => (
            <div
              key={index}
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: answers.some(a => a.question_id === questions[index].id)
                  ? '#722ed1'
                  : '#d9d9d9',
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
