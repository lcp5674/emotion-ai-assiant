-- AI情感助手 数据库完整Schema
-- 版本: 2026-04-16
-- 包含所有表: 初始表 + 性格模型(SBTI, Attachment, DeepProfile) + 助手收藏表
-- 使用方法:
--   1. 创建数据库: CREATE DATABASE emotion_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--   2. 执行此脚本: mysql -u root -p emotion_ai < schema.sql
--   3. 或者使用Alembic: alembic upgrade head

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 枚举类型定义
-- ============================================

CREATE TYPE IF NOT EXISTS mbtitype AS ENUM('ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ');
CREATE TYPE IF NOT EXISTS mbtidimension AS ENUM('EI', 'SN', 'TF', 'JP');
CREATE TYPE IF NOT EXISTS memberlevel AS ENUM('FREE', 'VIP', 'SVIP', 'ENTERPRISE');
CREATE TYPE IF NOT EXISTS articlecategory AS ENUM('EMOTION', 'RELATIONSHIP', 'SELF_GROWTH', 'PSYCHOLOGY', 'LOVE', 'FAMILY', 'CAREER');
CREATE TYPE IF NOT EXISTS articlestatus AS ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED');

-- ============================================
-- 表: users (用户表)
-- ============================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `email` VARCHAR(255) DEFAULT NULL COMMENT '邮箱',
  `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
  `avatar` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
  `password_hash` VARCHAR(255) DEFAULT NULL COMMENT '密码哈希',
  `mbti_type` VARCHAR(4) DEFAULT NULL COMMENT 'MBTI类型',
  `mbti_result_id` INT DEFAULT NULL COMMENT 'MBTI结果ID',
  `sbti_result_id` INT DEFAULT NULL COMMENT 'SBTI结果ID',
  `attachment_result_id` INT DEFAULT NULL COMMENT '依恋风格结果ID',
  `member_level` ENUM('FREE', 'VIP', 'SVIP', 'ENTERPRISE') DEFAULT NULL COMMENT '会员等级',
  `member_expire_at` DATETIME DEFAULT NULL COMMENT '会员过期时间',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否激活',
  `is_verified` TINYINT(1) DEFAULT NULL COMMENT '是否验证',
  `is_deleted` TINYINT(1) DEFAULT NULL COMMENT '是否删除',
  `is_admin` TINYINT(1) DEFAULT NULL COMMENT '是否为管理员',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 表: ai_assistants (AI助手表)
-- ============================================
DROP TABLE IF EXISTS `ai_assistants`;
CREATE TABLE `ai_assistants` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '助手ID',
  `name` VARCHAR(50) NOT NULL COMMENT '助手名称',
  `avatar` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
  `mbti_type` ENUM('ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ') NOT NULL COMMENT 'MBTI类型',
  `personality` TEXT DEFAULT NULL COMMENT '性格描述',
  `speaking_style` TEXT DEFAULT NULL COMMENT '说话风格',
  `expertise` VARCHAR(500) DEFAULT NULL COMMENT '专长领域',
  `greeting` TEXT DEFAULT NULL COMMENT '开场白',
  `tags` VARCHAR(500) DEFAULT NULL COMMENT '标签,逗号分隔',
  `sbti_types` VARCHAR(200) DEFAULT NULL COMMENT 'SBTI类型,逗号分隔',
  `attachment_styles` VARCHAR(200) DEFAULT NULL COMMENT '依恋风格,逗号分隔',
  `is_recommended` TINYINT(1) DEFAULT NULL COMMENT '是否推荐',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否启用',
  `sort_order` INT DEFAULT NULL COMMENT '排序',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI助手表';

-- ============================================
-- 表: assistant_collections (AI助手收藏表) [新增]
-- ============================================
DROP TABLE IF EXISTS `assistant_collections`;
CREATE TABLE `assistant_collections` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `assistant_id` INT NOT NULL COMMENT '助手ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  INDEX `ix_assistant_collections_user_id` (`user_id`),
  INDEX `ix_assistant_collections_assistant_id` (`assistant_id`),
  UNIQUE INDEX `ix_assistant_collections_unique` (`user_id`, `assistant_id`),
  CONSTRAINT `fk_assistant_collections_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_assistant_collections_assistant` FOREIGN KEY (`assistant_id`) REFERENCES `ai_assistants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI助手收藏表';

