# 性能优化指南

## 概述

本指南提供了心灵伴侣AI项目的前端性能优化最佳实践。

## 性能优化策略

### 1. 图片优化

**懒加载实现**：
```tsx
import { ImageLazyLoader, ImageSkeleton } from '../components';

<ImageLazyLoader
  src="/path/to/image.jpg"
  alt="描述文字"
  width={300}
  height={200}
  threshold={0.1}
  rootMargin="50px"
>
  <ImageSkeleton width={300} height={200} />
</ImageLazyLoader>
```

**图片格式建议**：
- 使用WebP格式（如果浏览器支持）
- 压缩图片文件大小
- 设置合适的尺寸

### 2. 组件懒加载

**路由级懒加载**：
```tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./views/home'));
const Login = lazy(() => import('./views/login'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

**组件级懒加载**：
```tsx
import { useState, useEffect, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function MyComponent() {
  const [showHeavy, setShowHeavy] = useState(false);

  return (
    <div>
      <button onClick={() => setShowHeavy(true)}>Show Heavy</button>
      {showHeavy && (
        <Suspense fallback={<div>Loading...</div>}>
          <HeavyComponent />
        </Suspense>
      )}
    </div>
  );
}
```

### 3. 代码分割

**动态导入**：
```typescript
// 按需导入
const utils = await import('./utils');
const data = await import(`./data-${id}`);

// 条件导入
if (isClient) {
  const { ClientComponent } = await import('./client');
} else {
  const { ServerComponent } = await import('./server');
}
```

### 4. 缓存策略

**组件缓存**：
```tsx
import { useMemo, useCallback } from 'react';

function MyComponent({ data }) {
  // 计算结果缓存
  const processedData = useMemo(() => {
    return expensiveCalculation(data);
  }, [data]);

  // 事件处理函数缓存
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);

  return (
    <div>
      <DataDisplay data={processedData} />
      <button onClick={handleClick}>Click</button>
    </div>
  );
}
```

### 5. 动画优化

**CSS动画优于JS动画**：
```css
/* 好的做法 */
.animate-slide {
  transition: transform 0.3s ease-in-out;
}

/* 避免 */
const animate = () => {
  requestAnimationFrame(() => {
    element.style.transform = `translateX(${position}px)`;
  });
};
```

### 6. 第三方库优化

**Tree Shaking优化**：
```javascript
// 好的做法（只导入需要的部分）
import { Button, Input } from 'antd';
import { message } from 'antd';

// 避免（导入整个库）
import * as antd from 'antd';
import { message as antdMessage } from 'antd/lib/message';
```

### 7. 构建优化

**Vite配置优化**：
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          antd: ['antd'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'antd'],
  },
});
```

## 性能监控

### 1. 监控指标

**Lighthouse指标**：
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- First Input Delay (FID)
- Time to Interactive (TTI)

**常用工具**：
- Lighthouse (Chrome DevTools)
- Web Vitals
- Performance API

### 2. 性能测试

**测试步骤**：
1. 清空缓存
2. 运行Lighthouse测试
3. 分析结果
4. 针对性优化
5. 重新测试验证

## 优化实践

### 首页优化

```tsx
// 优化前
import { useEffect, useState } from 'react';

function Home() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return <HomeContent data={data} />;
}

// 优化后
import { useEffect, useState, Suspense } from 'react';
const HomeContent = lazy(() => import('./HomeContent'));

function Home() {
  return (
    <Suspense fallback={<HomeSkeleton />}>
      <HomeContent />
    </Suspense>
  );
}
```

### 列表渲染优化

```tsx
import { useMemo } from 'react';

function ListComponent({ items }) {
  // 使用useMemo避免不必要的重渲染
  const renderedItems = useMemo(() => {
    return items.map(item => (
      <Item key={item.id} data={item} />
    ));
  }, [items]);

  return <div className="list">{renderedItems}</div>;
}
```

## 总结

性能优化是一个持续过程，需要定期监控和改进。重点关注：
1. 图片和资源加载优化
2. 组件懒加载和代码分割
3. 渲染和更新优化
4. 网络请求优化

通过遵循这些最佳实践，可以显著提升应用的加载速度和用户体验。
