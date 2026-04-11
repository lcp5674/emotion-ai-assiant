import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from './ErrorBoundary'

// 测试用的错误组件
const ErrorComponent = () => {
  throw new Error('Test error')
}

// 测试用的正常组件
const NormalComponent = () => <div>正常组件</div>

describe('ErrorBoundary Component', () => {
  it('renders children normally when no error occurs', () => {
    render(
      <ErrorBoundary>
        <NormalComponent />
      </ErrorBoundary>
    )
    
    expect(screen.getByText('正常组件')).toBeTruthy()
  })

  it('renders error message when child component throws error', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    )
    
    expect(screen.getByText('页面加载出错')).toBeTruthy()
    expect(screen.getByText('抱歉，页面发生了错误，请尝试刷新')).toBeTruthy()
  })

  it('renders custom fallback when provided', () => {
    const CustomFallback = () => <div>自定义错误页面</div>
    
    render(
      <ErrorBoundary fallback={<CustomFallback />}>
        <ErrorComponent />
      </ErrorBoundary>
    )
    
    expect(screen.getByText('自定义错误页面')).toBeTruthy()
  })

  it('resets error state when retry button is clicked', () => {
    let shouldThrow = true
    
    const TestComponent = () => {
      if (shouldThrow) {
        throw new Error('Test error')
      }
      return <div>恢复正常</div>
    }
    
    const { rerender } = render(
      <ErrorBoundary>
        <TestComponent />
      </ErrorBoundary>
    )
    
    // 初始状态应该显示错误
    expect(screen.getByText('页面加载出错')).toBeTruthy()
    
    // 点击重试按钮
    const retryButton = screen.getByText('重试')
    fireEvent.click(retryButton)
    
    // 设置不再抛出错误
    shouldThrow = false
    
    // 重新渲染组件
    rerender(
      <ErrorBoundary>
        <TestComponent />
      </ErrorBoundary>
    )
    
    // 应该显示正常内容
    expect(screen.getByText('恢复正常')).toBeTruthy()
  })
})
