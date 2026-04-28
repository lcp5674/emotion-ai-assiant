/**
 * MBTI 类型到 Live2D 模型的映射配置
 */

// 16种 MBTI 类型的 Live2D 模型路径 (SDK 5 兼容)
export const MBTI_LIVE2D_MODELS: Record<string, string> = {
  'INTJ': '/live2d/all/shizuku/shizuku.model.json',
  'INTJ-A': '/live2d/all/shizuku/shizuku.model.json',
  'INTJ-T': '/live2d/all/shizuku/shizuku.model.json',
  'INTP': '/live2d/all/shizuku/shizuku.model.json',
  'INTP-A': '/live2d/all/shizuku/shizuku.model.json',
  'INTP-T': '/live2d/all/shizuku/shizuku.model.json',
  'ENTJ': '/live2d/all/shizuku/shizuku.model.json',
  'ENTJ-A': '/live2d/all/shizuku/shizuku.model.json',
  'ENTJ-T': '/live2d/all/shizuku/shizuku.model.json',
  'ENTP': '/live2d/all/shizuku/shizuku.model.json',
  'ENTP-A': '/live2d/all/shizuku/shizuku.model.json',
  'ENTP-T': '/live2d/all/shizuku/shizuku.model.json',
  'INFJ': '/live2d/all/shizuku/shizuku.model.json',
  'INFJ-A': '/live2d/all/shizuku/shizuku.model.json',
  'INFJ-T': '/live2d/all/shizuku/shizuku.model.json',
  'INFP': '/live2d/all/shizuku/shizuku.model.json',
  'INFP-A': '/live2d/all/shizuku/shizuku.model.json',
  'INFP-T': '/live2d/all/shizuku/shizuku.model.json',
  'ENFJ': '/live2d/all/umaru/model.json',
  'ENFJ-A': '/live2d/all/umaru/model.json',
  'ENFJ-T': '/live2d/all/umaru/model.json',
  'ENFP': '/live2d/all/umaru/model.json',
  'ENFP-A': '/live2d/all/umaru/model.json',
  'ENFP-T': '/live2d/all/umaru/model.json',
  'ISTJ': '/live2d/all/chino/model.json',
  'ISTJ-A': '/live2d/all/chino/model.json',
  'ISTJ-T': '/live2d/all/chino/model.json',
  'ISFJ': '/live2d/all/umaru/model.json',
  'ISFJ-A': '/live2d/all/umaru/model.json',
  'ISFJ-T': '/live2d/all/umaru/model.json',
  'ESTJ': '/live2d/all/chino/model.json',
  'ESTJ-A': '/live2d/all/chino/model.json',
  'ESTJ-T': '/live2d/all/chino/model.json',
  'ESFJ': '/live2d/all/umaru/model.json',
  'ESFJ-A': '/live2d/all/umaru/model.json',
  'ESFJ-T': '/live2d/all/umaru/model.json',
  'ISTP': '/live2d/all/chino/model.json',
  'ISTP-A': '/live2d/all/chino/model.json',
  'ISTP-T': '/live2d/all/chino/model.json',
  'ISFP': '/live2d/all/rem/model.json',
  'ISFP-A': '/live2d/all/rem/model.json',
  'ISFP-T': '/live2d/all/rem/model.json',
  'ESTP': '/live2d/all/HK416-1-normal/model.json',
  'ESTP-A': '/live2d/all/HK416-1-normal/model.json',
  'ESTP-T': '/live2d/all/HK416-1-normal/model.json',
  'ESFP': '/live2d/all/rem/model.json',
  'ESFP-A': '/live2d/all/rem/model.json',
  'ESFP-T': '/live2d/all/rem/model.json',
  'default': '/live2d/all/shizuku/shizuku.model.json',
}

// 根据 MBTI 类型获取模型路径
export function getModelPathByMBTI(mbti: string): string {
  // 尝试完整匹配（如 INTJ-A, INTJ-T）
  if (MBTI_LIVE2D_MODELS[mbti]) {
    return MBTI_LIVE2D_MODELS[mbti]
  }

  // 尝试基础类型匹配（取前4个字符）
  const baseType = mbti.substring(0, 4)
  if (MBTI_LIVE2D_MODELS[baseType]) {
    return MBTI_LIVE2D_MODELS[baseType]
  }

  // 返回默认模型
  return MBTI_LIVE2D_MODELS['default']
}

// 获取所有模型路径（用于预加载）
export function getAllModelPaths(): string[] {
  const paths = new Set<string>()
  Object.values(MBTI_LIVE2D_MODELS).forEach(path => paths.add(path))
  return Array.from(paths)
}

// 默认模型路径
export const DEFAULT_MODEL_PATH = MBTI_LIVE2D_MODELS['default']
