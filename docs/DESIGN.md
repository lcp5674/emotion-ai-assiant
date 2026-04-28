# 心灵伴侣AI - 设计规范 (DESIGN.md)

> 本设计规范用于 AI 编码代理生成符合品牌风格的 UI。参考 Intercom、Claude 等 AI 产品的设计系统。

---

## 1. Visual Theme & Atmosphere

**整体氛围**: 温暖、治愈、专业、可信赖

**设计理念**:
- 情感支持类AI产品需要传递安全感和被理解的感觉
- 使用柔和的圆角和渐变，营造温暖的视觉体验
- 避免过于冰冷的技术感，增加人情味
- 紫色系作为主色调，传递智慧、创造力和高端感

**情感关键词**: 温暖 | 专业 | 可信赖 | 陪伴 | 成长

---

## 2. Color Palette & Roles

### 主色调 (Primary)
| 名称 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Primary | `#722ED1` | 114, 46, 209 | 主按钮、链接、重点强调 |
| Primary Light | `#9B59E4` | 155, 89, 228 | 悬停状态、次级强调 |
| Primary Dark | `#5B1FAD` | 91, 31, 173 | 按下状态 |

### 功能色 (Functional)
| 名称 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Success | `#52C41A` | 82, 196, 26 | 成功状态、积极情绪 |
| Warning | `#FAAD14` | 250, 173, 20 | 警告状态 |
| Error | `#FF4D4F` | 255, 77, 79 | 错误状态、消极情绪 |
| Info | `#1890FF` | 24, 144, 255 | 信息提示 |

### 情绪色板 (Emotion Colors)
| 情绪 | Hex | 用途 |
|------|-----|------|
| 开心 | `#FFD700` | 开心/快乐情绪 |
| 平静 | `#74B9FF` | 平静/放松情绪 |
| 兴奋 | `#FF6B6B` | 兴奋情绪 |
| 难过 | `#A29BFE` | 难过情绪 |
| 生气 | `#FF4757` | 生气情绪 |
| 焦虑 | `#FD79A8` | 焦虑情绪 |
| 困惑 | `#00CEC9` | 困惑情绪 |
| 惊讶 | `#EB2F96` | 惊讶情绪 |

### 中性色 (Neutral)
| 名称 | Hex | 用途 |
|------|-----|------|
| Background | `#F5F5F5` | 页面背景 |
| Surface | `#FFFFFF` | 卡片、面板背景 |
| Border | `#E8E8E8` | 边框、分割线 |
| Text Primary | `#262626` | 主要文本 |
| Text Secondary | `#8C8C8C` | 次要文本 |
| Text Disabled | `#D9D9D9` | 禁用文本 |

### 渐变 (Gradients)
```
Primary Gradient: linear-gradient(135deg, #722ED1 0%, #9B59E4 100%)
Warm Gradient: linear-gradient(135deg, #FF6B6B 0%, #FFD700 100%)
Calm Gradient: linear-gradient(135deg, #74B9FF 0%, #A29BFE 100%)
```

---

## 3. Typography Rules

### 字体家族
```css
--font-family-primary: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
--font-family-mono: 'SF Mono', 'Fira Code', Consolas, monospace;
```

### 字体层级
| 层级 | 字号 | 字重 | 行高 | 用途 |
|------|------|------|------|------|
| h1 | 32px | 600 | 1.3 | 页面主标题 |
| h2 | 24px | 600 | 1.3 | 页面副标题 |
| h3 | 20px | 600 | 1.4 | 区块标题 |
| h4 | 16px | 600 | 1.4 | 卡片标题 |
| body | 14px | 400 | 1.6 | 正文内容 |
| body-small | 12px | 400 | 1.5 | 辅助文本 |
| caption | 10px | 400 | 1.4 | 标签文字 |

### 字重规范
```css
--font-weight-light: 300;
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

---

## 4. Component Stylings

### 按钮 (Button)

**主要按钮**
```css
/* 默认状态 */
background: #722ED1;
color: #FFFFFF;
border-radius: 8px;
padding: 12px 24px;
font-weight: 500;
transition: all 0.2s ease;

/* 悬停状态 */
background: #9B59E4;
box-shadow: 0 4px 12px rgba(114, 46, 209, 0.3);

/* 按下状态 */
background: #5B1FAD;
transform: translateY(1px);

/* 禁用状态 */
background: #D9D9D9;
color: #8C8C8C;
cursor: not-allowed;
```

**次要按钮**
```css
background: transparent;
color: #722ED1;
border: 1px solid #722ED1;
border-radius: 8px;
padding: 12px 24px;

/* 悬停状态 */
background: rgba(114, 46, 209, 0.1);
```

**幽灵按钮**
```css
background: transparent;
color: #8C8C8C;
border: none;
padding: 8px 16px;
```

### 卡片 (Card)

**基础卡片**
```css
background: #FFFFFF;
border-radius: 12px;
padding: 24px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
border: 1px solid #E8E8E8;
transition: box-shadow 0.2s ease;

