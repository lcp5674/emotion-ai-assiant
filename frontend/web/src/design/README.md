# 心灵伴侣AI - 设计系统文档

## 概述

这是心灵伴侣AI的设计系统文档，包含设计令牌、组件规范和最佳实践。

## 目录
- [设计令牌](#设计令牌)
- [组件规范](#组件规范)
- [响应式设计](#响应式设计)
- [可访问性](#可访问性)
- [使用示例](#使用示例)

---

## 设计令牌

### 颜色系统

#### 主色调（紫色）
```typescript
// 使用方式
import { designTokens } from '../components';

const primaryColor = designTokens.colors.primary[500];  // #722ed1
const lightPrimary = designTokens.colors.primary[300]; // #b37feb
const darkPrimary = designTokens.colors.primary[700];  // #391085
```

#### 功能色
- **Success**: #52c41a (成功/积极)
- **Warning**: #faad14 (警告/提示)
- **Error**: #ff4d4f (错误/危险)

#### 中性色
```
text.primary: #262626    // 主要文字
text.secondary: #8c8c8c   // 次要文字
text.tertiary: #bfbfbf    // 辅助文字
background.primary: #ffffff
background.secondary: #fafafa
background.tertiary: #f5f5f5
```

### 间距系统

使用8px基准间距：
```
xs: 4px   (0.5x)
sm: 8px   (1x)
md: 12px  (1.5x)
lg: 16px  (2x)
xl: 24px  (3x)
2xl: 32px (4x)
3xl: 48px (6x)
```

### 字体系统

```typescript
// 标题
h1: 36px / bold
h2: 28px / semibold
h3: 24px / semibold

// 正文
body: 14px / regular
small: 12px / regular
```

### 渐变和阴影

```css
/* 主渐变 */
--gradient-primary: linear-gradient(135deg, #722ed1 0%, #b37feb 100%);

/* 阴影 */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.03);
--shadow-md: 0 1px 3px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
```

---

## 组件规范

### StyledButton - 统一按钮

```tsx
import { StyledButton } from '../components';

// 主按钮
<StyledButton type="primary" size="large">
  主要操作
</StyledButton>

// 文字按钮
<StyledButton type="text">次要操作</StyledButton>

// 幽灵按钮（用于深色背景）
<StyledButton type="ghost" style={{ color: '#fff' }}>
  透明按钮
</StyledButton>
```

### AccessibleImage - 无障碍图片

```tsx
import { AccessibleImage } from '../components';

<AccessibleImage
  src="/path/to/image.jpg"
  alt="AI助手头像"
  width={80}
  height={80}
  fallbackSrc="/fallback.jpg"
  lazyLoad
/>
```

### LoadingContainer - 加载状态

```tsx
import { LoadingContainer, SkeletonCard } from '../components';

<LoadingContainer loading={loading} error={error} empty={data.length === 0}>
  <YourContent data={data} />
</LoadingContainer>

// 骨架屏
<SkeletonCard count={4} />
```

---

## 响应式设计

### 断点系统

```
xxs: 480px   // 小屏手机
xs: 576px    // 手机
sm: 768px    // 平板竖屏
md: 992px    // 平板横屏
lg: 1200px   // 桌面小屏
xl: 1600px   // 桌面大屏
```

### ResponsiveContainer - 响应式容器

```tsx
import { ResponsiveContainer, ResponsiveGrid, ResponsiveText } from '../components';

<ResponsiveContainer
  style={{ padding: '24px' }}
  mobileStyle={{ padding: '12px' }}
>
  内容
</ResponsiveContainer>
```

### ResponsiveGrid - 响应式网格

```tsx
<ResponsiveGrid
  columns={4}        // 桌面4列
  tabletColumns={2}  // 平板2列
  mobileColumns={1}  // 手机1列
  gap={24}
  mobileGap={16}
>
  {items.map(item => <Card key={item.id}>{item}</Card>)}
</ResponsiveGrid>
```

### ResponsiveText - 响应式文字

```tsx
<ResponsiveText
  as="h1"
  size="4xl"         // 桌面36px
  mobileSize="2xl"   // 手机24px
  weight="bold"
>
  标题文字
</ResponsiveText>
```

---

## 可访问性

### WCAG 2.0 AA 标准

#### 1. 文字对比度
- 普通文字：4.5:1 以上
- 大文字（18pt+）：3:1 以上

#### 2. 交互元素
- 最小点击区域：48px × 48px
- 所有按钮可通过Tab键访问
- 有清晰的焦点状态

#### 3. 图片和多媒体
- 所有图片必须有alt属性
- 装饰性图片：alt=""

### 使用示例

```tsx
// 良好的做法
<img src="avatar.jpg" alt="用户头像" />
<button aria-label="关闭对话框" onClick={close}>
  ✕
</button>

// 使用AccessibleImage组件
<AccessibleImage src="..." alt="描述性文字" />
```

---

## 使用示例

### 完整页面示例

```tsx
import {
  StyledButton,
  ResponsiveContainer,
  ResponsiveGrid,
  ResponsiveText,
  AccessibleImage,
  LoadingContainer,
  designTokens,
} from '../components';

function ExamplePage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div style={{ backgroundColor: designTokens.colors.background.tertiary }}>
      {/* 页面标题 */}
      <header style={{
        background: designTokens.colors.gradients.primary,
        padding: designTokens.spacing['3xl'],
        textAlign: 'center',
        color: designTokens.colors.text.onPrimary,
      }}>
        <ResponsiveText
          as="h1"
          size="4xl"
          mobileSize="2xl"
          weight="bold"
        >
          页面标题
        </ResponsiveText>
      </header>

      {/* 主内容 */}
      <main className="container" style={{ padding: designTokens.spacing.xl }}>
        <LoadingContainer loading={loading} error={error} empty={data.length === 0}>
          <ResponsiveGrid columns={4} tabletColumns={2} mobileColumns={1}>
            {data.map(item => (
              <div key={item.id} style={{
                background: designTokens.colors.background.primary,
                borderRadius: designTokens.borderRadius.lg,
                padding: designTokens.spacing.lg,
                boxShadow: designTokens.colors.shadow.md,
              }}>
                <AccessibleImage
                  src={item.image}
                  alt={item.title}
                  width="100%"
                  height={160}
                />
                <ResponsiveText as="h3" size="lg" weight="semibold">
                  {item.title}
                </ResponsiveText>
                <StyledButton type="primary" block>
                  查看详情
                </StyledButton>
              </div>
            ))}
          </ResponsiveGrid>
        </LoadingContainer>
      </main>
    </div>
  );
}
```

### 聊天界面优化

```tsx
import { useIsMobile } from '../hooks/useIsMobile';

function ChatInterface() {
  const isMobile = useIsMobile();

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* 侧边栏 - 桌面显示，移动端抽屉 */}
      {!isMobile ? (
        <Sidebar style={{ width: '280px' }} />
      ) : (
        <MobileDrawer />
      )}

      {/* 主聊天区 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatHeader />
        <MessagesArea />
        <ChatInput
          style={{
            padding: isMobile ? '12px' : '16px',
          }}
        />
      </div>
    </div>
  );
}
```

---

## 最佳实践清单

### 开发前
- [ ] 确认设计稿符合设计系统规范
- [ ] 确认响应式布局断点
- [ ] 确认可访问性需求

### 开发中
- [ ] 使用设计令牌而非硬编码颜色/间距
- [ ] 使用自定义组件（StyledButton等）
- [ ] 测试键盘导航和屏幕阅读器
- [ ] 验证在小屏设备上的显示

### 发布前
- [ ] 检查文字对比度
- [ ] 检查响应式布局在各断点的表现
- [ ] 检查加载状态和错误处理
- [ ] 验证所有图片有alt属性

---

## 迁移指南

### 从旧代码迁移

#### 1. 替换颜色
```typescript
// 旧代码
style={{ backgroundColor: '#722ed1' }}

// 新代码
import { designTokens } from '../components';
style={{ backgroundColor: designTokens.colors.primary[500] }}
```

#### 2. 替换按钮
```tsx
// 旧代码
import { Button } from 'antd';
<Button type="primary">按钮</Button>

// 新代码
import { StyledButton } from '../components';
<StyledButton type="primary">按钮</StyledButton>
```

#### 3. 替换图片
```tsx
// 旧代码
<img src={src} alt={alt} />

// 新代码
import { AccessibleImage } from '../components';
<AccessibleImage src={src} alt={alt} />
```

---

## 相关资源

- [Ant Design 5.x 文档](https://ant.design/)
- [WCAG 2.0 可访问性指南](https://www.w3.org/TR/WCAG20/)
- [Material Design 响应式指南](https://material.io/design/layout/responsive-layout-grid.html)
- [React 可访问性最佳实践](https://reactjs.org/docs/accessibility.html)

---

**文档版本**：V1.0
**最后更新**：2026年3月30日
**维护者**：UI/UX设计团队
