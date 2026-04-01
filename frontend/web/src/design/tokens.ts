/**
 * 心灵伴侣AI 设计系统 - Design Tokens
 * 用于统一全局样式规范
 */

// ==========================================
// 颜色系统
// ==========================================
export const colors = {
  // 主色调 - 紫色渐变系列
  primary: {
    50: '#f9f0ff',
    100: '#efdbff',
    200: '#d3adf7',
    300: '#b37feb',
    400: '#9254de',
    500: '#722ed1',
    600: '#531dab',
    700: '#391085',
    800: '#22075e',
    900: '#120338',
  },

  // 功能色
  success: {
    50: '#f6ffed',
    100: '#d9f7be',
    500: '#52c41a',
    600: '#389e0d',
  },

  warning: {
    50: '#fffbe6',
    100: '#fff1b8',
    500: '#faad14',
    600: '#d48806',
  },

  error: {
    50: '#fff1f0',
    100: '#ffccc7',
    500: '#ff4d4f',
    600: '#cf1322',
  },

  // 中性色
  gray: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#f0f0f0',
    300: '#d9d9d9',
    400: '#bfbfbf',
    500: '#8c8c8c',
    600: '#595959',
    700: '#434343',
    800: '#262626',
    900: '#1f1f1f',
  },

  // 语义化别名
  text: {
    primary: '#262626',
    secondary: '#8c8c8c',
    tertiary: '#bfbfbf',
    disabled: '#d9d9d9',
    onPrimary: '#ffffff',
    onSecondary: '#262626',
  },

  background: {
    primary: '#ffffff',
    secondary: '#fafafa',
    tertiary: '#f5f5f5',
    overlay: 'rgba(0, 0, 0, 0.45)',
  },

  border: {
    default: '#d9d9d9',
    light: '#f0f0f0',
  },

  // 渐变
  gradients: {
    primary: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
    secondary: 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)',
    hero: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
  },

  // 阴影
  shadow: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.03)',
    md: '0 1px 3px rgba(0, 0, 0, 0.1)',
    lg: '0 4px 12px rgba(0, 0, 0, 0.15)',
    xl: '0 8px 24px rgba(0, 0, 0, 0.2)',
  },
};

// ==========================================
// 间距系统 (8px基准)
// ==========================================
export const spacing = {
  xxs: '4px',
  xs: '8px',
  sm: '12px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
};

// ==========================================
// 字体系统
// ==========================================
export const typography = {
  fontFamily: {
    sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },

  fontSize: {
    xs: '12px',
    sm: '13px',
    base: '14px',
    md: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '28px',
    '4xl': '36px',
    '5xl': '48px',
  },

  lineHeight: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },

  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // 语义化字体样式
  h1: {
    fontSize: '36px',
    lineHeight: '1.25',
    fontWeight: 700,
  },
  h2: {
    fontSize: '28px',
    lineHeight: '1.3',
    fontWeight: 600,
  },
  h3: {
    fontSize: '24px',
    lineHeight: '1.4',
    fontWeight: 600,
  },
  body: {
    fontSize: '14px',
    lineHeight: '1.5',
    fontWeight: 400,
  },
  small: {
    fontSize: '12px',
    lineHeight: '1.5',
    fontWeight: 400,
  },
};

// ==========================================
// 圆角系统
// ==========================================
export const borderRadius = {
  none: '0',
  sm: '4px',
  md: '6px',
  lg: '8px',
  xl: '12px',
  '2xl': '16px',
  full: '9999px',
};

// ==========================================
// 断点系统
// ==========================================
export const breakpoints = {
  xxs: '480px',   // 小屏手机
  xs: '576px',    // 手机
  sm: '768px',    // 平板竖屏
  md: '992px',    // 平板横屏
  lg: '1200px',   // 桌面小屏
  xl: '1600px',   // 桌面大屏
};

// ==========================================
// 动画系统
// ==========================================
export const animation = {
  duration: {
    fast: '0.15s',
    normal: '0.3s',
    slow: '0.5s',
  },

  easing: {
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  },
};

// ==========================================
// Z-index 层级
// ==========================================
export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
};

// ==========================================
// 导出完整设计系统
// ==========================================
export const designTokens = {
  colors,
  spacing,
  typography,
  borderRadius,
  breakpoints,
  animation,
  zIndex,
};

export default designTokens;