-- ============================================
-- 表: mbti_questions (MBTI题目表)
-- ============================================
DROP TABLE IF EXISTS `mbti_questions`;
CREATE TABLE `mbti_questions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '题目ID',
  `dimension` ENUM('EI', 'SN', 'TF', 'JP') NOT NULL COMMENT '所属维度',
  `question_no` INT NOT NULL COMMENT '题目序号(1-48)',
  `question_text` TEXT NOT NULL COMMENT '题目内容',
  `option_a` VARCHAR(500) NOT NULL COMMENT '选项A',
  `option_b` VARCHAR(500) NOT NULL COMMENT '选项B',
  `weight_a` INT DEFAULT NULL COMMENT '选项A权重',
  `weight_b` INT DEFAULT NULL COMMENT '选项B权重',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MBTI题目表';

-- ============================================
-- 表: mbti_answers (MBTI答题记录表)
-- ============================================
DROP TABLE IF EXISTS `mbti_answers`;
CREATE TABLE `mbti_answers` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '答题记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `question_id` INT NOT NULL COMMENT '题目ID',
  `answer` VARCHAR(1) NOT NULL COMMENT '答案(A/B)',
  `score` INT NOT NULL COMMENT '得分',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`),
  INDEX `ix_mbti_answers_user_id` (`user_id`),
  INDEX `ix_mbti_answers_question_id` (`question_id`),
  CONSTRAINT `fk_mbti_answers_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_mbti_answers_question` FOREIGN KEY (`question_id`) REFERENCES `mbti_questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MBTI答题记录表';

-- ============================================
-- 表: mbti_results (MBTI结果表)
-- ============================================
DROP TABLE IF EXISTS `mbti_results`;
CREATE TABLE `mbti_results` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '结果ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `mbti_type` ENUM('ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ') NOT NULL COMMENT 'MBTI类型',
  `ei_score` INT NOT NULL DEFAULT 0 COMMENT '内外向得分',
  `sn_score` INT NOT NULL DEFAULT 0 COMMENT '感觉直觉得分',
  `tf_score` INT NOT NULL DEFAULT 0 COMMENT '思考情感得分',
  `jp_score` INT NOT NULL DEFAULT 0 COMMENT '判断知觉得分',
  `report_json` TEXT DEFAULT NULL COMMENT '完整报告JSON',
  `version` INT DEFAULT 1 COMMENT '报告版本',
  `is_latest` TINYINT(1) DEFAULT TRUE COMMENT '是否为最新结果',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_mbti_results_user_id` (`user_id`),
  INDEX `ix_mbti_results_is_latest` (`is_latest`),
  CONSTRAINT `fk_mbti_results_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MBTI结果表';

-- ============================================
-- 表: sbti_questions (SBTI题目表)
-- ============================================
DROP TABLE IF EXISTS `sbti_questions`;
CREATE TABLE `sbti_questions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '题目ID',
  `question_no` INT NOT NULL COMMENT '题目序号',
  `statement_a` TEXT NOT NULL COMMENT '陈述A',
  `theme_a` VARCHAR(50) NOT NULL COMMENT '主题A',
  `weight_a` INT DEFAULT 1 COMMENT '主题A权重',
  `statement_b` TEXT NOT NULL COMMENT '陈述B',
  `theme_b` VARCHAR(50) NOT NULL COMMENT '主题B',
  `weight_b` INT DEFAULT 1 COMMENT '主题B权重',
  `domain` VARCHAR(50) NOT NULL COMMENT '领域',
  `is_active` TINYINT(1) DEFAULT TRUE COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sbti_questions_question_no` (`question_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SBTI题目表';

