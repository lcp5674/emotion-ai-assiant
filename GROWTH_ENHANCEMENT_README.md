# 成长与激励模块增强实现说明

## 概述

本文档详细说明成长与激励模块的增强功能实现，包括丰富的成长体系、多样化激励机制和智能任务系统。

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── growth_models_enhanced.py     # 增强数据模型
│   ├── schemas/
│   │   └── growth_schemas_enhanced.py    # 增强 Schema 定义
│   └── services/
│       ├── growth_service_enhanced.py    # 增强成长服务
│       └── smart_task_system.py          # 智能任务系统
└── GROWTH_ENHANCEMENT_README.md          # 本文档
```

## 1. 丰富的成长体系

### 1.1 更多等级和晋升路径

**实现文件**: `growth_service_enhanced.py`

- **等级扩展**: 从原来的20级扩展到50级
- **经验配置**: `EXTENDED_LEVEL_EXP` 字典定义了每一级所需的经验值
- **递增曲线**: 采用平滑递增的经验需求曲线，确保后期成长更具挑战性

### 1.2 多维度成长指标

**实现文件**: `growth_models_enhanced.py`, `growth_service_enhanced.py`

**六大成长维度**:
- `emotional_health` - 情感健康
- `self_awareness` - 自我认知
- `social_skills` - 社交能力
- `resilience` - 心理韧性
- `creativity` - 创造力
- `mindfulness` - 正念觉察

**核心功能**:
- 每个维度独立计算等级、经验和评分 (0-100分)
- 评分历史记录，便于追踪成长轨迹
- 维度经验配置: `DIMENSION_LEVEL_EXP`

**主要方法**:
```python
# 获取或创建用户的所有维度
get_or_create_user_dimensions(db, user_id)

# 为特定维度添加经验
add_dimension_exp(db, user_id, dimension, exp, score_delta)

# 获取用户维度数据
get_user_dimensions(db, user_id)
```

### 1.3 专家称号系统

**实现文件**: `growth_models_enhanced.py`, `growth_service_enhanced.py`

**称号等级**:
- `novice` - 新手
- `apprentice` - 学徒
- `journeyman` - 熟练工
- `expert` - 专家
- `master` - 大师
- `grandmaster` - 宗师

**称号配置**:
- 每个称号关联特定成长维度
- 解锁条件: 维度等级 + 维度评分 + 特定徽章
- 支持称号装备系统 (同一时间只能装备一个称号)

**默认称号**:
- 情感探索者、情绪觉察者、情绪管理大师
- 自我发现者
- 社交探索者
- 坚韧初学者

**主要方法**:
```python
# 初始化称号数据
init_default_titles(db)

# 获取所有称号
get_all_titles(db)

# 获取用户已获得称号
get_user_titles(db, user_id)

# 检查并解锁新称号
check_and_unlock_titles(db, user_id)

# 装备称号
equip_title(db, user_id, user_title_id, is_equipped)
```

## 2. 多样化激励机制

### 2.1 稀有徽章和限定成就

**实现文件**: `growth_models_enhanced.py`, `growth_service_enhanced.py`

**徽章稀有度**:
- `common` - 普通
- `rare` - 稀有
- `epic` - 史诗
- `legendary` - 传说

**限定类型**:
- `none` - 不限定
- `seasonal` - 季节性限定
- `holiday` - 节日限定
- `anniversary` - 周年纪念
- `limited` - 限时活动

**高级特性**:
- 最大持有者数量限制
- 获得序号记录 (用于稀有编号展示)
- 时间限定 (start_time/end_time)
- 复杂条件配置 (condition_meta JSON字段)

**默认徽章**:
- 百日坚持
- 春日探索者 (2025春季限定)
- 新年先锋 (2026新年限定，限1000人)
- 一路同行 (一周年纪念)
- 完美月度
- 早起的鸟儿

**主要方法**:
```python
# 初始化增强徽章数据
init_default_enhanced_badges(db)

# 获取所有增强徽章
get_all_enhanced_badges(db)

# 获取用户增强徽章
get_user_enhanced_badges(db, user_id)

# 检查并解锁增强徽章
check_and_unlock_enhanced_badges(db, user_id)

# 设置徽章展示
set_enhanced_badge_display(db, user_id, user_badge_id, is_displayed, display_note)
```

### 2.2 连续打卡奖励倍增

**实现文件**: `growth_models_enhanced.py`, `growth_service_enhanced.py`

**倍数配置**:
```python
STREAK_MULTIPLIERS = {
    1: 1.0,    # 1天: 1倍
    3: 1.5,    # 3天: 1.5倍
    7: 2.0,    # 7天: 2倍
    14: 2.5,   # 14天: 2.5倍
    30: 3.0,   # 30天: 3倍
    60: 3.5,   # 60天: 3.5倍
    90: 4.0,   # 90天: 4倍
    180: 5.0,  # 180天: 5倍
    365: 10.0, # 365天: 10倍
}
```

**核心功能**:
- 连续天数计算与断连检测
- 历史最大连续天数记录
- 总登录次数统计
- 奖励自动发放

**主要方法**:
```python
# 获取或创建连续打卡记录
get_or_create_login_streak(db, user_id)

# 记录登录并计算奖励
record_login(db, user_id)

# 获取倍数
_get_streak_multiplier(streak_days)
```

### 2.3 特殊纪念日奖励

**实现文件**: `growth_models_enhanced.py`, `growth_service_enhanced.py`

**纪念日类型**:
- `registration` - 注册纪念日
- `usage` - 使用里程碑
- `milestone` - 特殊里程碑

**默认纪念日**:
- 第一周 (7天) - 100经验
- 第一个月 (30天) - 300经验
- 百日纪念 (100天) - 500经验
- 一周年 (365天) - 2000经验

**主要方法**:
```python
# 初始化纪念日数据
init_default_anniversaries(db)

