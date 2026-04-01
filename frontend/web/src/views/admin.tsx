import { useEffect, useState } from 'react'
import { Card, Tabs, Form, Input, Select, Button, Table, Tag, Modal, Switch, Space, Popconfirm, Spin, App } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SaveOutlined, ReloadOutlined, ArrowLeftOutlined, ApiOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/request'

interface ConfigData {
  llm_provider: string
  openai_api_key?: string
  openai_model?: string
  openai_base_url?: string
  anthropic_api_key?: string
  anthropic_model?: string
  anthropic_base_url?: string
  glm_api_key?: string
  glm_model?: string
  glm_base_url?: string
  qwen_api_key?: string
  qwen_model?: string
  qwen_base_url?: string
  minimax_api_key?: string
  minimax_model?: string
  minimax_base_url?: string
  ernie_api_key?: string
  ernie_model?: string
  ernie_base_url?: string
  hunyuan_api_key?: string
  hunyuan_model?: string
  hunyuan_base_url?: string
  spark_api_key?: string
  spark_model?: string
  spark_base_url?: string
  doubao_api_key?: string
  doubao_model?: string
  doubao_base_url?: string
  siliconflow_api_key?: string
  siliconflow_model?: string
  siliconflow_base_url?: string
  has_openai_key?: boolean
  has_anthropic_key?: boolean
  has_glm_key?: boolean
  has_qwen_key?: boolean
  has_minimax_key?: boolean
  has_ernie_key?: boolean
  has_hunyuan_key?: boolean
  has_spark_key?: boolean
  has_doubao_key?: boolean
  has_siliconflow_key?: boolean
}

interface Assistant {
  id: number
  name: string
  description?: string
  avatar?: string
  mbti_type: string
  personality?: string
  speaking_style?: string
  expertise?: string
  greeting?: string
  tags?: string[]
  is_active: boolean
  is_recommended?: boolean
  created_at: string
}

const PROVIDERS = [
  { value: 'mock', label: 'Mock (开发测试)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic Claude' },
  { value: 'glm', label: '智谱 GLM' },
  { value: 'qwen', label: '阿里通义千问' },
  { value: 'minimax', label: 'MiniMax' },
  { value: 'ernie', label: '百度文心一言' },
  { value: 'hunyuan', label: '腾讯混元' },
  { value: 'spark', label: '讯飞星火' },
  { value: 'doubao', label: '字节豆包' },
  { value: 'siliconflow', label: '硅基流动' },
]

