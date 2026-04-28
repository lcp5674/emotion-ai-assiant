#!/bin/bash
# Live2D模型下载脚本
# 使用方法: bash scripts/download-live2d-models.sh

set -e

MODEL_DIR="frontend/web/public/live2d/default"
mkdir -p "$MODEL_DIR"

echo "开始下载Live2D示例模型..."

# 尝试从多个源下载模型
# 注意：这些模型需要符合Live2D免费素材协议

# 示例1: Shizuku (Cubism 2.1)
# 由于网络环境限制，这些URL可能需要用户手动下载

echo ""
echo "=========================================="
echo "下载说明"
echo "=========================================="
echo ""
echo "由于网络环境限制，请手动下载Live2D模型："
echo ""
echo "推荐方案1: Live2D官方示例"
echo "  1. 访问 https://www.live2d.com/learn/sample/"
echo "  2. 下载 FREE 版本的示例模型（如 Mark-kun 或 Hiyori）"
echo "  3. 解压后将 model3.json 放置到 $MODEL_DIR/"
echo ""
echo "推荐方案2: GitHub开源模型"
echo "  1. 访问 https://github.com/hacxy/l2d-models"
echo "  2. 或访问 https://github.com/Eikanya/Live2d-model"
echo "  3. 下载模型文件并放置到 $MODEL_DIR/"
echo ""
echo "推荐方案3: Booth (日本模型商店)"
echo "  1. 访问 https://booth.pm/"
echo "  2. 搜索免费的 Live2D 模型"
echo "  3. 下载后放置到 $MODEL_DIR/"
echo ""
echo "注意事项："
echo "  - 需要包含 model3.json 文件的主模型文件"
echo "  - 模型文件应包含 .moc3, .texture.png 等资源"
echo "  - 确保模型文件名与代码中的路径匹配"
echo ""
echo "当前支持的模型路径: $MODEL_DIR/model.json"
echo ""

# 创建一个示例配置文件
cat > "$MODEL_DIR/README.md" << 'EOF'
# Live2D模型目录

请在此目录下放置您的Live2D模型文件。

## 文件结构

```
live2d/
└── default/
    ├── model.json          # 主模型配置文件 (必需)
    ├── model.1024/
    │   └── texture_00.png  # 纹理文件
    ├── model.1024.meta.json
    ├── expressions/        # 表情文件
    │   └── happy.exp3.json
    └── motions/            # 动作文件
        └── idle.motion3.json
```

## 如何获取模型

1. **Live2D官方示例**: https://www.live2d.com/learn/sample/
2. **GitHub开源模型**: https://github.com/hacxy/l2d-models
3. **模之屋**: https://www.aplaybox.com/model/model
4. **Booth**: https://booth.pm/

## 配置说明

修改 `frontend/web/src/views/chat.tsx` 中的 `modelPath` 参数来使用不同的模型：

```jsx
<Live2DCanvas
  modelPath="/live2d/default/model.json"
  ...
/>
```
EOF

echo "配置文件已创建: $MODEL_DIR/README.md"
echo ""
echo "请手动下载Live2D模型文件后重新启动开发服务器。"
echo "=========================================="