-- ============================================
-- 表: sbti_answers (SBTI答题记录表)
-- ============================================
DROP TABLE IF EXISTS `sbti_answers`;
CREATE TABLE `sbti_answers` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '答题记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `question_id` INT NOT NULL COMMENT '题目ID',
  `answer` VARCHAR(1) NOT NULL COMMENT '答案(A/B)',
  `selected_theme` VARCHAR(50) NOT NULL COMMENT '选择的主题',
  `score` INT NOT NULL COMMENT '得分',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`),
  INDEX `ix_sbti_answers_user_id` (`user_id`),
  INDEX `ix_sbti_answers_question_id` (`question_id`),
  CONSTRAINT `fk_sbti_answers_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sbti_answers_question` FOREIGN KEY (`question_id`) REFERENCES `sbti_questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SBTI答题记录表';

-- ============================================
-- 表: sbti_results (SBTI结果表)
-- ============================================
DROP TABLE IF EXISTS `sbti_results`;
CREATE TABLE `sbti_results` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '结果ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `all_themes_scores` JSON NOT NULL COMMENT '所有主题得分',
  `top_theme_1` VARCHAR(50) NOT NULL COMMENT '第一主导主题',
  `top_theme_2` VARCHAR(50) NOT NULL COMMENT '第二主导主题',
  `top_theme_3` VARCHAR(50) NOT NULL COMMENT '第三主导主题',
  `top_theme_4` VARCHAR(50) NOT NULL COMMENT '第四主导主题',
  `top_theme_5` VARCHAR(50) NOT NULL COMMENT '第五主导主题',
  `executing_score` FLOAT NOT NULL COMMENT '执行力得分',
  `influencing_score` FLOAT NOT NULL COMMENT '影响力得分',
  `relationship_score` FLOAT NOT NULL COMMENT '关系力得分',
  `strategic_score` FLOAT NOT NULL COMMENT '战略力得分',
  `dominant_domain` VARCHAR(50) NOT NULL COMMENT '主导领域',
  `report_json` TEXT DEFAULT NULL COMMENT '完整报告JSON',
  `version` INT DEFAULT 1 COMMENT '报告版本',
  `is_latest` TINYINT(1) DEFAULT TRUE COMMENT '是否为最新结果',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `ix_sbti_results_user_id` (`user_id`),
  INDEX `ix_sbti_results_is_latest` (`is_latest`),
  CONSTRAINT `fk_sbti_results_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SBTI结果表';

-- ============================================
-- 表: attachment_questions (依恋风格题目表)
-- ============================================
DROP TABLE IF EXISTS `attachment_questions`;
CREATE TABLE `attachment_questions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '题目ID',
  `question_no` INT NOT NULL COMMENT '题目序号',
  `question_text` TEXT NOT NULL COMMENT '题目内容',
  `anxiety_weight` FLOAT DEFAULT 0 COMMENT '焦虑权重',
  `avoidance_weight` FLOAT DEFAULT 0 COMMENT '回避权重',
  `scale_min` INT DEFAULT 1 COMMENT '量表最小值',
  `scale_max` INT DEFAULT 7 COMMENT '量表最大值',
  `scale_min_label` VARCHAR(50) DEFAULT '完全不符合' COMMENT '最小值标签',
  `scale_max_label` VARCHAR(50) DEFAULT '完全符合' COMMENT '最大值标签',
  `is_active` TINYINT(1) DEFAULT TRUE COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_attachment_questions_question_no` (`question_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='依恋风格题目表';

-- ============================================
-- 表: attachment_answers (依恋风格答题记录表)
-- ============================================
DROP TABLE IF EXISTS `attachment_answers`;
CREATE TABLE `attachment_answers` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '答题记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `question_id` INT NOT NULL COMMENT '题目ID',
  `score` INT NOT NULL COMMENT '得分',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`),
  INDEX `ix_attachment_answers_user_id` (`user_id`),
  INDEX `ix_attachment_answers_question_id` (`question_id`),
  CONSTRAINT `fk_attachment_answers_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_attachment_answers_question` FOREIGN KEY (`question_id`) REFERENCES `attachment_questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='依恋风格答题记录表';

