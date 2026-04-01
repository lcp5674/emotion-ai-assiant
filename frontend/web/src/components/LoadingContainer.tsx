import { ReactNode } from 'react';
import { Spin, Card, Row, Col } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingContainerProps {
  loading: boolean;
  children: ReactNode;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
  errorText?: string;
  fullScreen?: boolean;
  withCard?: boolean;
}

/**
 * 加载状态容器组件
 * 统一管理加载、错误、空状态的显示
 */
export const LoadingContainer: React.FC<LoadingContainerProps> = ({
  loading,
  children,
  error,
  empty = false,
  emptyText = '暂无数据',
  errorText = '加载失败，请重试',
  fullScreen = true,
  withCard = true,
}) => {
  // 加载状态
  if (loading) {
    const loadingContent = (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: fullScreen ? '100vh' : '200px',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <Spin
          indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
          size="large"
        />
        <div style={{ color: '#8c8c8c', fontSize: '14px' }}>加载中...</div>
      </div>
    );

    return withCard ? <Card>{loadingContent}</Card> : loadingContent;
  }

  // 错误状态
  if (error) {
    const errorContent = (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: fullScreen ? '100vh' : '200px',
          flexDirection: 'column',
          gap: '16px',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '48px', color: '#ff4d4f' }}>⚠️</div>
        <div style={{ color: '#ff4d4f', fontSize: '16px', fontWeight: 500 }}>
          {errorText}
        </div>
        <div style={{ color: '#8c8c8c', fontSize: '14px' }}>{error}</div>
        <button
          onClick={() => window.location.reload()}
          style={{
            backgroundColor: '#722ed1',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer',
            marginTop: '8px',
          }}
        >
          重试
        </button>
      </div>
    );

    return withCard ? <Card>{errorContent}</Card> : errorContent;
  }

  // 空状态
  if (empty) {
    const emptyContent = (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: fullScreen ? '100vh' : '200px',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <div style={{ fontSize: '48px', color: '#bfbfbf' }}>📭</div>
        <div style={{ color: '#8c8c8c', fontSize: '16px' }}>
          {emptyText}
        </div>
      </div>
    );

    return withCard ? <Card>{emptyContent}</Card> : emptyContent;
  }

  // 正常状态
  return <>{children}</>;
};

interface SkeletonCardProps {
  count?: number;
}

/**
 * 骨架屏卡片组件
 * 用于列表和网格加载状态
 */
export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  count = 4,
}) => {
  const cards = Array(count).fill(0).map((_, index) => (
    <Col key={index} xs={24} sm={12} lg={6}>
      <div
        style={{
          height: '200px',
          background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
          backgroundSize: '200% 100%',
          borderRadius: '8px',
        }}
      />
    </Col>
  ));

  return (
    <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
      {cards}
    </Row>
  );
};
