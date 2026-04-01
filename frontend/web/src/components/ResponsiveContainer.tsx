import { ReactNode } from 'react';
import { useIsMobile } from '../hooks/useIsMobile';

interface ResponsiveContainerProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  mobileStyle?: React.CSSProperties;
  desktopStyle?: React.CSSProperties;
}

/**
 * 响应式容器组件
 * 根据屏幕尺寸自动应用不同的样式
 */
export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className = '',
  style = {},
  mobileStyle = {},
  desktopStyle = {},
}) => {
  const isMobile = useIsMobile();

  const mergedStyle = {
    ...style,
    ...(isMobile ? mobileStyle : desktopStyle),
  };

  return (
    <div className={`responsive-container ${className}`} style={mergedStyle}>
      {children}
    </div>
  );
};

interface ResponsiveGridProps {
  children: ReactNode;
  columns?: number;
  mobileColumns?: number;
  tabletColumns?: number;
  gap?: number;
  mobileGap?: number;
  className?: string;
}

/**
 * 响应式网格组件
 * 自动适应不同屏幕尺寸的列数
 */
export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  columns = 4,
  mobileColumns = 1,
  tabletColumns = 2,
  gap = 24,
  mobileGap = 16,
  className = '',
}) => {
  const isMobile = useIsMobile();

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: isMobile
      ? `repeat(${mobileColumns}, 1fr)`
      : window.innerWidth < 992
      ? `repeat(${tabletColumns}, 1fr)`
      : `repeat(${columns}, 1fr)`,
    gap: isMobile ? `${mobileGap}px` : `${gap}px`,
    width: '100%',
  };

  return (
    <div className={`responsive-grid ${className}`} style={gridStyle}>
      {children}
    </div>
  );
};

interface ResponsiveTextProps {
  children: ReactNode;
  as?: keyof JSX.IntrinsicElements;
  size?: 'xs' | 'sm' | 'base' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
  mobileSize?: 'xs' | 'sm' | 'base' | 'md' | 'lg' | 'xl';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  color?: string;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * 响应式文字组件
 * 自动适应不同屏幕尺寸的文字大小
 */
export const ResponsiveText: React.FC<ResponsiveTextProps> = ({
  children,
  as: Component = 'span',
  size = 'base',
  mobileSize,
  weight = 'normal',
  color,
  className = '',
  style = {},
}) => {
  const isMobile = useIsMobile();

  const sizeMap = {
    xs: '12px',
    sm: '13px',
    base: '14px',
    md: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '28px',
    '4xl': '36px',
  };

  const weightMap = {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  };

  const actualSize = isMobile && mobileSize ? mobileSize : size;

  const textStyle = {
    fontSize: sizeMap[actualSize],
    fontWeight: weightMap[weight],
    color: color,
    ...style,
  };

  return (
    <Component className={`responsive-text ${className}`} style={textStyle}>
      {children}
    </Component>
  );
};