-- ============================================
-- 表: attachment_results (依恋风格结果表)
-- ============================================
DROP TABLE IF EXISTS `attachment_results`;
CREATE TABLE `attachment_results` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '结果ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `anxiety_score` FLOAT NOT NULL COMMENT '焦虑得分',
  `avoidance_score` FLOAT NOT NULL COMMENT '回避得分',
  `attachment_style` VARCHAR(20) NOT NULL COMMENT '依恋风格',
  `sub_type` VARCHAR(50) DEFAULT NULL COMMENT '子类型',
  `characteristics` JSON DEFAULT NULL COMMENT '特征描述',
  `relationship_tips` TEXT DEFAULT NULL COMMENT '关系建议',
  `self_growth_tips` TEXT DEFAULT NULL COMMENT '自我成长建议',
  `report_json` TEXT DEFAULT NULL COMMENT '完整报告JSON',
  `version` INT DEFAULT 1 COMMENT '报告版本',
  `is_latest` TINYINT(1) DEFAULT TRUE COMMENT '是否为最新结果',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `ix_attachment_results_user_id` (`user_id`),
  INDEX `ix_attachment_results_is_latest` (`is_latest`),
  CONSTRAINT `fk_attachment_results_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='依恋风格结果表';

-- ============================================
-- 表: deep_persona_profiles (深度画像表)
-- ============================================
DROP TABLE IF EXISTS `deep_persona_profiles`;
CREATE TABLE `deep_persona_profiles` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '画像ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `mbti_result_id` INT DEFAULT NULL COMMENT 'MBTI结果ID',
  `sbti_result_id` INT DEFAULT NULL COMMENT 'SBTI结果ID',
  `attachment_result_id` INT DEFAULT NULL COMMENT '依恋风格结果ID',
  `core_tags` JSON DEFAULT NULL COMMENT '核心标签',
  `emotion_pattern` TEXT DEFAULT NULL COMMENT '情绪模式',
  `communication_style` TEXT DEFAULT NULL COMMENT '沟通风格',
  `relationship_needs` JSON DEFAULT NULL COMMENT '关系需求',
  `growth_suggestions` JSON DEFAULT NULL COMMENT '成长建议',
  `ai_compatibility` JSON DEFAULT NULL COMMENT 'AI相性',
  `completeness` INT DEFAULT 0 COMMENT '完整度',
  `has_deep_report` TINYINT(1) DEFAULT FALSE COMMENT '是否有深度报告',
  `deep_report_content` TEXT DEFAULT NULL COMMENT '深度报告内容',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_deep_persona_profiles_user_id` (`user_id`),
  INDEX `ix_deep_persona_profiles_completeness` (`completeness`),
  CONSTRAINT `fk_deep_persona_profiles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_deep_persona_profiles_mbti` FOREIGN KEY (`mbti_result_id`) REFERENCES `mbti_results` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_deep_persona_profiles_sbti` FOREIGN KEY (`sbti_result_id`) REFERENCES `sbti_results` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_deep_persona_profiles_attachment` FOREIGN KEY (`attachment_result_id`) REFERENCES `attachment_results` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='深度画像表';

-- ============================================
-- 表: persona_insights (人格洞察表)
-- ============================================
DROP TABLE IF EXISTS `persona_insights`;
CREATE TABLE `persona_insights` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '洞察ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `insight_type` VARCHAR(50) NOT NULL COMMENT '洞察类型',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `content` TEXT NOT NULL COMMENT '内容',
  `tags` JSON DEFAULT NULL COMMENT '标签',
  `is_helpful` TINYINT(1) DEFAULT NULL COMMENT '是否有帮助',
  `user_feedback` TEXT DEFAULT NULL COMMENT '用户反馈',
  `generated_by` VARCHAR(50) DEFAULT 'ai' COMMENT '生成方式',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_persona_insights_user_id` (`user_id`),
  INDEX `ix_persona_insights_insight_type` (`insight_type`),
  INDEX `ix_persona_insights_created_at` (`created_at`),
  CONSTRAINT `fk_persona_insights_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人格洞察表';