const MODELS: Record<string, { value: string; label: string }[]> = {
  mock: [{ value: 'mock-gpt-4', label: 'Mock GPT-4' }],
  openai: [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ],
  anthropic: [
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
    { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
  ],
  glm: [
    { value: 'glm-4', label: 'GLM-4' },
    { value: 'glm-4-flash', label: 'GLM-4 Flash' },
    { value: 'glm-4-plus', label: 'GLM-4 Plus' },
    { value: 'glm-3-turbo', label: 'GLM-3 Turbo' },
  ],
  qwen: [
    { value: 'qwen-turbo', label: 'Qwen Turbo' },
    { value: 'qwen-plus', label: 'Qwen Plus' },
    { value: 'qwen-max', label: 'Qwen Max' },
    { value: 'qwen-long', label: 'Qwen Long' },
  ],
  minimax: [
    { value: 'abab6.5s-chat', label: 'Abab 6.5s Chat' },
    { value: 'abab6.5g-chat', label: 'Abab 6.5g Chat' },
    { value: 'abab5.5s-chat', label: 'Abab 5.5s Chat' },
  ],
  ernie: [
    { value: 'ernie-4.0-8k', label: 'ERNIE 4.0 8K' },
    { value: 'ernie-4.0-8k-preview', label: 'ERNIE 4.0 8K Preview' },
    { value: 'ernie-3.5-8k', label: 'ERNIE 3.5 8K' },
    { value: 'ernie-speed-8k', label: 'ERNIE Speed 8K' },
  ],
  hunyuan: [
    { value: 'hunyuan-pro', label: 'Hunyuan Pro' },
    { value: 'hunyuan-standard', label: 'Hunyuan Standard' },
    { value: 'hunyuan-lite', label: 'Hunyuan Lite' },
  ],
  spark: [
    { value: 'spark-v3.5', label: '星火V3.5' },
    { value: 'spark-v3.0', label: '星火V3.0' },
    { value: 'spark-v2.0', label: '星火V2.0' },
    { value: 'spark-v1.5', label: '星火V1.5' },
  ],
  doubao: [
    { value: 'doubao-pro-32k', label: '豆包Pro 32K' },
    { value: 'doubao-pro-128k', label: '豆包Pro 128K' },
    { value: 'doubao-lite-32k', label: '豆包Lite 32K' },
    { value: 'doubao-lite-128k', label: '豆包Lite 128K' },
  ],
  siliconflow: [
    { value: 'Qwen/Qwen2-72B-Instruct', label: 'Qwen2-72B' },
    { value: 'Qwen/Qwen2-7B-Instruct', label: 'Qwen2-7B' },
    { value: 'THUDM/glm-4-9b-chat', label: 'GLM-4-9B' },
    { value: 'THUDM/chatglm3-6b', label: 'ChatGLM3-6B' },
    { value: 'baichuan-inc/Baichuan2-13B-Chat', label: 'Baichuan2-13B' },
    { value: '01-ai/Yi-34B-Chat', label: 'Yi-34B' },
  ],
}

export default function Admin() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [activeTab, setActiveTab] = useState('config')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [config, setConfig] = useState<ConfigData>({
    llm_provider: 'mock',
  })
  const [assistants, setAssistants] = useState<Assistant[]>([])
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAssistant, setEditingAssistant] = useState<Assistant | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadConfig()
    loadAssistants()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const res = await api.admin.config()
      setConfig(res || { llm_provider: 'mock' })
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadAssistants = async () => {
    try {
      setAssistantLoading(true)
      const res = await api.admin.assistants()
      setAssistants(res?.list || res || [])
    } catch (error) {
      console.error(error)
    } finally {
      setAssistantLoading(false)
    }
  }

  const handleSaveConfig = async () => {
    try {
      setSaving(true)
      const updateData: any = {
        llm_provider: config.llm_provider,
      }
      
      if (config.openai_api_key) updateData.openai_api_key = config.openai_api_key
      if (config.openai_model) updateData.openai_model = config.openai_model
      if (config.openai_base_url) updateData.openai_base_url = config.openai_base_url
      if (config.anthropic_api_key) updateData.anthropic_api_key = config.anthropic_api_key
      if (config.anthropic_model) updateData.anthropic_model = config.anthropic_model
      if (config.anthropic_base_url) updateData.anthropic_base_url = config.anthropic_base_url
      if (config.glm_api_key) updateData.glm_api_key = config.glm_api_key
      if (config.glm_model) updateData.glm_model = config.glm_model
      if (config.glm_base_url) updateData.glm_base_url = config.glm_base_url
      if (config.qwen_api_key) updateData.qwen_api_key = config.qwen_api_key
      if (config.qwen_model) updateData.qwen_model = config.qwen_model
      if (config.qwen_base_url) updateData.qwen_base_url = config.qwen_base_url
      if (config.minimax_api_key) updateData.minimax_api_key = config.minimax_api_key
      if (config.minimax_model) updateData.minimax_model = config.minimax_model
      if (config.minimax_base_url) updateData.minimax_base_url = config.minimax_base_url
      if (config.ernie_api_key) updateData.ernie_api_key = config.ernie_api_key
      if (config.ernie_model) updateData.ernie_model = config.ernie_model
      if (config.ernie_base_url) updateData.ernie_base_url = config.ernie_base_url
      if (config.hunyuan_api_key) updateData.hunyuan_api_key = config.hunyuan_api_key
      if (config.hunyuan_model) updateData.hunyuan_model = config.hunyuan_model
      if (config.hunyuan_base_url) updateData.hunyuan_base_url = config.hunyuan_base_url
      if (config.spark_api_key) updateData.spark_api_key = config.spark_api_key
      if (config.spark_model) updateData.spark_model = config.spark_model
      if (config.spark_base_url) updateData.spark_base_url = config.spark_base_url
      if (config.doubao_api_key) updateData.doubao_api_key = config.doubao_api_key
      if (config.doubao_model) updateData.doubao_model = config.doubao_model
      if (config.doubao_base_url) updateData.doubao_base_url = config.doubao_base_url
      if (config.siliconflow_api_key) updateData.siliconflow_api_key = config.siliconflow_api_key
      if (config.siliconflow_model) updateData.siliconflow_model = config.siliconflow_model
      if (config.siliconflow_base_url) updateData.siliconflow_base_url = config.siliconflow_base_url
      
      await api.admin.updateConfig(updateData)
      message.success('配置保存成功')
    } catch (error) {
      console.error(error)
      message.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleTestConnect = async () => {
    try {
      setTesting(true)
      const updateData: any = {
        llm_provider: config.llm_provider,
      }
      
      if (config.openai_api_key) updateData.openai_api_key = config.openai_api_key
      if (config.openai_model) updateData.openai_model = config.openai_model
      if (config.openai_base_url) updateData.openai_base_url = config.openai_base_url
      if (config.anthropic_api_key) updateData.anthropic_api_key = config.anthropic_api_key
      if (config.anthropic_model) updateData.anthropic_model = config.anthropic_model
      if (config.anthropic_base_url) updateData.anthropic_base_url = config.anthropic_base_url
      if (config.glm_api_key) updateData.glm_api_key = config.glm_api_key
      if (config.glm_model) updateData.glm_model = config.glm_model
      if (config.glm_base_url) updateData.glm_base_url = config.glm_base_url
      if (config.qwen_api_key) updateData.qwen_api_key = config.qwen_api_key
      if (config.qwen_model) updateData.qwen_model = config.qwen_model
      if (config.qwen_base_url) updateData.qwen_base_url = config.qwen_base_url
      if (config.minimax_api_key) updateData.minimax_api_key = config.minimax_api_key
      if (config.minimax_model) updateData.minimax_model = config.minimax_model
      if (config.minimax_base_url) updateData.minimax_base_url = config.minimax_base_url
      if (config.ernie_api_key) updateData.ernie_api_key = config.ernie_api_key
      if (config.ernie_model) updateData.ernie_model = config.ernie_model
      if (config.ernie_base_url) updateData.ernie_base_url = config.ernie_base_url
      if (config.hunyuan_api_key) updateData.hunyuan_api_key = config.hunyuan_api_key
      if (config.hunyuan_model) updateData.hunyuan_model = config.hunyuan_model
      if (config.hunyuan_base_url) updateData.hunyuan_base_url = config.hunyuan_base_url
      if (config.spark_api_key) updateData.spark_api_key = config.spark_api_key
      if (config.spark_model) updateData.spark_model = config.spark_model
      if (config.spark_base_url) updateData.spark_base_url = config.spark_base_url
      if (config.doubao_api_key) updateData.doubao_api_key = config.doubao_api_key
      if (config.doubao_model) updateData.doubao_model = config.doubao_model
      if (config.doubao_base_url) updateData.doubao_base_url = config.doubao_base_url
      if (config.siliconflow_api_key) updateData.siliconflow_api_key = config.siliconflow_api_key
      if (config.siliconflow_model) updateData.siliconflow_model = config.siliconflow_model
      if (config.siliconflow_base_url) updateData.siliconflow_base_url = config.siliconflow_base_url
      
      await api.admin.updateConfig(updateData)
      
      const testRes = await api.admin.testConnection()
      
      if (testRes.success) {
        message.success('连接成功! 厂商: ' + testRes.provider + ', 回复: ' + testRes.response?.substring(0, 50) + '...')
      } else {
        message.error('连接失败: ' + testRes.error)
      }
    } catch (error: any) {
      console.error(error)
      message.error('连接失败: ' + (error?.response?.data?.detail || error?.message || '未知错误'))
    } finally {
      setTesting(false)
    }
  }

  const handleProviderChange = (provider: string) => {
    setConfig({ ...config, llm_provider: provider })
  }

  const handleAddAssistant = () => {
    setEditingAssistant(null)
    form.resetFields()
    form.setFieldsValue({
      is_active: true,
      is_recommended: false,
    })
    setModalOpen(true)
  }

  const handleEditAssistant = (record: Assistant) => {
    setEditingAssistant(record)
    form.setFieldsValue({
      ...record,
      tags: record.tags || [],
    })
    setModalOpen(true)
  }

  const handleDeleteAssistant = async (id: number) => {
    try {
      await api.admin.deleteAssistant(id)
      message.success('删除成功')
      loadAssistants()
    } catch (error) {
      console.error(error)
      message.error('删除失败')
    }
  }

  const handleSubmitAssistant = async () => {
    try {
      const values = await form.validateFields()
      const submitData = {
        ...values,
        tags: values.tags?.join(',') || '',
      }
      if (editingAssistant) {
        await api.admin.updateAssistant(editingAssistant.id, submitData)
        message.success('更新成功')
      } else {
        await api.admin.createAssistant(submitData)
        message.success('创建成功')
      }
      setModalOpen(false)
      loadAssistants()
    } catch (error) {
      console.error(error)
      message.error('操作失败')
    }
  }

  const getCurrentModel = () => {
    const provider = config.llm_provider
    switch (provider) {
      case 'openai': return config.openai_model
      case 'anthropic': return config.anthropic_model
      case 'glm': return config.glm_model
      case 'qwen': return config.qwen_model
      case 'minimax': return config.minimax_model
      case 'ernie': return config.ernie_model
      case 'hunyuan': return config.hunyuan_model
      case 'spark': return config.spark_model
      case 'doubao': return config.doubao_model
      case 'siliconflow': return config.siliconflow_model
      default: return ''
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '名称',
      dataIndex: 'name',
      width: 120,
    },
    {
      title: 'MBTI',
      dataIndex: 'mbti_type',
      width: 80,
      render: (mbti: string) => <Tag color="purple">{mbti || '-'}</Tag>,
    },
    {
      title: '人格',
      dataIndex: 'personality',
      width: 150,
      ellipsis: true,
    },
    {
      title: '推荐',
      dataIndex: 'is_recommended',
      width: 70,
      render: (rec: boolean) => <Tag color={rec ? 'gold' : 'default'}>{rec ? '是' : '否'}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      width: 70,
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'default'}>{active ? '启用' : '禁用'}</Tag>
      ),
    },
    {
      title: '操作',
      width: 100,
      render: (_: any, record: Assistant) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEditAssistant(record)} />
          <Popconfirm title="确定删除?" onConfirm={() => handleDeleteAssistant(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  const renderConfigForm = () => {
    const provider = config.llm_provider || 'mock'
    const currentModel = getCurrentModel()

    return (
      <Form layout="vertical" style={{ maxWidth: 700 }}>
        <Form.Item label="LLM Provider" required>
          <Select
            value={provider}
            onChange={handleProviderChange}
            options={PROVIDERS}
          />
        </Form.Item>

        {provider === 'openai' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.openai_api_key || ''}
                onChange={(e) => setConfig({ ...config, openai_api_key: e.target.value })}
                placeholder={config.has_openai_key ? '已配置 (不修改请留空)' : '请输入 OpenAI API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Select
                value={currentModel}
                onChange={(value) => setConfig({ ...config, openai_model: value })}
                placeholder="选择模型"
                options={MODELS.openai}
                allowClear
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.openai_base_url || ''}
                onChange={(e) => setConfig({ ...config, openai_base_url: e.target.value })}
                placeholder="如需代理请填写"
              />
            </Form.Item>
          </>
        )}

        {provider === 'anthropic' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.anthropic_api_key || ''}
                onChange={(e) => setConfig({ ...config, anthropic_api_key: e.target.value })}
                placeholder={config.has_anthropic_key ? '已配置 (不修改请留空)' : '请输入 Anthropic API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.anthropic_model || ''}
                onChange={(e) => setConfig({ ...config, anthropic_model: e.target.value })}
                placeholder="输入模型名称，如 claude-3-5-sonnet-20241022"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.anthropic_base_url || ''}
                onChange={(e) => setConfig({ ...config, anthropic_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'glm' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.glm_api_key || ''}
                onChange={(e) => setConfig({ ...config, glm_api_key: e.target.value })}
                placeholder={config.has_glm_key ? '已配置 (不修改请留空)' : '请输入智谱 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.glm_model || ''}
                onChange={(e) => setConfig({ ...config, glm_model: e.target.value })}
                placeholder="输入模型名称，如 glm-4"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.glm_base_url || ''}
                onChange={(e) => setConfig({ ...config, glm_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'qwen' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.qwen_api_key || ''}
                onChange={(e) => setConfig({ ...config, qwen_api_key: e.target.value })}
                placeholder={config.has_qwen_key ? '已配置 (不修改请留空)' : '请输入阿里云 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.qwen_model || ''}
                onChange={(e) => setConfig({ ...config, qwen_model: e.target.value })}
                placeholder="输入模型名称，如 qwen-turbo"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.qwen_base_url || ''}
                onChange={(e) => setConfig({ ...config, qwen_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'minimax' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.minimax_api_key || ''}
                onChange={(e) => setConfig({ ...config, minimax_api_key: e.target.value })}
                placeholder={config.has_minimax_key ? '已配置 (不修改请留空)' : '请输入 MiniMax API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.minimax_model || ''}
                onChange={(e) => setConfig({ ...config, minimax_model: e.target.value })}
                placeholder="输入模型名称，如 abab6.5s-chat"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.minimax_base_url || ''}
                onChange={(e) => setConfig({ ...config, minimax_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'ernie' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.ernie_api_key || ''}
                onChange={(e) => setConfig({ ...config, ernie_api_key: e.target.value })}
                placeholder={config.has_ernie_key ? '已配置 (不修改请留空)' : '请输入百度智能云 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.ernie_model || ''}
                onChange={(e) => setConfig({ ...config, ernie_model: e.target.value })}
                placeholder="输入模型名称，如 ernie-4.0-8k"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.ernie_base_url || ''}
                onChange={(e) => setConfig({ ...config, ernie_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'hunyuan' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.hunyuan_api_key || ''}
                onChange={(e) => setConfig({ ...config, hunyuan_api_key: e.target.value })}
                placeholder={config.has_hunyuan_key ? '已配置 (不修改请留空)' : '请输入腾讯云 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.hunyuan_model || ''}
                onChange={(e) => setConfig({ ...config, hunyuan_model: e.target.value })}
                placeholder="输入模型名称，如 hunyuan-pro"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.hunyuan_base_url || ''}
                onChange={(e) => setConfig({ ...config, hunyuan_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'spark' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.spark_api_key || ''}
                onChange={(e) => setConfig({ ...config, spark_api_key: e.target.value })}
                placeholder={config.has_spark_key ? '已配置 (不修改请留空)' : '请输入讯飞 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.spark_model || ''}
                onChange={(e) => setConfig({ ...config, spark_model: e.target.value })}
                placeholder="输入模型名称，如 spark-v3.5"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.spark_base_url || ''}
                onChange={(e) => setConfig({ ...config, spark_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'doubao' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.doubao_api_key || ''}
                onChange={(e) => setConfig({ ...config, doubao_api_key: e.target.value })}
                placeholder={config.has_doubao_key ? '已配置 (不修改请留空)' : '请输入字节跳动火山引擎 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.doubao_model || ''}
                onChange={(e) => setConfig({ ...config, doubao_model: e.target.value })}
                placeholder="输入模型名称，如 doubao-pro-32k"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.doubao_base_url || ''}
                onChange={(e) => setConfig({ ...config, doubao_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'siliconflow' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.siliconflow_api_key || ''}
                onChange={(e) => setConfig({ ...config, siliconflow_api_key: e.target.value })}
                placeholder={config.has_siliconflow_key ? '已配置 (不修改请留空)' : '请输入硅基流动 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.siliconflow_model || ''}
                onChange={(e) => setConfig({ ...config, siliconflow_model: e.target.value })}
                placeholder="输入模型名称，如 Qwen/Qwen2-72B-Instruct"
              />
            </Form.Item>
            <Form.Item label="Base URL (可选)">
              <Input
                value={config.siliconflow_base_url || ''}
                onChange={(e) => setConfig({ ...config, siliconflow_base_url: e.target.value })}
                placeholder="自定义API端点"
              />
            </Form.Item>
          </>
        )}

        {provider === 'mock' && (
          <Form.Item>
            <div style={{ color: '#888' }}>Mock 模式仅用于开发测试，不会调用真实 LLM API</div>
          </Form.Item>
        )}

        <Form.Item>
          <Space>
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSaveConfig} loading={saving}>
              保存配置
            </Button>
            <Button icon={<ApiOutlined />} onClick={handleTestConnect} loading={testing}>
              测试连接
            </Button>
            <Button icon={<ReloadOutlined />} onClick={loadConfig}>
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '24px' }}>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
          返回
        </Button>
      </div>
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'config',
              label: 'LLM 配置',
              children: renderConfigForm(),
            },
            {
              key: 'assistants',
              label: 'AI 助手管理',
              children: (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleAddAssistant}>
                      添加助手
                    </Button>
                  </div>
                  <Table
                    columns={columns}
                    dataSource={assistants}
                    rowKey="id"
                    loading={assistantLoading}
                    pagination={{ pageSize: 10 }}
                  />
                </div>
              ),
            },
          ]}
        />
      </Card>

      <Modal
        title={editingAssistant ? '编辑助手' : '添加助手'}
        open={modalOpen}
        onOk={handleSubmitAssistant}
        onCancel={() => setModalOpen(false)}
        width={600}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input placeholder="请输入助手名称" />
          </Form.Item>
          <Form.Item name="mbti_type" label="MBTI类型" rules={[{ required: true, message: '请输入MBTI类型' }]}>
            <Input placeholder="如: ENFP, INFP" />
          </Form.Item>
          <Form.Item name="personality" label="人格描述">
            <Input.TextArea rows={2} placeholder="请描述助手的人格特点" />
          </Form.Item>
          <Form.Item name="speaking_style" label="说话风格">
            <Input.TextArea rows={2} placeholder="请描述助手的说话风格" />
          </Form.Item>
          <Form.Item name="expertise" label="专业领域">
            <Input.TextArea rows={2} placeholder="请描述助手的专业领域" />
          </Form.Item>
          <Form.Item name="greeting" label="问候语">
            <Input.TextArea rows={2} placeholder="请输入开场问候语" />
          </Form.Item>
          <Form.Item name="is_recommended" label="推荐" valuePropName="checked">
            <Switch checkedChildren="推荐" unCheckedChildren="普通" />
          </Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