/* 悬停状态 */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
```

**聊天消息卡片**
```css
/* 用户消息 */
background: #722ED1;
color: #FFFFFF;
border-radius: 16px 16px 4px 16px;
padding: 12px 16px;
max-width: 70%;
align-self: flex-end;

/* AI回复 */
background: #FFFFFF;
color: #262626;
border-radius: 16px 16px 16px 4px;
padding: 12px 16px;
max-width: 70%;
align-self: flex-start;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
```

### 输入框 (Input)

```css
/* 默认状态 */
background: #FFFFFF;
border: 1px solid #E8E8E8;
border-radius: 8px;
padding: 12px 16px;
font-size: 14px;
transition: border-color 0.2s ease, box-shadow 0.2s ease;

/* 聚焦状态 */
border-color: #722ED1;
box-shadow: 0 0 0 2px rgba(114, 46, 209, 0.1);
outline: none;

/* 错误状态 */
border-color: #FF4D4F;
box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.1);
```

### 标签 (Tag)

```css
/* 默认标签 */
background: rgba(114, 46, 209, 0.1);
color: #722ED1;
border-radius: 4px;
padding: 4px 8px;
font-size: 12px;
font-weight: 500;

/* 情绪标签（带颜色）*/
emotion-happy: background: rgba(255, 215, 0, 0.2); color: #B8860B;
emotion-calm: background: rgba(116, 185, 255, 0.2); color: #1890FF;
```

### 进度条 (Progress)

```css
/* 测评进度条 */
background: #E8E8E8;
border-radius: 8px;
height: 8px;
overflow: hidden;