-- ============================================
-- 表: knowledge_articles (知识文章表)
-- ============================================
DROP TABLE IF EXISTS `knowledge_articles`;
CREATE TABLE `knowledge_articles` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '文章ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `summary` VARCHAR(500) DEFAULT NULL COMMENT '摘要',
  `content` TEXT NOT NULL COMMENT '文章内容(Markdown)',
  `content_html` TEXT DEFAULT NULL COMMENT 'HTML内容',
  `category` ENUM('EMOTION', 'RELATIONSHIP', 'SELF_GROWTH', 'PSYCHOLOGY', 'LOVE', 'FAMILY', 'CAREER') NOT NULL COMMENT '分类',
  `tags` VARCHAR(500) DEFAULT NULL COMMENT '标签,逗号分隔',
  `mbti_types` VARCHAR(100) DEFAULT NULL COMMENT '相关MBTI类型,逗号分隔',
  `vector_id` VARCHAR(100) DEFAULT NULL COMMENT '向量ID',
  `status` ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED') DEFAULT NULL COMMENT '状态',
  `view_count` INT DEFAULT NULL COMMENT '阅读数',
  `like_count` INT DEFAULT NULL COMMENT '点赞数',
  `cover_image` VARCHAR(500) DEFAULT NULL COMMENT '封面图',
  `author` VARCHAR(100) DEFAULT NULL COMMENT '作者',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `published_at` DATETIME DEFAULT NULL COMMENT '发布时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识文章表';

