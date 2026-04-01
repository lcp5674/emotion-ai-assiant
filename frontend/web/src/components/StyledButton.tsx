import { Button as AntButton, ButtonProps } from 'antd';
import { designTokens } from '../design/tokens';

/**
 * 统一的按钮组件
 * 基于Ant Design Button，使用设计系统样式
 */
export const StyledButton: React.FC<ButtonProps> = (props) => {
  const { type = 'default', size = 'middle', style, ...restProps } = props;

  // 基础样式
  const baseStyle: React.CSSProperties = {
    borderRadius: designTokens.borderRadius.md,
    fontWeight: designTokens.typography.fontWeight.medium,
    transition: `all ${designTokens.animation.duration.normal} ${designTokens.animation.easing.easeInOut}`,
  };

  const mergedStyle = {
    ...baseStyle,
    ...style,
  };

  return (
    <AntButton
      type={type}
      size={size}
      style={mergedStyle}
      {...restProps}
    />
  );
};
