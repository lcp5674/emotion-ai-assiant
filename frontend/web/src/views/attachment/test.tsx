import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Button, Progress, Spin, App, Slider } from 'antd'
import { HeartOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useAttachmentStore } from '../../stores'

export default function AttachmentTest() {
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
  } = useAttachmentStore()

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const res = await api.attachment.questions()
      setQuestions(res.questions || [])
    } catch (error) {
      message.error('加载题目失败')
    } finally {
      setLoading(false)
    }
  }

  const handleScoreChange = (score: number) => {
    const currentQuestion = questions[currentQuestionIndex]
    if (currentQuestion) {
      addAnswer({ question_id: currentQuestion.id, score })
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
      const res = await api.attachment.submit(uniqueAnswers)
      setResult(res)
      message.success('测评完成！')
      navigate('/attachment/result')
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
  const currentAnswer = answers.find(a => a.question_id === currentQuestion?.id)?.score

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
          <Link to="/attachment" style={{ fontSize: 20, color: '#eb2f96', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 8 }}>
            <HeartOutlined /> 依恋风格测评
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
            strokeColor="#eb2f96"
            trailColor="#f0f0f0"
            style={{ marginBottom: 32 }}
          />

          {/* Question */}
          {currentQuestion && (
            <div className="fade-in">
              <h2 style={{ fontSize: 20, marginBottom: 32, textAlign: 'center', lineHeight: 1.6 }}>
                {currentQuestion.question_text}
              </h2>

              <div style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ color: '#8c8c8c' }}>{currentQuestion.scale_min_label}</span>
                  <span style={{ color: '#eb2f96', fontWeight: 'bold' }}>
                    {currentAnswer || '未选择'}
                  </span>
                  <span style={{ color: '#8c8c8c' }}>{currentQuestion.scale_max_label}</span>
                </div>
                <Slider
                  min={currentQuestion.scale_min}
                  max={currentQuestion.scale_max}
                  value={currentAnswer || currentQuestion.scale_min}
                  onChange={handleScoreChange}
                  tooltip={{
                    formatter: (value) => `${value}`,
                  }}
                  marks={{
                    [currentQuestion.scale_min]: `${currentQuestion.scale_min}`,
                    [Math.floor((currentQuestion.scale_min + currentQuestion.scale_max) / 2)]: `${Math.floor((currentQuestion.scale_min + currentQuestion.scale_max) / 2)}`,
                    [currentQuestion.scale_max]: `${currentQuestion.scale_max}`,
                  }}
                  styles={{
                    track: { background: '#eb2f96' },
                    rail: { background: '#f0f0f0' },
                    handle: { borderColor: '#eb2f96', background: '#eb2f96' },
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ color: '#8c8c8c', fontSize: 12 }}>
                  1 = 完全不符合，7 = 完全符合
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={currentQuestionIndex === 0}
              onClick={() => useAttachmentStore.getState().setCurrentIndex(currentQuestionIndex - 1)}
            >
              上一题
            </Button>
            {currentQuestionIndex === questions.length - 1 ? (
              <Button
                type="primary"
                loading={submitting}
                onClick={handleSubmit}
                style={{ background: '#eb2f96' }}
                disabled={answers.length < questions.length}
              >
                提交结果
              </Button>
            ) : (
              <Button
                type="primary"
                onClick={() => useAttachmentStore.getState().setCurrentIndex(currentQuestionIndex + 1)}
                style={{ background: '#eb2f96' }}
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
                  ? '#eb2f96'
                  : '#d9d9d9',
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
