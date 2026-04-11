import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { LoadingContainer, SkeletonCard } from './LoadingContainer'

// 模拟 window.location.reload
vi.mock('window', () => ({
  location: {
    reload: vi.fn()
  }
}))

describe('LoadingContainer Component', () => {
  it('renders loading state when loading is true', () => {
    render(
      <LoadingContainer loading={true}>
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('加载中...')).toBeTruthy()
  })

  it('renders error state when error is provided', () => {
    render(
      <LoadingContainer loading={false} error="加载失败">
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('加载失败，请重试')).toBeTruthy()
    expect(screen.getByText('加载失败')).toBeTruthy()
  })

  it('renders empty state when empty is true', () => {
    render(
      <LoadingContainer loading={false} empty={true}>
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('暂无数据')).toBeTruthy()
  })

  it('renders custom empty text when emptyText is provided', () => {
    render(
      <LoadingContainer loading={false} empty={true} emptyText="没有找到数据">
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('没有找到数据')).toBeTruthy()
  })

  it('renders children when no loading, error, or empty', () => {
    render(
      <LoadingContainer loading={false}>
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('正常内容')).toBeTruthy()
  })

  it('calls window.location.reload when retry button is clicked', () => {
    render(
      <LoadingContainer loading={false} error="加载失败">
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    const retryButton = screen.getByText('重试')
    fireEvent.click(retryButton)
    
    expect(window.location.reload).toHaveBeenCalled()
  })

  it('renders without card when withCard is false', () => {
    render(
      <LoadingContainer loading={true} withCard={false}>
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('加载中...')).toBeTruthy()
  })

  it('renders with custom error text when errorText is provided', () => {
    render(
      <LoadingContainer loading={false} error="网络错误" errorText="网络连接失败">
        <div>正常内容</div>
      </LoadingContainer>
    )
    
    expect(screen.getByText('网络连接失败')).toBeTruthy()
  })
})

describe('SkeletonCard Component', () => {
  it('renders default number of skeleton cards (4)', () => {
    const { container } = render(<SkeletonCard />)
    const cards = container.querySelectorAll('[style*="background: linear-gradient"]')
    expect(cards.length).toBe(4)
  })

  it('renders specified number of skeleton cards', () => {
    const { container } = render(<SkeletonCard count={6} />)
    const cards = container.querySelectorAll('[style*="background: linear-gradient"]')
    expect(cards.length).toBe(6)
  })
})
