/**
 * Live2D 预加载和缓存模块 - 支持多版本 Cubism Core 动态适配
 */

let pixiPromise: Promise<any> | null = null
let live2dPromise: Promise<any> | null = null
const modelCache = new Map<string, any>()
const loadingPromises = new Map<string, Promise<any>>()

let cubismCoreVersion: 'v4' | 'v5' | 'unknown' = 'unknown'
const coreLoadPromises: Map<string, Promise<any>> = new Map()

export async function preloadLive2DLibraries(): Promise<{ PIXI: any; Live2DModel: any }> {
  if (!pixiPromise) {
    pixiPromise = import('pixi.js').then(m => m.default || m)
  }
  if (!live2dPromise) {
    live2dPromise = import('pixi-live2d-display').then(m => m.Live2DModel || m)
  }

  const [PIXI, Live2DModel] = await Promise.all([pixiPromise, live2dPromise])
  return { PIXI, Live2DModel }
}

async function loadCubismCore(version: 'v4' | 'v5'): Promise<any> {
  const cacheKey = `cubism_core_${version}`
  
  if (coreLoadPromises.has(cacheKey)) {
    return coreLoadPromises.get(cacheKey)
  }

  const loadPromise = (async () => {
    if (version === 'v5') {
      // 优先从本地加载 Cubism 5 Core
      const script = document.createElement('script')
      script.src = '/live2d/live2dcubismcore.min.js'
      
      return new Promise((resolve, reject) => {
        script.onload = () => {
          cubismCoreVersion = 'v5'
          console.log('成功从本地加载 Cubism 5 Core')
          resolve((window as any).Live2DCubismCore)
        }
        script.onerror = () => {
          console.warn('本地加载失败，尝试从 CDN 加载 Cubism 5 Core')
          // 回退到 CDN
          const cdnScript = document.createElement('script')
          cdnScript.src = 'https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js'
          cdnScript.onload = () => {
            cubismCoreVersion = 'v5'
            console.log('从 CDN 回退加载 Cubism 5 Core 成功')
            resolve((window as any).Live2DCubismCore)
          }
          cdnScript.onerror = () => {
            reject(new Error('Cubism 5 Core 加载失败'))
          }
          document.head.appendChild(cdnScript)
        }
        document.head.appendChild(script)
      })
    } else {
      cubismCoreVersion = 'v4'
      return Promise.resolve((window as any).Live2DCubismCore)
    }
  })()

  coreLoadPromises.set(cacheKey, loadPromise)
  return loadPromise
}

async function detectModelVersion(modelPath: string): Promise<'v4' | 'v5'> {
  try {
    const response = await fetch(modelPath)
    const modelJson = await response.json()
    if (modelJson.moc && modelJson.moc.includes('moc3')) {
      return 'v5'
    }
    return 'v4'
  } catch {
    return 'v4'
  }
}

export function getCachedLive2DModel(path: string): any | undefined {
  return modelCache.get(path)
}

export function setCachedLive2DModel(path: string, model: any): void {
  modelCache.set(path, model)
}

export async function loadLive2DModel(
  path: string,
  Live2DModel: any,
  options?: any
): Promise<any> {
  const cached = modelCache.get(path)
  // 验证缓存的模型是否有效
  if (cached && cached.anchor && cached.scale && cached.position && cached.width > 0 && cached.height > 0) {
    return cached
  }

  if (cached) {
    console.log('Live2D 缓存无效，重新加载:', path)
    modelCache.delete(path)
  }

  const existing = loadingPromises.get(path)
  if (existing) {
    return existing
  }

  console.log('Live2D 加载新模型:', path)
  
  const loadWithFallback = async (): Promise<any> => {
    try {
      const model = await Live2DModel.from(path, { ...options, coreVersion: 'v4' })
      // 验证模型是否加载成功
      if (model && model.width > 0 && model.height > 0) {
        setCachedLive2DModel(path, model)
        return model
      }
      throw new Error('模型加载后验证失败')
    } catch (v4Error: any) {
      const errorMsg = String(v4Error)
      console.warn('v4加载失败，尝试v5:', errorMsg)
      
      // 尝试v5
      if (errorMsg.includes('moc3') || errorMsg.includes('unsupport') || errorMsg.includes('Invalid')) {
        try {
          await loadCubismCore('v5')
          const model = await Live2DModel.from(path, { ...options })
          if (model && model.width > 0 && model.height > 0) {
            setCachedLive2DModel(path, model)
            return model
          }
          throw new Error('v5模型加载后验证失败')
        } catch (v5Error) {
          console.error('v5也加载失败:', v5Error)
          throw v4Error
        }
      }
      throw v4Error
    }
  }

  const loadPromise = loadWithFallback().catch((error: any) => {
    console.error('模型加载最终失败:', path, error)
    loadingPromises.delete(path)
    // 不缓存失败的模型
    throw error
  })

  loadingPromises.set(path, loadPromise)
  return loadPromise
}

export function clearModelCache(): void {
  modelCache.clear()
}

export async function warmupModel(path: string, Live2DModel: any): Promise<void> {
  if (!modelCache.has(path) && !loadingPromises.has(path)) {
    await loadLive2DModel(path, Live2DModel)
  }
}

export function isModelCached(path: string): boolean {
  return modelCache.has(path)
}

export async function preloadModels(modelPaths: string[], Live2DModel: any): Promise<void> {
  await Promise.all(modelPaths.map(path => warmupModel(path, Live2DModel)))
}

// 预加载指定模型（不等待结果，用于后台预热）
export function preloadModelsInBackground(modelPaths: string[]): void {
  // 动态加载 Live2DModel
  import('pixi-live2d-display').then(m => {
    const Live2DModel = m.Live2DModel || m
    modelPaths.forEach((path, index) => {
      setTimeout(() => {
        if (!modelCache.has(path) && !loadingPromises.has(path)) {
          warmupModel(path, Live2DModel).catch(() => {})
        }
      }, index * 200) // 错开加载时间
    })
  }).catch(console.warn)
}

export function getCubismCoreVersion(): string {
  return cubismCoreVersion
}

// 默认要预加载的模型列表 - 已知可用的模型
const DEFAULT_PRELOAD_MODELS = [
  '/live2d/all/shizuku/shizuku.model.json',
  '/live2d/all/rem/model.json',
  '/live2d/all/umaru/model.json',
  '/live2d/all/chino/model.json',
  '/live2d/all/HK416-1-normal/model.json',
  '/live2d/all/hibiki/hibiki.model.json',
  '/live2d/all/mai/model.json',
  '/live2d/all/Pio/model.json',
  '/live2d/all/tia/model.json',
  '/live2d/all/koharu/model.json',
]

let preloadingStarted = false

export async function startBackgroundPreload(): Promise<void> {
  if (preloadingStarted) return
  preloadingStarted = true
  
  try {
    const { Live2DModel } = await preloadLive2DLibraries()
    
    // 使用 requestIdleCallback 在浏览器空闲时预加载
    const preloadInBackground = () => {
      DEFAULT_PRELOAD_MODELS.forEach((path, index) => {
        setTimeout(() => {
          if (!modelCache.has(path)) {
            warmupModel(path, Live2DModel).catch(() => {})
          }
        }, index * 100) // 错开加载时间，避免同时发起太多请求
      })
    }
    
    if ('requestIdleCallback' in window) {
      (window as any).requestIdleCallback(preloadInBackground, { timeout: 5000 })
    } else {
      preloadInBackground()
    }
  } catch (e) {
    console.warn('模型预加载启动失败:', e)
  }
}