-- ============================================
-- 表: knowledge_collections (知识收藏表)
-- ============================================
DROP TABLE IF EXISTS `knowledge_collections`;
CREATE TABLE `knowledge_collections` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `article_id` INT NOT NULL COMMENT '文章ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  INDEX `ix_knowledge_collections_user_id` (`user_id`),
  INDEX `ix_knowledge_collections_article_id` (`article_id`),
  UNIQUE INDEX `ix_knowledge_collections_unique` (`user_id`, `article_id`),
  CONSTRAINT `fk_knowledge_collections_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_knowledge_collections_article` FOREIGN KEY (`article_id`) REFERENCES `knowledge_articles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识收藏表';

-- ============================================
-- 表: banners (横幅表)
-- ============================================
DROP TABLE IF EXISTS `banners`;
CREATE TABLE `banners` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '横幅ID',
  `title` VARCHAR(100) NOT NULL COMMENT '标题',
  `image_url` VARCHAR(500) NOT NULL COMMENT '图片URL',
  `link_url` VARCHAR(500) DEFAULT NULL COMMENT '跳转链接',
  `link_type` VARCHAR(20) DEFAULT NULL COMMENT '跳转类型(internal/external)',
  `position` VARCHAR(20) DEFAULT NULL COMMENT '位置(home/mbti/chat)',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否启用',
  `sort_order` INT DEFAULT NULL COMMENT '排序',
  `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
  `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='横幅表';

-- ============================================
-- 表: announcements (公告表)
-- ============================================
DROP TABLE IF EXISTS `announcements`;
CREATE TABLE `announcements` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '公告ID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `content` TEXT NOT NULL COMMENT '内容',
  `content_type` VARCHAR(20) DEFAULT NULL COMMENT '内容类型(text/markdown)',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否启用',
  `is_top` TINYINT(1) DEFAULT NULL COMMENT '是否置顶',
  `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
  `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公告表';

-- ============================================
-- 表: badges (徽章表)
-- ============================================
DROP TABLE IF EXISTS `badges`;
CREATE TABLE `badges` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '徽章ID',
  `badge_code` VARCHAR(50) NOT NULL COMMENT '徽章编码',
  `name` VARCHAR(100) NOT NULL COMMENT '徽章名称',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '徽章描述',
  `icon` VARCHAR(500) DEFAULT NULL COMMENT '图标URL',
  `rarity` VARCHAR(20) NOT NULL COMMENT '稀有度',
  `category` VARCHAR(50) DEFAULT NULL COMMENT '分类: 入门/活跃/成就/隐藏',
  `condition_type` VARCHAR(50) DEFAULT NULL COMMENT '解锁条件类型: login_days/conversation_count/diary_count',
  `condition_value` INT DEFAULT NULL COMMENT '条件值',
  `hint` VARCHAR(200) DEFAULT NULL COMMENT '获取提示（对未解锁用户显示）',
  `is_hidden` TINYINT(1) DEFAULT NULL COMMENT '是否隐藏',
  `is_active` TINYINT(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_badges_badge_code` (`badge_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='徽章表';

-- ============================================
-- 表: user_badges (用户徽章表)
-- ============================================
DROP TABLE IF EXISTS `user_badges`;
CREATE TABLE `user_badges` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `badge_id` INT NOT NULL COMMENT '徽章ID',
  `earned_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '获得时间',
  PRIMARY KEY (`id`),
  INDEX `ix_user_badges_user_id` (`user_id`),
  INDEX `ix_user_badges_badge_id` (`badge_id`),
  UNIQUE INDEX `ix_user_badges_unique` (`user_id`, `badge_id`),
  CONSTRAINT `fk_user_badges_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_badges_badge` FOREIGN KEY (`badge_id`) REFERENCES `badges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户徽章表';

-- ============================================
-- 表: system_configs (系统配置表)
-- ============================================
DROP TABLE IF EXISTS `system_configs`;
CREATE TABLE `system_configs` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键名',
  `config_value` TEXT DEFAULT NULL COMMENT '配置值',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '配置描述',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_system_configs_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ============================================
-- 表: chat_sessions (聊天会话表)
-- ============================================
DROP TABLE IF EXISTS `chat_sessions`;
CREATE TABLE `chat_sessions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '会话ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `assistant_id` INT NOT NULL COMMENT '助手ID',
  `session_id` VARCHAR(100) NOT NULL COMMENT '会话唯一标识',
  `title` VARCHAR(200) DEFAULT NULL COMMENT '会话标题',
  `message_count` INT DEFAULT 0 COMMENT '消息数量',
  `is_closed` TINYINT(1) DEFAULT FALSE COMMENT '是否已关闭',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `closed_at` DATETIME DEFAULT NULL COMMENT '关闭时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_chat_sessions_session_id` (`session_id`),
  INDEX `ix_chat_sessions_user_id` (`user_id`),
  INDEX `ix_chat_sessions_assistant_id` (`assistant_id`),
  CONSTRAINT `fk_chat_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_chat_sessions_assistant` FOREIGN KEY (`assistant_id`) REFERENCES `ai_assistants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天会话表';

-- ============================================
-- 表: chat_messages (聊天消息表)
-- ============================================
DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `session_id` VARCHAR(100) NOT NULL COMMENT '会话ID',
  `user_id` INT DEFAULT NULL COMMENT '用户ID(可为空用于系统消息)',
  `role` VARCHAR(20) NOT NULL COMMENT '角色(user/assistant/system)',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `model` VARCHAR(50) DEFAULT NULL COMMENT '使用的模型',
  `tokens` INT DEFAULT NULL COMMENT '消耗的token数',
  `is_collected` TINYINT(1) DEFAULT FALSE COMMENT '是否收藏',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_chat_messages_session_id` (`session_id`),
  INDEX `ix_chat_messages_user_id` (`user_id`),
  INDEX `ix_chat_messages_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天消息表';

-- ============================================
-- 表: diary_entries (日记表)
-- ============================================
DROP TABLE IF EXISTS `diary_entries`;
CREATE TABLE `diary_entries` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '日记ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) DEFAULT NULL COMMENT '日记标题',
  `content` TEXT NOT NULL COMMENT '日记内容',
  `mood_level` INT DEFAULT NULL COMMENT '心情等级(1-5)',
  `emotion_tags` VARCHAR(500) DEFAULT NULL COMMENT '情绪标签,逗号分隔',
  `weather` VARCHAR(50) DEFAULT NULL COMMENT '天气',
  `sleep_quality` INT DEFAULT NULL COMMENT '睡眠质量(1-5)',
  `exercise_minutes` INT DEFAULT NULL COMMENT '运动时长(分钟)',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `analyzed_at` DATETIME DEFAULT NULL COMMENT '分析时间',
  PRIMARY KEY (`id`),
  INDEX `ix_diary_entries_user_id` (`user_id`),
  INDEX `ix_diary_entries_created_at` (`created_at`),
  CONSTRAINT `fk_diary_entries_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日记表';

-- ============================================
-- 表: diary_moods (心情记录表)
-- ============================================
DROP TABLE IF EXISTS `diary_moods`;
CREATE TABLE `diary_moods` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '心情记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `mood_date` DATE NOT NULL COMMENT '心情日期',
  `mood_score` INT NOT NULL COMMENT '心情得分(1-10)',
  `emotion_type` VARCHAR(50) DEFAULT NULL COMMENT '主要情绪类型',
  `emotion_intensity` INT DEFAULT NULL COMMENT '情绪强度(1-5)',
  `trigger_factor` VARCHAR(200) DEFAULT NULL COMMENT '触发因素',
  `note` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_diary_moods_user_date` (`user_id`, `mood_date`),
  CONSTRAINT `fk_diary_moods_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心情记录表';

-- ============================================
-- 表: diary_tags (日记标签表)
-- ============================================
DROP TABLE IF EXISTS `diary_tags`;
CREATE TABLE `diary_tags` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '标签ID',
  `name` VARCHAR(50) NOT NULL COMMENT '标签名称',
  `color` VARCHAR(20) DEFAULT NULL COMMENT '标签颜色',
  `category` VARCHAR(50) DEFAULT NULL COMMENT '标签分类',
  `usage_count` INT DEFAULT 0 COMMENT '使用次数',
  `is_system` TINYINT(1) DEFAULT FALSE COMMENT '是否系统标签',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日记标签表';

-- ============================================
-- 表: diary_entry_tags (日记标签关联表)
-- ============================================
DROP TABLE IF EXISTS `diary_entry_tags`;
CREATE TABLE `diary_entry_tags` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '关联ID',
  `entry_id` INT NOT NULL COMMENT '日记ID',
  `tag_id` INT NOT NULL COMMENT '标签ID',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `ix_diary_entry_tags_unique` (`entry_id`, `tag_id`),
  CONSTRAINT `fk_diary_entry_tags_entry` FOREIGN KEY (`entry_id`) REFERENCES `diary_entries` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_diary_entry_tags_tag` FOREIGN KEY (`tag_id`) REFERENCES `diary_tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日记标签关联表';

-- ============================================
-- 表: checkin_records (打卡记录表)
-- ============================================
DROP TABLE IF EXISTS `checkin_records`;
CREATE TABLE `checkin_records` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '打卡记录ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `checkin_date` DATE NOT NULL COMMENT '打卡日期',
  `note` TEXT DEFAULT NULL COMMENT '打卡备注',
  `mood` VARCHAR(50) DEFAULT NULL COMMENT '当时心情',
  `streak_count` INT DEFAULT 0 COMMENT '连续打卡天数',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_checkin_records_user_date` (`user_id`, `checkin_date`),
  CONSTRAINT `fk_checkin_records_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';

-- ============================================
-- 表: user_memories (用户记忆表)
-- ============================================
DROP TABLE IF EXISTS `user_memories`;
CREATE TABLE `user_memories` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '记忆ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `memory_type` VARCHAR(50) NOT NULL COMMENT '记忆类型',
  `content` TEXT NOT NULL COMMENT '记忆内容',
  `importance` INT DEFAULT 5 COMMENT '重要性(1-10)',
  `last_accessed_at` DATETIME DEFAULT NULL COMMENT '最后访问时间',
  `access_count` INT DEFAULT 0 COMMENT '访问次数',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_user_memories_user_id` (`user_id`),
  INDEX `ix_user_memories_memory_type` (`memory_type`),
  CONSTRAINT `fk_user_memories_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户记忆表';

-- ============================================
-- 表: feedback (反馈表)
-- ============================================
DROP TABLE IF EXISTS `feedback`;
CREATE TABLE `feedback` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '反馈ID',
  `user_id` INT DEFAULT NULL COMMENT '用户ID',
  `type` VARCHAR(50) NOT NULL COMMENT '反馈类型',
  `content` TEXT NOT NULL COMMENT '反馈内容',
  `contact` VARCHAR(100) DEFAULT NULL COMMENT '联系方式',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT '处理状态',
  `admin_note` TEXT DEFAULT NULL COMMENT '管理员备注',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `ix_feedback_user_id` (`user_id`),
  INDEX `ix_feedback_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='反馈表';

-- ============================================
-- Alembic版本表
-- ============================================
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Alembic版本表';

-- 插入当前数据库版本
INSERT INTO `alembic_version` (`version_num`) VALUES ('2026_04_16_001');

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 初始化完成
-- ============================================
