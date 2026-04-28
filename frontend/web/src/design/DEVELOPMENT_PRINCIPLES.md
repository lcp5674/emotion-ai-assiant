# 前端开发设计原则

## 核心原则

### 1. 选择器/枚举类字段必须使用下拉菜单 + 中文显示

**原则描述：** 在管理系统（如Admin后台）中，所有具有预定义值的字段（如MBTI类型、SBTI主题、依恋风格等）必须使用下拉选择器（Select）而非文本输入框，并且选项必须使用中文显示，包含丰富的描述信息。

**实施要求：**
- 使用 `antd` 的 `Select` 组件
- 每个选项必须包含中文标签，格式：`{value} - {中文名称}: {详细描述}`
- 对于多值字段（如SBTI主题、依恋风格），使用 `mode="multiple"` 支持多选
- 提供搜索功能（设置 `showSearch` 和 `optionFilterProp`）

**示例：**

```typescript
// ❌ 错误：使用文本输入框
<Form.Item name="mbti_type" label="MBTI类型">
  <Input placeholder="如: ENFP, INFP" />
</Form.Item>

// ✅ 正确：使用下拉选择器 + 中文显示
const MBTI_TYPES = [
  { value: 'INFP', label: 'INFP - 调停者: 理想主义、富有同情心、追求意义' },
  { value: 'ENFP', label: 'ENFP - 竞选者: 热情洋溢、创意无限、善于激励' },
  // ...
]

<Form.Item name="mbti_type" label="MBTI类型">
  <Select
    placeholder="选择MBTI类型"
    showSearch
    allowClear
    optionFilterProp="label"
    options={MBTI_TYPES.map(m => ({ value: m.value, label: m.label }))}
  />
</Form.Item>
```

### 2. 数据提交格式转换

**原则描述：** 前端下拉选择器使用数组格式，后端API通常使用逗号分隔的字符串格式。提交数据时必须进行格式转换。

**实施要求：**
- 提交前：将数组转换为逗号分隔的字符串
- 编辑时：将逗号分隔的字符串解析为数组

**示例：**

```typescript
const handleSubmitAssistant = async () => {
  const values = await form.validateFields()
  const submitData = {
    ...values,
    sbti_types: Array.isArray(values.sbti_types) 
      ? values.sbti_types.join(',') 
      : (values.sbti_types || ''),
    attachment_styles: Array.isArray(values.attachment_styles) 
      ? values.attachment_styles.join(',') 
      : (values.attachment_styles || ''),
  }
  // 提交到API...
}

const handleEditAssistant = (record: Assistant) => {
  form.setFieldsValue({
    ...record,
    sbti_types: record.sbti_types 
      ? record.sbti_types.split(',').filter(Boolean) 
      : [],
    attachment_styles: record.attachment_styles 
      ? record.attachment_styles.split(',').filter(Boolean) 
      : [],
  })
}
```

### 3. 枚举值必须提供丰富的中文描述

**原则描述：** 每个枚举值的中文标签应该包含：
- 类型代码（如ISTJ）
- 中文名称（如物流师）
- 简要特征描述

**示例：**

```typescript
// MBTI类型
{ value: 'ISTJ', label: 'ISTJ - 物流师: 严谨务实、注重细节、责任心强' }

// SBTI主题
{ value: 'executing', label: '执行者 - 目标导向、决策果断、结果导向' }

// 依恋风格
{ value: 'secure', label: '安全型 - 信任他人、积极寻求亲密、情感稳定' }
```

### 4. 遵循本原则的场景

本原则适用于以下场景：
- 管理后台的增删改查表单
- 用户资料编辑页面
- AI助手配置页面
- 任何具有预定义枚举值的字段

### 5. 例外情况

如果预定义的选项无法满足需求，可以：
- 在下拉选项中添加"其他"选项
- 额外提供一个文本输入框作为补充
- 或在系统中设计可配置的枚举表

## 更新日志

- 2024-04-20: 初始版本，规定选择器必须使用下拉菜单 + 中文显示
