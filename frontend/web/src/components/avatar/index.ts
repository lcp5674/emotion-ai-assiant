/**
 * Avatar Components - 虚拟形象组件导出
 */

export { default as AvatarCanvas, EXPRESSIONS, MOTIONS } from './AvatarCanvas'
export type { AvatarCanvasProps } from './AvatarCanvas'

export { default as Live2DCanvas, EXPRESSION_PARAMS, MOTION_GROUPS } from './Live2DCanvas'
export type { Live2DCanvasProps } from './Live2DCanvas'

export { default as AvatarController, useAvatarAnimation } from './AvatarController'
export type { AvatarControllerProps, AnimationState } from './AvatarController'