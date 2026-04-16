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
  volcengine_api_key?: string
  volcengine_model?: string
  volcengine_base_url?: string
  has_volcengine_key?: boolean
  sensetime_api_key?: string
  sensetime_model?: string
  has_sensetime_key?: boolean
  baichuan_api_key?: string
  baichuan_model?: string
  has_baichuan_key?: boolean
  moonshot_api_key?: string
  moonshot_model?: string
  has_moonshot_key?: boolean
  lingyi_api_key?: string
  lingyi_model?: string
  has_lingyi_key?: boolean
  custom_llm_api_key?: string
  custom_llm_model?: string
  custom_llm_base_url?: string
  has_custom_llm_key?: boolean
  llm_failover_chain?: string
}

interface Assistant {
  id: number
  name: string
  description?: string
  avatar?: string
  mbti_type: string
  sbti_types?: string  // SBTI主题类型
  attachment_styles?: string  // 依恋风格类型
  personality?: string
  speaking_style?: string
  expertise?: string
  greeting?: string
  tags?: string[]
  is_active: boolean
  is_recommended?: boolean
  is_favorited?: boolean
  created_at: string
}

const PROVIDERS = [
  { value: 'mock', label: 'Mock (开发测试)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic Claude' },
  { value: 'volcengine', label: '字节火山引擎' },
  { value: 'doubao', label: '字节豆包' },
  { value: 'glm', label: '智谱 GLM' },
  { value: 'qwen', label: '阿里通义千问' },
  { value: 'minimax', label: 'MiniMax' },
  { value: 'ernie', label: '百度文心一言' },
  { value: 'hunyuan', label: '腾讯混元' },
  { value: 'spark', label: '讯飞星火' },
  { value: 'siliconflow', label: '硅基流动' },
  { value: 'sensetime', label: '商汤科技' },
  { value: 'baichuan', label: '百川智能' },
  { value: 'moonshot', label: '月之暗面' },
  { value: 'lingyi', label: '零一万物' },
  { value: 'custom', label: '自定义 (兼容OpenAI协议)' },
]

