/**
 * 情绪分析模块 - 调用后端API进行AI模型情感分析
 *
 * 后端使用轻量级预训练模型 (distilbert-base-multilingual-uncased-sentiment)
 * 支持中英文情感识别，返回虚拟形象的表情和动作指令
 */

import api from '../../api/request'

// 情绪标签映射到表情（与后端保持一致）
const EMOTION_TO_EXPRESSION: Record<string, { expression: string; motion: string }> = {
  'joy': { expression: 'happy', motion: 'happy' },
  'happy': { expression: 'happy', motion: 'happy' },
  'positive': { expression: 'happy', motion: 'happy' },
  'sadness': { expression: 'sad', motion: 'sad' },
  'sad': { expression: 'sad', motion: 'sad' },
  'negative': { expression: 'sad', motion: 'sad' },
  'anger': { expression: 'angry', motion: 'angry' },
  'angry': { expression: 'angry', motion: 'angry' },
  'fear': { expression: 'surprised', motion: 'nod' },
  'surprise': { expression: 'surprised', motion: 'nod' },
  'neutral': { expression: 'smile', motion: 'idle' },
  'disgust': { expression: 'angry', motion: 'angry' },
}

/**
 * 分析文本情绪
 * @param text 输入文本
 * @returns 情绪分析结果 { expression, motion, confidence, label }
 */
export async function analyzeSentiment(
  text: string
): Promise<{ expression: string; motion: string; confidence: number; label: string } | null> {
  if (!text || !text.trim()) {
    return null
  }

  try {
    const response = await api.post('/sentiment/analyze', {
      text: text.trim()
    }) as any

    console.log('后端AI情绪分析结果:', response)

    if (response && response.expression) {
      return {
        expression: response.expression,
        motion: response.motion,
        confidence: response.confidence,
        label: response.label
      }
    }

    return null
  } catch (error) {
    console.error('情绪分析API调用失败:', error)
    return null
  }
}

// 以下函数保持向后兼容
export async function loadSentimentModel(): Promise<any> {
  console.log('情绪分析使用后端AI模型')
  return {}
}

export function warmupModel(): Promise<void> {
  return Promise.resolve()
}

export function isModelLoaded(): boolean {
  return true
}
