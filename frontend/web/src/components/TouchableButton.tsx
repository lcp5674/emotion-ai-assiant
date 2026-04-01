import { ButtonProps, Button as AntButton } from 'antd';
import { useState } from 'react';

interface TouchableButtonProps extends ButtonProps {
  onTap?: () => void;
  pressEffect?: boolean;
}

/**
 * 触摸优化的按钮组件
 * 支持更大的点击区域和触摸反馈
 */
export const TouchableButton: React.FC<TouchableButtonProps> = ({
  children,
  onTap,
  pressEffect = true,
  style,
  className,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);

  const handleMouseDown = () => {
    setIsPressed(true);
  };

  const handleMouseUp = () => {
    setIsPressed(false);
  };

  const handleMouseLeave = () => {
    setIsPressed(false);
  };

  const handleTouchStart = () => {
    setIsPressed(true);
  };

  const handleTouchEnd = () => {
    setIsPressed(false);
  };

  const handleClick = () => {
    onTap?.();
  };

  // 基础样式 - 确保最小点击区域
  const baseStyle: React.CSSProperties = {
    minWidth: '80px',
    minHeight: '32px',
  };

  // 按压效果
  const pressedStyle = pressEffect && isPressed ? {
    transform: 'scale(0.98)',
    opacity: 0.8,
  } as React.CSSProperties : {};

  const mergedStyle = {
    ...baseStyle,
    ...pressedStyle,
    ...style,
  };

  return (
    <AntButton
      className={`touchable-button ${className}`}
      style={mergedStyle}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onClick={handleClick}
      {...props}
    >
      {children}
    </AntButton>
  );
};

interface InteractiveCardProps {
  children: React.ReactNode;
  onClick?: () => void;
  style?: React.CSSProperties;
  className?: string;
}

/**
 * 交互式卡片组件
 * 支持悬停和点击效果
 */
export const InteractiveCard: React.FC<InteractiveCardProps> = ({
  children,
  onClick,
  style = {},
  className = '',
}) => {
  const cardStyle: React.CSSProperties = {
    background: '#ffffff',
    borderRadius: '8px',
    padding: '16px',
    cursor: onClick ? 'pointer' : 'default',
    ...style,
  };

  return (
    <div
      className={`interactive-card ${className}`}
      style={cardStyle}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