.progress-fill {
  background: linear-gradient(90deg, #722ED1 0%, #9B59E4 100%);
  height: 100%;
  border-radius: 8px;
  transition: width 0.3s ease;
}
```

---

## 5. Layout Principles

### 间距系统
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
--spacing-3xl: 64px;
```

### 页面布局
```
移动端 (<768px): 单列布局，全宽卡片
平板端 (768-1024px): 双列网格，最大宽度 960px
桌面端 (>1024px): 三列布局，最大宽度 1200px
```

### 留白理念
- 内容区域与屏幕边缘保持 16px 边距（移动端）或 24px（桌面端）
- 区块之间保持 24px 间距
- 组件内部保持 12-16px 内边距
- 避免内容过于拥挤，保持呼吸感

### 容器圆角
```css
--radius-sm: 4px;    /* 标签、小按钮 */
--radius-md: 8px;    /* 输入框、中按钮 */
--radius-lg: 12px;   /* 卡片 */
--radius-xl: 16px;   /* 大卡片、聊天消息 */
--radius-full: 9999px; /* 圆形按钮、头像 */
```

---

## 6. Depth & Elevation

### 阴影层级
```css
/* 轻微阴影 - 默认卡片 */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

/* 中等阴影 - 悬停卡片 */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

/* 高阴影 - 弹窗、模态框 */
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);

/* 主色调阴影 - 主按钮悬停 */
box-shadow: 0 4px 12px rgba(114, 46, 209, 0.3);
```

### 层级 (z-index)
```css
--z-dropdown: 100;
--z-sticky: 200;
--z-modal-backdrop: 300;
--z-modal: 400;
--z-tooltip: 500;
--z-toast: 600;
```

### 边框
```css
/* 默认边框 */
border: 1px solid #E8E8E8;

/* 主色调边框（聚焦）*/
border: 1px solid #722ED1;
```

---

## 7. Do's and Don'ts

### Do's ✅

1. **使用圆角设计**
   - 所有卡片使用 12px 圆角
   - 按钮使用 8px 圆角
   - 输入框使用 8px 圆角

2. **保持一致的颜色应用**
   - 主按钮始终使用 `#722ED1`
   - 成功状态使用 `#52C41A`
   - 错误状态使用 `#FF4D4F`

3. **使用柔和的阴影**
   - 默认卡片使用轻微阴影
   - 避免使用过重的阴影

4. **保持足够的间距**
   - 组件之间至少 16px
   - 区块之间至少 24px

5. **使用渐变增加层次感**
   - 主按钮背景可使用渐变
   - 心情图表可使用情绪渐变

6. **响应式设计**
   - 移动端优先
   - 断点: 768px, 1024px

### Don'ts ❌

1. **不要使用过于尖锐的设计**
   - 避免使用 0px 圆角
   - 避免生硬的边缘

2. **不要混用色调**
   - 不要在同一界面使用多个主色
   - 不要混用不同风格的蓝色

3. **不要过度使用强调色**
   - 红色只用于错误和警告
   - 不要用红色作为装饰

4. **不要让内容过于拥挤**
   - 避免密不透风的布局
   - 每个卡片之间保持间距

5. **不要忽略可访问性**
   - 确保文本对比度足够
   - 确保交互元素足够大

---

## 8. Responsive Behavior

### 断点
```css
--breakpoint-sm: 576px;   /* 大手机 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 小桌面 */
--breakpoint-xl: 1200px;  /* 大桌面 */
```

### 响应式策略
- **移动端 (<768px)**:
  - 单列布局
  - 底部导航栏
  - 全宽按钮
  - 简化侧边栏为抽屉

- **平板端 (768-1024px)**:
  - 双列网格
  - 侧边栏可折叠
  - 卡片适度增大

- **桌面端 (>1024px)**:
  - 三列布局
  - 固定侧边栏
  - 悬停交互效果

### 触摸目标
- 最小触摸目标: 44px × 44px
- 按钮高度建议: 44-48px
- 列表项高度: 至少 48px

### 折叠策略
- 测评步骤: 桌面端显示侧边进度条，移动端收起为顶部进度条
- 助手列表: 桌面端侧边栏，移动端底部标签切换
- 设置选项: 桌面端标签页，移动端垂直列表

---

## 9. Agent Prompt Guide

### 快速颜色参考
```
主色: #722ED1 (紫色)
成功: #52C41A (绿色)
警告: #FAAD14 (黄色)
错误: #FF4D4F (红色)
背景: #F5F5F5 (浅灰)
文字: #262626 (深灰)
文字次: #8C8C8C (中灰)
```

### 常用样式模板

**创建卡片组件**
```tsx
<div style={{
  background: '#FFFFFF',
  borderRadius: '12px',
  padding: '24px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
  border: '1px solid #E8E8E8'
}}>
  {/* 卡片内容 */}
</div>
```

**创建主按钮**
```tsx
<button style={{
  background: '#722ED1',
  color: '#FFFFFF',
  borderRadius: '8px',
  padding: '12px 24px',
  fontWeight: 500,
  border: 'none',
  cursor: 'pointer'
}}>
  按钮文字
</button>
```

**创建聊天消息**
```tsx
// 用户消息
<div style={{
  background: '#722ED1',
  color: '#FFFFFF',
  borderRadius: '16px 16px 4px 16px',
  padding: '12px 16px',
  maxWidth: '70%'
}}>
  {message}
</div>

// AI回复
<div style={{
  background: '#FFFFFF',
  color: '#262626',
  borderRadius: '16px 16px 16px 4px',
  padding: '12px 16px',
  maxWidth: '70%',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
}}>
  {message}
</div>
```

**创建输入框**
```tsx
<input type="text" style={{
  background: '#FFFFFF',
  border: '1px solid #E8E8E8',
  borderRadius: '8px',
  padding: '12px 16px',
  fontSize: '14px',
  outline: 'none'
}} placeholder="请输入..." />
```

---

## 10. Icon & Emoji Guidelines

### 图标库
- 主要使用 **Ant Design Icons**
- 备选: Lucide React

### 情绪 Emoji 使用
| 情绪 | Emoji | Unicode |
|------|-------|---------|
| 开心 | 😊 | U+1F60A |
| 难过 | 😢 | U+1F622 |
| 生气 | 😠 | U+1F620 |
| 平静 | 😌 | U+1F60C |
| 兴奋 | 🎉 | U+1F389 |
| 焦虑 | 😰 | U+1F630 |
| 困惑 | 🤔 | U+1F914 |
| 惊讶 | 😮 | U+1F62E |
| 惊讶(替代) | 😲 | U+1F632 |
| 爱 | ❤️ | U+2764 |
| 思考 | 🤨 | U+1F928 |

### Emoji 尺寸规范
- 消息中: 24px
- 选择器中: 32px
- 心情打卡: 48px

---

## 11. Animation Guidelines

### 时长规范
```css
--duration-fast: 150ms;    /* 微交互 */
--duration-normal: 200ms;  /* 一般过渡 */
--duration-slow: 300ms;    /* 页面过渡 */
```

### 缓动函数
```css
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 常用动画
```css
/* 按钮悬停 */
transform: translateY(-2px);
box-shadow: 0 4px 12px rgba(114, 46, 209, 0.3);

/* 卡片悬停 */
transform: translateY(-4px);
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

/* 页面进入 */
opacity: 0;
transform: translateY(20px);
animation: fadeInUp 0.3s ease forwards;
```

---

## 12. Accessibility Guidelines

### 颜色对比度
- 正文文字与背景: 至少 4.5:1
- 大文字(18px+)与背景: 至少 3:1
- 交互元素与周围元素: 至少 3:1

### 焦点状态
```css
/* 键盘焦点指示器 */
outline: 2px solid #722ED1;
outline-offset: 2px;

/* 聚焦时移除默认轮廓 */
:focus-visible {
  outline: 2px solid #722ED1;
  outline-offset: 2px;
}
```

### 屏幕阅读器
- 使用语义化 HTML
- 添加 aria-label 给图标按钮
- 确保动态内容有 aria-live 通知

---

*本设计规范最后更新: 2026-04-24*
*版本: 1.0.0*
