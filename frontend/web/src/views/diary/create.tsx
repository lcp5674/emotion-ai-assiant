import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  Button,
  DatePicker,
  Slider,
  Select,
  Space,
  Divider,
  Spin,
  App,
  Row,
  Col,
  message as antMessage,
} from 'antd'
import {
  CalendarOutlined,
  SmileOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { api } from '../../api/request'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select

interface MoodOption {
  value: string
  label: string
  icon: string
  color: string
}

interface EmotionOption {
  value: string
  label: string
  icon: string
  color: string
}

const MOOD_OPTIONS: MoodOption[] = [
  { value: 'terrible', label: '糟糕', icon: '😢', color: '#ff4d4f' },
  { value: 'bad', label: '不好', icon: '😔', color: '#fa8c16' },
  { value: 'neutral', label: '一般', icon: '😐', color: '#faad14' },
  { value: 'good', label: '不错', icon: '🙂', color: '#52c41a' },
  { value: 'excellent', label: '很棒', icon: '😄', color: '#1890ff' },
]

const EMOTION_OPTIONS: EmotionOption[] = [
  { value: 'happy', label: '开心', icon: '😊', color: '#FFD700' },
  { value: 'sad', label: '难过', icon: '😢', color: '#A29BFE' },
  { value: 'angry', label: '生气', icon: '😠', color: '#FF4757' },
  { value: 'calm', label: '平静', icon: '😌', color: '#74B9FF' },
  { value: 'excited', label: '兴奋', icon: '🎉', color: '#FF6B6B' },
  { value: 'anxious', label: '焦虑', icon: '😰', color: '#FD79A8' },
  { value: 'confused', label: '困惑', icon: '😕', color: '#00CEC9' },
  { value: 'surprised', label: '惊讶', icon: '😮', color: '#EB2F96' },
]

const CATEGORIES = ['工作', '学习', '生活', '情感', '健康', '其他']

export default function DiaryCreate() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [isEdit, setIsEdit] = useState(false)
  const [tags, setTags] = useState<{ id: number; name: string; color?: string }[]>([])
  const [tagInputVisible, setTagInputVisible] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagColor, setNewTagColor] = useState('#722ed1')

  const getMoodIcon = (score: number) => {
    if (score >= 8) return <SmileOutlined style={{ color: '#52c41a' }} />
    if (score >= 6) return <SmileOutlined style={{ color: '#faad14' }} />
    if (score >= 4) return <SmileOutlined style={{ color: '#fa8c16' }} />
    return <SmileOutlined style={{ color: '#ff4d4f' }} />
  }

  useEffect(() => {
    if (id) {
      setIsEdit(true)
      loadDiary(parseInt(id))
    } else {
      form.setFieldValue('date', dayjs())
      form.setFieldValue('mood_score', 5)
    }
    loadTags()
  }, [id])

  const loadDiary = async (diaryId: number) => {
    setLoading(true)
    try {
      const res = await api.diary.get(diaryId)
      form.setFieldsValue({
        date: dayjs(res.date),
        mood_score: res.mood_score,
        mood_level: res.mood_level,
        primary_emotion: res.primary_emotion,
        content: res.content,
        category: res.category,
        tags: res.tags ? res.tags.split(',').filter(Boolean) : [],
      })
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '加载日记失败')
    } finally {
      setLoading(false)
    }
  }

  const loadTags = async () => {
    try {
      const res = await api.diary.listTags()
      setTags(res || [])
    } catch (error) {
      console.error(error)
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      message.warning('请输入标签名称')
      return
    }
    try {
      const res = await api.diary.createTag({ name: newTagName.trim(), color: newTagColor })
      setTags([...tags, res])
      form.setFieldValue('tags', [...(form.getFieldValue('tags') || []), newTagName.trim()])
      setNewTagName('')
      setTagInputVisible(false)
      message.success('标签创建成功')
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '创建标签失败')
    }
  }

  const handleDeleteTag = async (tagId: number) => {
    try {
      await api.diary.deleteTag(tagId)
      setTags(tags.filter(t => t.id !== tagId))
      message.success('标签已删除')
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '删除标签失败')
    }
  }

  const handleSubmit = async (values: any) => {
    setLoading(true)

    const data = {
      ...values,
      date: values.date.format('YYYY-MM-DD'),
      tags: Array.isArray(values.tags) ? values.tags.join(',') : '',
    }

    try {
      if (isEdit && id) {
        await api.diary.update(parseInt(id), data)
        message.success('更新成功')
      } else {
        await api.diary.create(data)
        message.success('创建成功')
      }
      navigate('/diary')
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '操作失败')
    } finally {
      setLoading(false)
    }
  }

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
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/diary')}
          >
            回到列表
          </Button>
        </div>
      </header>

      <div className="container" style={{ padding: '40px 16px' }}>
        <Card>
          <Spin spinning={loading}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                date: dayjs(),
                mood_score: 5,
                tags: [],
              }}
            >
              {/* 日期 */}
              <Form.Item
                name="date"
                label="日期"
                rules={[{ required: true, message: '请选择日期' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  disabledDate={(current) =>
                    current && (current > dayjs() || current < dayjs().subtract(10, 'year'))
                  }
                />
              </Form.Item>

              <Divider />

              {/* 心情评分 */}
              <Form.Item
                name="mood_score"
                label="心情评分"
                rules={[{ required: true, message: '请评分' }]}
              >
                <div>
                  <Slider
                    min={1}
                    max={10}
                    marks={{
                      1: '😢',
                      5: '😐',
                      10: '😄',
                    }}
                    tipFormatter={(value) => {
                      return (
                        <span style={{ fontSize: '14px', whiteSpace: 'nowrap' }}>
                          {value}分 {value >= 8 ? '很棒' : value >= 6 ? '不错' : value >= 4 ? '一般' : value >= 2 ? '不好' : '糟糕'}
                        </span>
                      )
                    }}
                  />
                  <div style={{ textAlign: 'center', marginTop: 16 }}>
                    <span style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                      {form.getFieldValue('mood_score') || 5}分
                    </span>
                    <span style={{ marginLeft: 16, color: '#8c8c8c' }}>
                      {getMoodIcon(form.getFieldValue('mood_score') || 5)}
                    </span>
                  </div>
                </div>
              </Form.Item>

              {/* 心情等级 */}
              <Form.Item
                name="mood_level"
                label="心情等级"
              >
                <Select placeholder="选择心情等级">
                  {MOOD_OPTIONS.map((option) => (
                    <Option key={option.value} value={option.value}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ color: option.color }}>{option.icon}</span>
                        <span>{option.label}</span>
                      </span>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Divider />

              {/* 情绪 */}
              <Form.Item
                name="primary_emotion"
                label="主要情绪"
              >
                <Select placeholder="选择主要情绪" showSearch>
                  {EMOTION_OPTIONS.map((option) => (
                    <Option key={option.value} value={option.value}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ color: option.color }}>{option.icon}</span>
                        <span>{option.label}</span>
                      </span>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Divider />

              {/* 内容 */}
              <Form.Item
                name="content"
                label="日记内容"
                rules={[{ required: true, message: '请输入日记内容' }, { min: 10, message: '日记内容至少10个字符' }]}
              >
                <TextArea
                  rows={8}
                  placeholder="写下今天的心情和感受..."
                  showCount
                  maxLength={5000}
                  style={{
                    resize: 'vertical',
                    fontSize: '16px',
                    lineHeight: 1.6,
                  }}
                />
              </Form.Item>

              {/* 分类和标签 */}
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="category"
                    label="分类"
                  >
                    <Select placeholder="选择分类" style={{ width: '100%' }}>
                      {CATEGORIES.map((category) => (
                        <Option key={category} value={category}>
                          {category}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="tags"
                    label="标签"
                  >
                    <Select
                      placeholder="选择或创建标签"
                      style={{ width: '100%' }}
                      mode="multiple"
                      dropdownRender={(menu) => (
                        <>
                          {menu}
                          <Divider style={{ margin: '8px 0' }} />
                          {tagInputVisible ? (
                            <div style={{ padding: '4px 8px', display: 'flex', gap: 8, alignItems: 'center' }}>
                              <Input
                                placeholder="输入标签名"
                                value={newTagName}
                                onChange={(e) => setNewTagName(e.target.value)}
                                style={{ flex: 1 }}
                                autoFocus
                              />
                              <Button type="primary" size="small" onClick={handleCreateTag}>
                                创建
                              </Button>
                              <Button size="small" onClick={() => setTagInputVisible(false)}>
                                取消
                              </Button>
                            </div>
                          ) : (
                            <Button
                              type="link"
                              block
                              onClick={() => setTagInputVisible(true)}
                              style={{ padding: '4px 8px', textAlign: 'left' }}
                            >
                              + 创建新标签
                            </Button>
                          )}
                        </>
                      )}
                    >
                      {tags.map((tag) => (
                        <Select.Option key={tag.id} value={tag.name}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>
                              <span style={{
                                display: 'inline-block',
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                backgroundColor: tag.color || '#722ed1',
                                marginRight: 8
                              }} />
                              {tag.name}
                            </span>
                          </div>
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              {/* 提交按钮 */}
              <Form.Item>
                <Space style={{ width: '100%', justifyContent: 'center' }}>
                  <Button
                    size="large"
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate('/diary')}
                  >
                    取消
                  </Button>
                  <Button
                    type="primary"
                    size="large"
                    htmlType="submit"
                    style={{ background: '#722ed1', width: 120 }}
                  >
                    {isEdit ? '更新' : '保存'}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Spin>
        </Card>
      </div>
    </div>
  )
}
