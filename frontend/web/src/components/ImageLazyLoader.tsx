import { useState, useEffect, useRef } from 'react';

interface ImageLazyLoaderProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  fallbackSrc?: string;
  width?: number | string;
  height?: number | string;
  threshold?: number;
  rootMargin?: string;
}

/**
 * 图片懒加载组件
 * 当图片进入视口时才加载
 */
export const ImageLazyLoader: React.FC<ImageLazyLoaderProps> = ({
  src,
  alt,
  className = '',
  style = {},
  fallbackSrc,
  width,
  height,
  threshold = 0.1,
  rootMargin = '50px',
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [displaySrc, setDisplaySrc] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setDisplaySrc(src);
            observer.unobserve(imgRef.current!);
          }
        });
      },
      {
        rootMargin,
        threshold,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [src, rootMargin, threshold]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    if (fallbackSrc) {
      setDisplaySrc(fallbackSrc);
    }
  };

  const imageStyle: React.CSSProperties = {
    opacity: isLoaded ? 1 : 0,
    transition: 'opacity 0.3s ease-in-out',
    width,
    height,
    ...style,
  };

  return (
    <img
      ref={imgRef}
      src={displaySrc || fallbackSrc || '/placeholder.png'}
      alt={alt}
      className={`image-lazy-loader ${className}`}
      style={imageStyle}
      onLoad={handleLoad}
      onError={handleError}
    />
  );
};

// 骨架屏组件
interface ImageSkeletonProps {
  width?: number | string;
  height?: number | string;
  style?: React.CSSProperties;
  className?: string;
}

export const ImageSkeleton: React.FC<ImageSkeletonProps> = ({
  width = '100%',
  height = '200px',
  style,
  className,
}) => {
  const skeletonStyle: React.CSSProperties = {
    width,
    height,
    background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
    backgroundSize: '200% 100%',
    borderRadius: '8px',
    ...style,
  };

  return (
    <div
      className={`image-skeleton ${className}`}
      style={skeletonStyle}
    />
  );
};
