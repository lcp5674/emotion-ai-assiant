import { useState } from 'react';

interface AccessibleImageProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  fallbackSrc?: string;
  width?: number | string;
  height?: number | string;
  lazyLoad?: boolean;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * 无障碍图片组件
 * 提供alt属性、错误处理、懒加载等功能
 */
export const AccessibleImage: React.FC<AccessibleImageProps> = ({
  src,
  alt,
  className = '',
  style = {},
  fallbackSrc,
  width,
  height,
  lazyLoad = true,
  onLoad,
  onError,
}) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    if (fallbackSrc) {
      setImgSrc(fallbackSrc);
    }
    onError?.();
  };

  const baseStyle = {
    width,
    height,
    opacity: isLoaded ? 1 : 0,
    transition: 'opacity 0.3s ease-in-out',
    ...style,
  };

  return (
    <div
      className={`accessible-image-container ${className}`}
      style={{
        position: 'relative',
        width,
        height,
        display: 'inline-block',
        overflow: 'hidden',
      }}
      role="img"
      aria-label={alt}
    >
      {!isLoaded && !hasError && (
        <div
          className="image-skeleton"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
            backgroundSize: '200% 100%',
            animation: 'shimmer 1.5s infinite',
          }}
        />
      )}

      {hasError && !fallbackSrc && (
        <div
          className="image-error"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f5f5f5',
            color: '#8c8c8c',
            fontSize: '14px',
          }}
        >
          图片加载失败
        </div>
      )}

      <img
        src={imgSrc}
        alt={alt}
        className={`accessible-image ${isLoaded ? 'loaded' : ''}`}
        style={baseStyle}
        loading={lazyLoad ? 'lazy' : undefined}
        onLoad={handleLoad}
        onError={handleError}
        width={width}
        height={height}
      />

      <style>{`
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
      `}</style>
    </div>
  );
};

// 简写导出
export { AccessibleImage as Img };