# 获取所有纪念日
get_all_anniversaries(db)

# 检查并发放纪念日奖励
check_and_award_anniversaries(db, user_id)

# 获取用户纪念日记录
get_user_anniversaries(db, user_id)
```

## 3. 智能任务系统

### 3.1 AI生成个性化成长任务

**实现文件**: `smart_task_system.py`

**任务模板库**:
- 按维度和难度分类的丰富任务模板
- 六大维度 × 四种难度 = 完整任务体系
- 包含任务标题、描述、预计时间、奖励配置

**用户画像构建**:
```python
_build_user_profile(db, user_id)
```
- 维度评分分析
- 历史成功率统计
- 任务完成情况汇总

**任务生成方法**:
```python
generate_tasks(db, user_id, dimension=None, difficulty=None, count=1)
```
- 支持指定维度或自动选择
- 支持指定难度或自动计算
- 支持批量生成 (最多5个)

### 3.2 任务难度自适应调整

**实现文件**: `smart_task_system.py`

**难度算法**:
1. **基础难度**: 根据维度评分确定
   - 评分 < 40: easy
   - 40 ≤ 评分 < 70: medium
   - 评分 ≥ 70: hard

2. **成功率调整**: 根据历史任务成功率微调
   - 成功率 > 85%: +1难度
   - 成功率 < 30%: -1难度

**难度历史记录**:
- 保存每次任务的完成情况
- 记录用户反馈评分 (1-5分)
- 记录实际完成时间

**推荐任务**:
```python
get_recommended_tasks(db, user_id, count=3)
```
- 优先推荐最薄弱维度的任务
- 根据最优难度选择
- 自动补充确保推荐数量

**主要方法**:
```python
# 获取用户智能任务
get_user_smart_tasks(db, user_id, include_completed=False)

# 获取单个任务
get_task(db, user_id, task_id)

# 更新任务进度
update_task_progress(db, user_id, task_id, progress)

# 完成任务并领取奖励
complete_task(db, user_id, task_id, feedback_score, completion_time_minutes)

# 删除任务
delete_task(db, user_id, task_id)
```

## 4. 综合功能

### 4.1 数据初始化

```python
# 初始化所有增强模块数据
init_default_data(db)
```

### 4.2 成长概览

```python
# 获取完整的成长体系概览
get_growth_overview(db, user_id)
```

返回内容包括:
- 等级信息
- 所有维度数据
- 用户称号
- 徽章进度
- 连续打卡记录
- 纪念日记录
- 智能任务列表

## 5. 服务实例获取

```python
from app.services.growth_service_enhanced import get_growth_service_enhanced
from app.services.smart_task_system import get_smart_task_system

growth_service = get_growth_service_enhanced()
task_system = get_smart_task_system()
```

## 6. 使用示例

### 示例1: 用户登录

```python
from sqlalchemy.orm import Session
from app.services.growth_service_enhanced import get_growth_service_enhanced

db: Session = ...  # 获取数据库会话
user_id = 1

growth_service = get_growth_service_enhanced()
result = growth_service.record_login(db, user_id)

print(f"连续打卡: {result['streak'].current_streak}天")
print(f"获得经验: {result['bonus_exp']}")
print(f"倍数: x{result['multiplier']}")
```

### 示例2: 生成智能任务

```python
from app.services.smart_task_system import get_smart_task_system

task_system = get_smart_task_system()

# 生成3个推荐任务
tasks = task_system.generate_tasks(db, user_id, count=3)

for task in tasks:
    print(f"任务: {task.title}")
    print(f"描述: {task.description}")
    print(f"难度: {task.difficulty}")
```

### 示例3: 完成任务

```python
task_id = tasks[0].id
result = task_system.complete_task(
    db, 
    user_id, 
    task_id,
    feedback_score=5.0,
    completion_time_minutes=10
)

print(f"获得经验: {result['reward_exp']}")
```

### 示例4: 获取成长概览

```python
overview = growth_service.get_growth_overview(db, user_id)

print(f"等级: {overview['level_info']['current_level']}")
print(f"徽章进度: {overview['badges']['unlocked_count']}/{overview['badges']['total']}")
```

## 7. 数据库迁移说明

需要创建以下新表:
- `user_growth_dimensions` - 用户成长维度
- `expert_titles` - 专家称号定义
- `user_titles` - 用户称号记录
- `enhanced_badges` - 增强徽章定义
- `user_enhanced_badges` - 用户增强徽章记录
- `login_streaks` - 连续打卡记录
- `special_anniversaries` - 特殊纪念日定义
- `user_anniversaries` - 用户纪念日记录
- `smart_tasks` - 智能任务
- `task_difficulty_history` - 任务难度历史

## 8. 扩展建议

### 8.1 进一步扩展
- 接入真实AI API实现任务生成
- 添加更多任务模板
- 实现社交排行榜
- 添加好友系统和互动任务
- 实现更复杂的徽章解锁条件

### 8.2 性能优化
- 添加缓存层
- 批量操作优化
- 历史数据归档

## 总结

本增强模块提供了完整的成长与激励体系，包括:
- ✅ 50级成长体系 + 六大维度
- ✅ 专家称号系统
- ✅ 稀有徽章与限定成就
- ✅ 连续打卡奖励倍增
- ✅ 特殊纪念日奖励
- ✅ AI个性化任务生成
- ✅ 难度自适应调整
- ✅ 完整的推荐系统

所有功能已完整实现并可直接集成使用！
