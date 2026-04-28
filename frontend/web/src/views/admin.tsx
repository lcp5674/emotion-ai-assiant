import { useEffect, useState } from 'react'
import { Card, Tabs, Form, Input, Select, Button, Table, Tag, Modal, Switch, Space, Popconfirm, Spin, App, Alert, Descriptions, Divider, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SaveOutlined, ReloadOutlined, ArrowLeftOutlined, ApiOutlined, SyncOutlined, CloudSyncOutlined } from '@ant-design/icons'
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
  live2d_model_url?: string  // Live2D模型文件URL
  is_active: boolean
  is_recommended?: boolean
  is_favorited?: boolean
  created_at: string
}

const PROVIDERS = [
  { value: 'volcengine', label: '字节火山引擎' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic Claude' },
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

const MBTI_TYPES = [
  { value: 'ISTJ', label: 'ISTJ - 物流师', category: '分析师' },
  { value: 'ISFJ', label: 'ISFJ - 守卫者', category: '守护者' },
  { value: 'INFJ', label: 'INFJ - 提倡者', category: '理想主义者' },
  { value: 'INTJ', label: 'INTJ - 建筑师', category: '分析师' },
  { value: 'ISTP', label: 'ISTP - 鉴赏家', category: '行动者' },
  { value: 'ISFP', label: 'ISFP - 探险家', category: '行动者' },
  { value: 'INFP', label: 'INFP - 调停者', category: '理想主义者' },
  { value: 'INTP', label: 'INTP - 逻辑学家', category: '分析师' },
  { value: 'ESTP', label: 'ESTP - 企业家', category: '行动者' },
  { value: 'ESFP', label: 'ESFP - 表演者', category: '行动者' },
  { value: 'ENFP', label: 'ENFP - 竞选者', category: '理想主义者' },
  { value: 'ENTP', label: 'ENTP - 辩论家', category: '分析师' },
  { value: 'ESTJ', label: 'ESTJ - 总经理', category: '守护者' },
  { value: 'ESFJ', label: 'ESFJ - 执政官', category: '守护者' },
  { value: 'ENFJ', label: 'ENFJ - 主人公', category: '理想主义者' },
  { value: 'ENTJ', label: 'ENTJ - 指挥官', category: '分析师' },
]

const SBTI_THEME_OPTIONS = [
  { value: 'executing', label: '执行者 - 目标导向、决策果断、结果导向' },
  { value: 'influencing', label: '影响者 - 影响他人、激励团队、善于表达' },
  { value: 'relationship', label: '关系建立 - 关注他人、合作共赢、建立信任' },
  { value: 'strategic', label: '战略思考 - 长远规划、创新思维、问题解决' },
  { value: 'analytical', label: '分析者 - 数据驱动、逻辑严谨、追求精准' },
  { value: 'creative', label: '创意者 - 创新思维、艺术感、突破常规' },
  { value: 'supportive', label: '支持者 - 乐于助人、同理心强、关怀他人' },
  { value: 'challenge', label: '挑战者 - 敢于冒险、竞争意识、追求卓越' },
  { value: 'collaborative', label: '协作者 - 团队合作、善于协调、资源整合' },
  { value: 'independent', label: '独立者 - 自主决策、自律性强、独自解决问题' },
]

const ATTACHMENT_STYLE_OPTIONS = [
  { value: 'secure', label: '安全型 - 信任他人、积极寻求亲密、情感稳定' },
  { value: 'anxious', label: '焦虑型 - 担心被抛弃、过度依赖、情绪波动' },
  { value: 'avoidant', label: '回避型 - 避免亲密、独立自主、情感距离' },
  { value: 'disorganized', label: '混乱型 - 矛盾心理、行为不稳定、难以预测' },
  { value: 'fearful', label: '恐惧型 - 害怕亲密回避社交、自我保护强' },
]

const MODELS: Record<string, { value: string; label: string }[]> = {
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

  // 知识库同步状态
  const [knowledgeSyncConfig, setKnowledgeSyncConfig] = useState<any>({
    source_url: null,
    enabled: true,
    auto_sync: false,
    sync_interval_hours: 24,
    last_sync_time: null,
    default_sources: {},
  })
  const [knowledgeSyncStatus, setKnowledgeSyncStatus] = useState<any>({
    configured: false,
    enabled: true,
    auto_sync: false,
    sync_interval_hours: 24,
    last_sync_time: null,
    local_articles_count: 0,
    sources: {},
  })
  const [knowledgeSyncLoading, setKnowledgeSyncLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)

  // 知识库Embedding和分块配置
  const [knowledgeBaseConfig, setKnowledgeBaseConfig] = useState<any>({
    embedding_model: 'BAAI/bge-large-zh-v1.5',
    embedding_dim: 1024,
    chunk_size: 500,
    chunk_overlap: 50,
    vector_db_type: 'milvus',
    milvus_host: 'localhost',
    milvus_port: 19530,
    milvus_collection: 'emotion_knowledge',
    qdrant_host: 'localhost',
    qdrant_port: 6333,
    qdrant_collection: 'emotion_knowledge',
  })
  const [knowledgeBaseLoading, setKnowledgeBaseLoading] = useState(false)

  useEffect(() => {
    loadConfig()
    loadAssistants()
    loadKnowledgeSyncConfig()
    loadKnowledgeSyncStatus()
    loadKnowledgeBaseConfig()
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

  // 知识库同步相关函数
  const loadKnowledgeSyncConfig = async () => {
    try {
      setKnowledgeSyncLoading(true)
      const res = await api.admin.knowledgeSyncConfig()
      setKnowledgeSyncConfig(res || {
        source_url: null,
        enabled: true,
        auto_sync: false,
        sync_interval_hours: 24,
        last_sync_time: null,
        default_sources: {},
      })
    } catch (error) {
      console.error(error)
    } finally {
      setKnowledgeSyncLoading(false)
    }
  }

  const loadKnowledgeSyncStatus = async () => {
    try {
      const res = await api.admin.knowledgeSyncStatus()
      setKnowledgeSyncStatus(res || {
        configured: false,
        enabled: true,
        auto_sync: false,
        sync_interval_hours: 24,
        last_sync_time: null,
        local_articles_count: 0,
        sources: {},
      })
    } catch (error) {
      console.error(error)
    }
  }

  // 知识库Embedding和分块配置
  const loadKnowledgeBaseConfig = async () => {
    try {
      setKnowledgeBaseLoading(true)
      const res = await api.admin.knowledgeBaseConfig()
      setKnowledgeBaseConfig(res || {
        embedding_model: 'BAAI/bge-large-zh-v1.5',
        embedding_dim: 1024,
        chunk_size: 500,
        chunk_overlap: 50,
        vector_db_type: 'milvus',
        milvus_host: 'localhost',
        milvus_port: 19530,
        milvus_collection: 'emotion_knowledge',
        qdrant_host: 'localhost',
        qdrant_port: 6333,
        qdrant_collection: 'emotion_knowledge',
      })
    } catch (error) {
      console.error(error)
    } finally {
      setKnowledgeBaseLoading(false)
    }
  }

  const handleSaveKnowledgeBaseConfig = async () => {
    try {
      setKnowledgeBaseLoading(true)
      await api.admin.updateKnowledgeBaseConfig(knowledgeBaseConfig)
      message.success('知识库配置已保存')
    } catch (error) {
      console.error(error)
      message.error('保存失败')
    } finally {
      setKnowledgeBaseLoading(false)
    }
  }

  const handleSaveKnowledgeSyncConfig = async () => {
    try {
      setSyncing(true)
      await api.admin.updateKnowledgeSyncConfig({
        source_url: knowledgeSyncConfig.source_url || null,
        enabled: knowledgeSyncConfig.enabled,
        auto_sync: knowledgeSyncConfig.auto_sync,
        sync_interval_hours: knowledgeSyncConfig.sync_interval_hours,
      })
      message.success('知识库同步配置已保存')
      loadKnowledgeSyncStatus()
    } catch (error) {
      console.error(error)
      message.error('保存失败')
    } finally {
      setSyncing(false)
    }
  }

  const handleTriggerSync = async () => {
    try {
      setSyncing(true)
      const res = await api.admin.triggerKnowledgeSync()
      if (res.success) {
        message.success(res.message || '同步成功')
      } else {
        message.warning(res.message || '同步完成但无新内容')
      }
      loadKnowledgeSyncStatus()
    } catch (error: any) {
      console.error(error)
      message.error('同步失败: ' + (error?.response?.data?.detail || error?.message || '未知错误'))
    } finally {
      setSyncing(false)
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
      sbti_types: record.sbti_types ? record.sbti_types.split(',').filter(Boolean) : [],
      attachment_styles: record.attachment_styles ? record.attachment_styles.split(',').filter(Boolean) : [],
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
        sbti_types: Array.isArray(values.sbti_types) ? values.sbti_types.join(',') : (values.sbti_types || ''),
        attachment_styles: Array.isArray(values.attachment_styles) ? values.attachment_styles.join(',') : (values.attachment_styles || ''),
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
            {
              key: 'knowledge_sync',
              label: '知识库同步',
              children: (
                <div>
                  <Spin spinning={knowledgeSyncLoading}>
                    <Alert
                      type="info"
                      showIcon
                      message="知识库联网同步功能"
                      description="从公开的免费心理知识API自动获取内容，包括励志名言、生活建议和正能量语录。支持管理员手动触发同步或配置自动同步。"
                      style={{ marginBottom: 16 }}
                    />

                    <Descriptions bordered column={1} size="small" style={{ marginBottom: 16 }}>
                      <Descriptions.Item label="本地文章数量">
                        <Tag color="blue">{knowledgeSyncStatus.local_articles_count || 0}</Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="最后同步时间">
                        {knowledgeSyncStatus.last_sync_time
                          ? new Date(knowledgeSyncStatus.last_sync_time).toLocaleString('zh-CN')
                          : '从未同步'}
                      </Descriptions.Item>
                      <Descriptions.Item label="同步状态">
                        <Tag color={knowledgeSyncStatus.enabled ? 'green' : 'orange'}>
                          {knowledgeSyncStatus.enabled ? '已启用' : '已禁用'}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="自动同步">
                        <Tag color={knowledgeSyncStatus.auto_sync ? 'green' : 'default'}>
                          {knowledgeSyncStatus.auto_sync ? '已启用' : '未启用'}
                        </Tag>
                        {knowledgeSyncStatus.auto_sync && (
                          <span style={{ marginLeft: 8, color: '#888' }}>
                            (每 {knowledgeSyncStatus.sync_interval_hours || 24} 小时)
                          </span>
                        )}
                      </Descriptions.Item>
                    </Descriptions>

                    <Divider>默认数据源 (免费公开API)</Divider>

                    <div style={{ marginBottom: 16 }}>
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="ZenQuotes API">
                          <code style={{ fontSize: 12 }}>https://zenquotes.io/api/random</code>
                          <Tag color="green" style={{ marginLeft: 8 }}>励志名言</Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Advice Slip API">
                          <code style={{ fontSize: 12 }}>https://api.adviceslip.com/advice</code>
                          <Tag color="blue" style={{ marginLeft: 8 }}>生活建议</Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Affirmations API">
                          <code style={{ fontSize: 12 }}>https://www.affirmations.cool/</code>
                          <Tag color="purple" style={{ marginLeft: 8 }}>正能量语录</Tag>
                        </Descriptions.Item>
                      </Descriptions>
                    </div>

                    <Divider>同步配置</Divider>

                    <Form layout="vertical" style={{ maxWidth: 600 }}>
                      <Form.Item label="自定义数据源URL (可选)">
                        <Input
                          placeholder="留空则使用上述所有默认源"
                          value={knowledgeSyncConfig.source_url || ''}
                          onChange={(e) => setKnowledgeSyncConfig({
                            ...knowledgeSyncConfig,
                            source_url: e.target.value || null
                          })}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          如果配置了自定义URL，则只从该URL获取数据
                        </div>
                      </Form.Item>

                      <Form.Item label="同步间隔 (小时)">
                        <InputNumber
                          min={1}
                          max={168}
                          value={knowledgeSyncConfig.sync_interval_hours || 24}
                          onChange={(value) => setKnowledgeSyncConfig({
                            ...knowledgeSyncConfig,
                            sync_interval_hours: value || 24
                          })}
                          style={{ width: 200 }}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          设置自动同步的间隔时间（1-168小时）
                        </div>
                      </Form.Item>

                      <Form.Item>
                        <Space>
                          <Button
                            type="primary"
                            icon={<SyncOutlined />}
                            onClick={handleTriggerSync}
                            loading={syncing}
                          >
                            立即同步
                          </Button>
                          <Button
                            icon={<SaveOutlined />}
                            onClick={handleSaveKnowledgeSyncConfig}
                            loading={syncing}
                          >
                            保存配置
                          </Button>
                          <Button
                            icon={<ReloadOutlined />}
                            onClick={() => {
                              loadKnowledgeSyncConfig()
                              loadKnowledgeSyncStatus()
                            }}
                          >
                            刷新状态
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Spin>
                </div>
              ),
            },
            {
              key: 'knowledge_base_embedding',
              label: '知识库配置',
              children: (
                <div>
                  <Spin spinning={knowledgeBaseLoading}>
                    <Alert
                      type="info"
                      showIcon
                      message="知识库Embedding和分块配置"
                      description="配置RAG知识库使用的Embedding模型和文本分块参数。这些设置影响知识检索的质量和准确性。"
                      style={{ marginBottom: 16 }}
                    />

                    <Divider>Embedding配置</Divider>

                    <Form layout="vertical" style={{ maxWidth: 700 }}>
                      <Form.Item label="Embedding模型">
                        <Select
                          value={knowledgeBaseConfig.embedding_model}
                          onChange={(value) => setKnowledgeBaseConfig({
                            ...knowledgeBaseConfig,
                            embedding_model: value
                          })}
                          style={{ width: '100%' }}
                        >
                          <Select.Option value="BAAI/bge-large-zh-v1.5">BAAI/bge-large-zh-v1.5 (推荐)</Select.Option>
                          <Select.Option value="BAAI/bge-base-zh-v1.5">BAAI/bge-base-zh-v1.5</Select.Option>
                          <Select.Option value="text-embedding-ada-002">OpenAI text-embedding-ada-002</Select.Option>
                          <Select.Option value="m3e-base">M3E Base</Select.Option>
                        </Select>
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          中文优化模型，适合心理知识库的语义检索
                        </div>
                      </Form.Item>

                      <Form.Item label="Embedding维度">
                        <InputNumber
                          value={knowledgeBaseConfig.embedding_dim}
                          onChange={(value) => setKnowledgeBaseConfig({
                            ...knowledgeBaseConfig,
                            embedding_dim: value || 1024
                          })}
                          min={128}
                          max={4096}
                          step={128}
                          style={{ width: 200 }}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          BAAI/bge-large-zh-v1.5 为 1024 维，BAAI/bge-base-zh-v1.5 为 768 维
                        </div>
                      </Form.Item>

                      <Divider>文本分块配置</Divider>

                      <Form.Item label="分块大小 (Chunk Size)">
                        <InputNumber
                          value={knowledgeBaseConfig.chunk_size}
                          onChange={(value) => setKnowledgeBaseConfig({
                            ...knowledgeBaseConfig,
                            chunk_size: value || 500
                          })}
                          min={100}
                          max={2000}
                          step={50}
                          style={{ width: 200 }}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          每个文本块的最大字符数。较小适合精确检索，较大适合保持上下文
                        </div>
                      </Form.Item>

                      <Form.Item label="分块重叠 (Chunk Overlap)">
                        <InputNumber
                          value={knowledgeBaseConfig.chunk_overlap}
                          onChange={(value) => setKnowledgeBaseConfig({
                            ...knowledgeBaseConfig,
                            chunk_overlap: value || 50
                          })}
                          min={0}
                          max={500}
                          step={10}
                          style={{ width: 200 }}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>
                          相邻文本块之间的重叠字符数，帮助保持检索的连续性
                        </div>
                      </Form.Item>

                      <Divider>向量数据库配置</Divider>

                      <Form.Item label="向量数据库类型">
                        <Select
                          value={knowledgeBaseConfig.vector_db_type}
                          onChange={(value) => setKnowledgeBaseConfig({
                            ...knowledgeBaseConfig,
                            vector_db_type: value
                          })}
                          style={{ width: '100%' }}
                        >
                          <Select.Option value="milvus">Milvus</Select.Option>
                          <Select.Option value="qdrant">Qdrant</Select.Option>
                          <Select.Option value="memory">内存存储 (开发测试)</Select.Option>
                        </Select>
                      </Form.Item>

                      {knowledgeBaseConfig.vector_db_type === 'milvus' && (
                        <>
                          <Form.Item label="Milvus 主机">
                            <Input
                              value={knowledgeBaseConfig.milvus_host}
                              onChange={(e) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                milvus_host: e.target.value
                              })}
                              placeholder="localhost"
                            />
                          </Form.Item>
                          <Form.Item label="Milvus 端口">
                            <InputNumber
                              value={knowledgeBaseConfig.milvus_port}
                              onChange={(value) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                milvus_port: value || 19530
                              })}
                              min={1}
                              max={65535}
                              style={{ width: 200 }}
                            />
                          </Form.Item>
                          <Form.Item label="Milvus Collection名称">
                            <Input
                              value={knowledgeBaseConfig.milvus_collection}
                              onChange={(e) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                milvus_collection: e.target.value
                              })}
                              placeholder="emotion_knowledge"
                            />
                          </Form.Item>
                        </>
                      )}

                      {knowledgeBaseConfig.vector_db_type === 'qdrant' && (
                        <>
                          <Form.Item label="Qdrant 主机">
                            <Input
                              value={knowledgeBaseConfig.qdrant_host}
                              onChange={(e) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                qdrant_host: e.target.value
                              })}
                              placeholder="localhost"
                            />
                          </Form.Item>
                          <Form.Item label="Qdrant 端口">
                            <InputNumber
                              value={knowledgeBaseConfig.qdrant_port}
                              onChange={(value) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                qdrant_port: value || 6333
                              })}
                              min={1}
                              max={65535}
                              style={{ width: 200 }}
                            />
                          </Form.Item>
                          <Form.Item label="Qdrant Collection名称">
                            <Input
                              value={knowledgeBaseConfig.qdrant_collection}
                              onChange={(e) => setKnowledgeBaseConfig({
                                ...knowledgeBaseConfig,
                                qdrant_collection: e.target.value
                              })}
                              placeholder="emotion_knowledge"
                            />
                          </Form.Item>
                        </>
                      )}

                      <Form.Item>
                        <Space>
                          <Button
                            type="primary"
                            icon={<SaveOutlined />}
                            onClick={handleSaveKnowledgeBaseConfig}
                            loading={knowledgeBaseLoading}
                          >
                            保存配置
                          </Button>
                          <Button
                            icon={<ReloadOutlined />}
                            onClick={loadKnowledgeBaseConfig}
                          >
                            重置
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Spin>
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
          <Form.Item name="mbti_type" label="MBTI类型" rules={[{ required: true, message: '请选择MBTI类型' }]}>
            <Select
              placeholder="选择MBTI类型"
              showSearch
              allowClear
              optionFilterProp="label"
              dropdownRender={menu => menu}
              options={MBTI_TYPES.map(m => ({ value: m.value, label: m.label }))}
            />
          </Form.Item>
          <Form.Item name="sbti_types" label="SBTI主题类型">
            <Select
              mode="multiple"
              placeholder="选择SBTI主题"
              allowClear
              optionFilterProp="label"
              options={SBTI_THEME_OPTIONS.map(s => ({ value: s.value, label: s.label }))}
            />
          </Form.Item>
          <Form.Item name="attachment_styles" label="依恋风格类型">
            <Select
              mode="multiple"
              placeholder="选择依恋风格"
              allowClear
              optionFilterProp="label"
              options={ATTACHMENT_STYLE_OPTIONS.map(a => ({ value: a.value, label: a.label }))}
            />
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
          <Form.Item
            name="live2d_model_url"
            label="Live2D模型URL"
            tooltip="填写Live2D模型的在线URL，如: https://example.com/model/Haru.model3.json"
          >
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 100px)' }}
                placeholder="https://example.com/model/Haru.model3.json"
              />
              <Button onClick={async () => {
                const url = form.getFieldValue('live2d_model_url')
                if (!url) {
                  message.warning('请先输入Live2D模型URL')
                  return
                }
                try {
                  message.loading('正在测试Live2D模型连通性并下载...', 0)
                  const response = await fetch(url, { method: 'HEAD' })
                  if (response.ok) {
                    message.success('Live2D模型配置成功！模型文件可访问')
                  } else {
                    message.error('模型文件不可访问')
                  }
                } catch (error) {
                  message.error('连接失败，请检查URL是否正确')
                }
              }}>测试</Button>
            </Input.Group>
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