const FAILOVER_CHAIN_OPTIONS = [
  { value: 'volcengine', label: '火山引擎' },
  { value: 'doubao', label: '豆包' },
  { value: 'glm', label: '智谱GLM' },
  { value: 'qwen', label: '通义千问' },
  { value: 'siliconflow', label: '硅基流动' },
  { value: 'ernie', label: '文心一言' },
  { value: 'hunyuan', label: '腾讯混元' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Claude' },
  { value: 'minimax', label: 'MiniMax' },
  { value: 'spark', label: '讯飞星火' },
  { value: 'sensetime', label: '商汤' },
  { value: 'baichuan', label: '百川' },
  { value: 'moonshot', label: '月之暗面' },
  { value: 'lingyi', label: '零一万物' },
  { value: 'custom', label: '自定义' },
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
  const [testingProvider, setTestingProvider] = useState<string | null>(null)
  const [config, setConfig] = useState<ConfigData>({
    llm_provider: 'mock',
    llm_failover_chain: 'volcengine,doubao,glm,qwen,siliconflow,ernie,hunyuan',
  })
  const [assistants, setAssistants] = useState<Assistant[]>([])
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAssistant, setEditingAssistant] = useState<Assistant | null>(null)
  const [form] = Form.useForm()
  const [providerStatus, setProviderStatus] = useState<{provider: string; has_api_key: boolean; model: string; base_url: string}[]>([])
  const [providerStatusLoading, setProviderStatusLoading] = useState(false)

  useEffect(() => {
    loadConfig()
    loadAssistants()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const res = await api.admin.config()
      setConfig(res || { llm_provider: 'mock' })
      // 加载provider状态
      loadProviderStatus()
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadProviderStatus = async () => {
    try {
      setProviderStatusLoading(true)
      const res = await api.admin.providerStatus()
      setProviderStatus(res.providers || [])
    } catch (error) {
      console.error(error)
    } finally {
      setProviderStatusLoading(false)
    }
  }

  const testProvider = async (provider: string) => {
    try {
      setTestingProvider(provider)
      const res = await api.admin.testProvider(provider)
      if (res.success) {
        message.success(`${provider} 测试成功! 模型: ${res.model}`)
      } else {
        message.error(`${provider} 测试失败: ${res.error}`)
      }
    } catch (error: any) {
      message.error(`${provider} 测试失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`)
    } finally {
      setTestingProvider(null)
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

  // 辅助函数：检测是否是掩码值（格式如 d76c...c157）
  const isMaskedValue = (value: string) => value && value.includes('...')

  const handleSaveConfig = async () => {
    try {
      setSaving(true)
      const updateData: any = {
        llm_provider: config.llm_provider,
        llm_failover_chain: config.llm_failover_chain,
      }

      // API Key：只有非掩码值才发送，掩码表示已有配置但用户未修改
      if (config.openai_api_key && !isMaskedValue(config.openai_api_key)) updateData.openai_api_key = config.openai_api_key
      if (config.openai_model) updateData.openai_model = config.openai_model
      if (config.openai_base_url) updateData.openai_base_url = config.openai_base_url
      if (config.anthropic_api_key && !isMaskedValue(config.anthropic_api_key)) updateData.anthropic_api_key = config.anthropic_api_key
      if (config.anthropic_model) updateData.anthropic_model = config.anthropic_model
      if (config.anthropic_base_url) updateData.anthropic_base_url = config.anthropic_base_url
      if (config.glm_api_key && !isMaskedValue(config.glm_api_key)) updateData.glm_api_key = config.glm_api_key
      if (config.glm_model) updateData.glm_model = config.glm_model
      if (config.glm_base_url) updateData.glm_base_url = config.glm_base_url
      if (config.qwen_api_key && !isMaskedValue(config.qwen_api_key)) updateData.qwen_api_key = config.qwen_api_key
      if (config.qwen_model) updateData.qwen_model = config.qwen_model
      if (config.qwen_base_url) updateData.qwen_base_url = config.qwen_base_url
      if (config.minimax_api_key && !isMaskedValue(config.minimax_api_key)) updateData.minimax_api_key = config.minimax_api_key
      if (config.minimax_model) updateData.minimax_model = config.minimax_model
      if (config.minimax_base_url) updateData.minimax_base_url = config.minimax_base_url
      if (config.ernie_api_key && !isMaskedValue(config.ernie_api_key)) updateData.ernie_api_key = config.ernie_api_key
      if (config.ernie_model) updateData.ernie_model = config.ernie_model
      if (config.ernie_base_url) updateData.ernie_base_url = config.ernie_base_url
      if (config.hunyuan_api_key && !isMaskedValue(config.hunyuan_api_key)) updateData.hunyuan_api_key = config.hunyuan_api_key
      if (config.hunyuan_model) updateData.hunyuan_model = config.hunyuan_model
      if (config.hunyuan_base_url) updateData.hunyuan_base_url = config.hunyuan_base_url
      if (config.spark_api_key && !isMaskedValue(config.spark_api_key)) updateData.spark_api_key = config.spark_api_key
      if (config.spark_model) updateData.spark_model = config.spark_model
      if (config.spark_base_url) updateData.spark_base_url = config.spark_base_url
      if (config.doubao_api_key && !isMaskedValue(config.doubao_api_key)) updateData.doubao_api_key = config.doubao_api_key
      if (config.doubao_model) updateData.doubao_model = config.doubao_model
      if (config.doubao_base_url) updateData.doubao_base_url = config.doubao_base_url
      if (config.siliconflow_api_key && !isMaskedValue(config.siliconflow_api_key)) updateData.siliconflow_api_key = config.siliconflow_api_key
      if (config.siliconflow_model) updateData.siliconflow_model = config.siliconflow_model
      if (config.siliconflow_base_url) updateData.siliconflow_base_url = config.siliconflow_base_url
      if (config.volcengine_api_key && !isMaskedValue(config.volcengine_api_key)) updateData.volcengine_api_key = config.volcengine_api_key
      if (config.volcengine_model) updateData.volcengine_model = config.volcengine_model
      if (config.volcengine_base_url) updateData.volcengine_base_url = config.volcengine_base_url
      if (config.sensetime_api_key && !isMaskedValue(config.sensetime_api_key)) updateData.sensetime_api_key = config.sensetime_api_key
      if (config.sensetime_model) updateData.sensetime_model = config.sensetime_model
      if (config.baichuan_api_key && !isMaskedValue(config.baichuan_api_key)) updateData.baichuan_api_key = config.baichuan_api_key
      if (config.baichuan_model) updateData.baichuan_model = config.baichuan_model
      if (config.moonshot_api_key && !isMaskedValue(config.moonshot_api_key)) updateData.moonshot_api_key = config.moonshot_api_key
      if (config.moonshot_model) updateData.moonshot_model = config.moonshot_model
      if (config.lingyi_api_key && !isMaskedValue(config.lingyi_api_key)) updateData.lingyi_api_key = config.lingyi_api_key
      if (config.lingyi_model) updateData.lingyi_model = config.lingyi_model
      if (config.custom_llm_api_key && !isMaskedValue(config.custom_llm_api_key)) updateData.custom_llm_api_key = config.custom_llm_api_key
      if (config.custom_llm_model) updateData.custom_llm_model = config.custom_llm_model
      if (config.custom_llm_base_url) updateData.custom_llm_base_url = config.custom_llm_base_url

      await api.admin.updateConfig(updateData)
      message.success('配置保存成功')
      // 重新加载provider状态
      loadProviderStatus()
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
        llm_failover_chain: config.llm_failover_chain,
      }

      // API Key：只有非掩码值才发送，掩码表示已有配置但用户未修改
      if (config.openai_api_key && !isMaskedValue(config.openai_api_key)) updateData.openai_api_key = config.openai_api_key
      if (config.openai_model) updateData.openai_model = config.openai_model
      if (config.openai_base_url) updateData.openai_base_url = config.openai_base_url
      if (config.anthropic_api_key && !isMaskedValue(config.anthropic_api_key)) updateData.anthropic_api_key = config.anthropic_api_key
      if (config.anthropic_model) updateData.anthropic_model = config.anthropic_model
      if (config.anthropic_base_url) updateData.anthropic_base_url = config.anthropic_base_url
      if (config.glm_api_key && !isMaskedValue(config.glm_api_key)) updateData.glm_api_key = config.glm_api_key
      if (config.glm_model) updateData.glm_model = config.glm_model
      if (config.glm_base_url) updateData.glm_base_url = config.glm_base_url
      if (config.qwen_api_key && !isMaskedValue(config.qwen_api_key)) updateData.qwen_api_key = config.qwen_api_key
      if (config.qwen_model) updateData.qwen_model = config.qwen_model
      if (config.qwen_base_url) updateData.qwen_base_url = config.qwen_base_url
      if (config.minimax_api_key && !isMaskedValue(config.minimax_api_key)) updateData.minimax_api_key = config.minimax_api_key
      if (config.minimax_model) updateData.minimax_model = config.minimax_model
      if (config.minimax_base_url) updateData.minimax_base_url = config.minimax_base_url
      if (config.ernie_api_key && !isMaskedValue(config.ernie_api_key)) updateData.ernie_api_key = config.ernie_api_key
      if (config.ernie_model) updateData.ernie_model = config.ernie_model
      if (config.ernie_base_url) updateData.ernie_base_url = config.ernie_base_url
      if (config.hunyuan_api_key && !isMaskedValue(config.hunyuan_api_key)) updateData.hunyuan_api_key = config.hunyuan_api_key
      if (config.hunyuan_model) updateData.hunyuan_model = config.hunyuan_model
      if (config.hunyuan_base_url) updateData.hunyuan_base_url = config.hunyuan_base_url
      if (config.spark_api_key && !isMaskedValue(config.spark_api_key)) updateData.spark_api_key = config.spark_api_key
      if (config.spark_model) updateData.spark_model = config.spark_model
      if (config.spark_base_url) updateData.spark_base_url = config.spark_base_url
      if (config.doubao_api_key && !isMaskedValue(config.doubao_api_key)) updateData.doubao_api_key = config.doubao_api_key
      if (config.doubao_model) updateData.doubao_model = config.doubao_model
      if (config.doubao_base_url) updateData.doubao_base_url = config.doubao_base_url
      if (config.siliconflow_api_key && !isMaskedValue(config.siliconflow_api_key)) updateData.siliconflow_api_key = config.siliconflow_api_key
      if (config.siliconflow_model) updateData.siliconflow_model = config.siliconflow_model
      if (config.siliconflow_base_url) updateData.siliconflow_base_url = config.siliconflow_base_url
      if (config.volcengine_api_key && !isMaskedValue(config.volcengine_api_key)) updateData.volcengine_api_key = config.volcengine_api_key
      if (config.volcengine_model) updateData.volcengine_model = config.volcengine_model
      if (config.volcengine_base_url) updateData.volcengine_base_url = config.volcengine_base_url
      if (config.sensetime_api_key && !isMaskedValue(config.sensetime_api_key)) updateData.sensetime_api_key = config.sensetime_api_key
      if (config.sensetime_model) updateData.sensetime_model = config.sensetime_model
      if (config.baichuan_api_key && !isMaskedValue(config.baichuan_api_key)) updateData.baichuan_api_key = config.baichuan_api_key
      if (config.baichuan_model) updateData.baichuan_model = config.baichuan_model
      if (config.moonshot_api_key && !isMaskedValue(config.moonshot_api_key)) updateData.moonshot_api_key = config.moonshot_api_key
      if (config.moonshot_model) updateData.moonshot_model = config.moonshot_model
      if (config.lingyi_api_key && !isMaskedValue(config.lingyi_api_key)) updateData.lingyi_api_key = config.lingyi_api_key
      if (config.lingyi_model) updateData.lingyi_model = config.lingyi_model
      if (config.custom_llm_api_key && !isMaskedValue(config.custom_llm_api_key)) updateData.custom_llm_api_key = config.custom_llm_api_key
      if (config.custom_llm_model) updateData.custom_llm_model = config.custom_llm_model
      if (config.custom_llm_base_url) updateData.custom_llm_base_url = config.custom_llm_base_url

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
        sbti_types: values.sbti_types || '',
        attachment_styles: values.attachment_styles || '',
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
      case 'custom': return config.custom_llm_model
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
      title: 'SBTI主题',
      dataIndex: 'sbti_types',
      width: 150,
      ellipsis: true,
      render: (sbti: string) => sbti ? <Tag color="blue">{sbti}</Tag> : '-',
    },
    {
      title: '依恋风格',
      dataIndex: 'attachment_styles',
      width: 100,
      ellipsis: true,
      render: (style: string) => style ? <Tag color="green">{style}</Tag> : '-',
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

        <Form.Item label="Failover Chain (降级链)" tooltip="当主Provider失败时，按顺序尝试其他Provider。用逗号分隔。">
          <Select
            mode="multiple"
            value={config.llm_failover_chain?.split(',').filter(Boolean) || []}
            onChange={(values) => setConfig({ ...config, llm_failover_chain: values.join(',') })}
            options={FAILOVER_CHAIN_OPTIONS}
            placeholder="选择降级Provider顺序"
            style={{ width: '100%' }}
          />
        </Form.Item>

        {/* 降级链Provider状态 */}
        {providerStatus.length > 0 && (
          <Form.Item label="降级链状态" tooltip="显示降级链中各Provider的配置状态和可用性测试">
            <div style={{ border: '1px solid #d9d9d9', borderRadius: 8, padding: 16, background: '#fafafa' }}>
              <Spin spinning={providerStatusLoading}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
                  {providerStatus.map((p) => (
                    <div key={p.provider} style={{
                      padding: 12,
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                      background: p.has_api_key ? '#f6ffed' : '#fff7e6',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <span style={{ fontWeight: 500 }}>{p.provider}</span>
                        <Tag color={p.has_api_key ? 'green' : 'orange'}>
                          {p.has_api_key ? '已配置' : '未配置'}
                        </Tag>
                      </div>
                      <div style={{ fontSize: 12, color: '#8c8c8c', marginBottom: 8 }}>
                        模型: {p.model}
                      </div>
                      <Button
                        size="small"
                        onClick={() => testProvider(p.provider)}
                        loading={testingProvider === p.provider}
                        disabled={!p.has_api_key}
                      >
                        测试连接
                      </Button>
                    </div>
                  ))}
                </div>
              </Spin>
            </div>
          </Form.Item>
        )}

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

        {provider === 'volcengine' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.volcengine_api_key || ''}
                onChange={(e) => setConfig({ ...config, volcengine_api_key: e.target.value })}
                placeholder={config.has_volcengine_key ? '已配置 (不修改请留空)' : '请输入火山引擎 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.volcengine_model || ''}
                onChange={(e) => setConfig({ ...config, volcengine_model: e.target.value })}
                placeholder="输入模型名称，如 doubao-pro-32k"
              />
            </Form.Item>
            <Form.Item label="Base URL">
              <Input
                value={config.volcengine_base_url || ''}
                onChange={(e) => setConfig({ ...config, volcengine_base_url: e.target.value })}
                placeholder="https://ark.cn-beijing.volces.com/api/v3"
              />
            </Form.Item>
          </>
        )}

        {provider === 'sensetime' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.sensetime_api_key || ''}
                onChange={(e) => setConfig({ ...config, sensetime_api_key: e.target.value })}
                placeholder={config.has_sensetime_key ? '已配置 (不修改请留空)' : '请输入商汤科技 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.sensetime_model || ''}
                onChange={(e) => setConfig({ ...config, sensetime_model: e.target.value })}
                placeholder="输入模型名称，如 sensechat-5"
              />
            </Form.Item>
          </>
        )}

        {provider === 'baichuan' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.baichuan_api_key || ''}
                onChange={(e) => setConfig({ ...config, baichuan_api_key: e.target.value })}
                placeholder={config.has_baichuan_key ? '已配置 (不修改请留空)' : '请输入百川智能 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.baichuan_model || ''}
                onChange={(e) => setConfig({ ...config, baichuan_model: e.target.value })}
                placeholder="输入模型名称，如 baichuan4"
              />
            </Form.Item>
          </>
        )}

        {provider === 'moonshot' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.moonshot_api_key || ''}
                onChange={(e) => setConfig({ ...config, moonshot_api_key: e.target.value })}
                placeholder={config.has_moonshot_key ? '已配置 (不修改请留空)' : '请输入月之暗面 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.moonshot_model || ''}
                onChange={(e) => setConfig({ ...config, moonshot_model: e.target.value })}
                placeholder="输入模型名称，如 moonshot-v1-8k"
              />
            </Form.Item>
          </>
        )}

        {provider === 'lingyi' && (
          <>
            <Form.Item label="API Key">
              <Input.Password
                value={config.lingyi_api_key || ''}
                onChange={(e) => setConfig({ ...config, lingyi_api_key: e.target.value })}
                placeholder={config.has_lingyi_key ? '已配置 (不修改请留空)' : '请输入零一万物 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model">
              <Input
                value={config.lingyi_model || ''}
                onChange={(e) => setConfig({ ...config, lingyi_model: e.target.value })}
                placeholder="输入模型名称，如 yi-medium"
              />
            </Form.Item>
          </>
        )}

        {provider === 'custom' && (
          <>
            <Form.Item label="API Key" tooltip="填入您的API Key，支持任何兼容OpenAI协议的服务">
              <Input.Password
                value={config.custom_llm_api_key || ''}
                onChange={(e) => setConfig({ ...config, custom_llm_api_key: e.target.value })}
                placeholder={config.has_custom_llm_key ? '已配置 (不修改请留空)' : '请输入 API Key'}
              />
            </Form.Item>
            <Form.Item label="Model" tooltip="填入要使用的模型名称">
              <Input
                value={config.custom_llm_model || ''}
                onChange={(e) => setConfig({ ...config, custom_llm_model: e.target.value })}
                placeholder="输入模型名称，如 gpt-3.5-turbo"
              />
            </Form.Item>
            <Form.Item label="Base URL" tooltip="填入API Endpoint URL，必须是OpenAI兼容格式">
              <Input
                value={config.custom_llm_base_url || ''}
                onChange={(e) => setConfig({ ...config, custom_llm_base_url: e.target.value })}
                placeholder="https://api.openai.com/v1"
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
          <Form.Item name="sbti_types" label="SBTI主题类型" tooltip="逗号分隔的主题类型，如: executing,influencing,relationship,strategic">
            <Input placeholder="如: executing,influencing,relationship" />
          </Form.Item>
          <Form.Item name="attachment_styles" label="依恋风格类型" tooltip="逗号分隔的风格类型，如: secure,anxious,avoidant">
            <Input placeholder="如: secure,anxious" />
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
