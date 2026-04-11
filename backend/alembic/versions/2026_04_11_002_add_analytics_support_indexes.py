"""
添加数据分析和客服系统的索引
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_11_002_add_analytics_support_indexes'
down_revision = '2026_04_11_001_add_personality_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为 user_activities 表添加索引
    op.create_index('idx_user_activities_user_id', 'user_activities', ['user_id'])
    op.create_index('idx_user_activities_event_type', 'user_activities', ['event_type'])
    op.create_index('idx_user_activities_created_at', 'user_activities', ['created_at'])
    
    # 为 analytics_metrics 表添加索引
    op.create_index('idx_analytics_metrics_metric_name', 'analytics_metrics', ['metric_name'])
    op.create_index('idx_analytics_metrics_metric_date', 'analytics_metrics', ['metric_date'])
    op.create_index('idx_analytics_metrics_dimension', 'analytics_metrics', ['dimension'])
    
    # 为 user_behavior 表添加索引
    op.create_index('idx_user_behavior_user_id', 'user_behavior', ['user_id'])
    op.create_index('idx_user_behavior_behavior_type', 'user_behavior', ['behavior_type'])
    
    # 为 support_tickets 表添加索引
    op.create_index('idx_support_tickets_user_id', 'support_tickets', ['user_id'])
    op.create_index('idx_support_tickets_status', 'support_tickets', ['status'])
    op.create_index('idx_support_tickets_priority', 'support_tickets', ['priority'])
    op.create_index('idx_support_tickets_created_at', 'support_tickets', ['created_at'])
    
    # 为 ticket_messages 表添加索引
    op.create_index('idx_ticket_messages_ticket_id', 'ticket_messages', ['ticket_id'])
    op.create_index('idx_ticket_messages_created_at', 'ticket_messages', ['created_at'])
    
    # 为 chatbot_conversations 表添加索引
    op.create_index('idx_chatbot_conversations_user_id', 'chatbot_conversations', ['user_id'])
    op.create_index('idx_chatbot_conversations_session_id', 'chatbot_conversations', ['session_id'])
    
    # 为 chatbot_messages 表添加索引
    op.create_index('idx_chatbot_messages_conversation_id', 'chatbot_messages', ['conversation_id'])
    op.create_index('idx_chatbot_messages_created_at', 'chatbot_messages', ['created_at'])


def downgrade() -> None:
    # 删除 user_activities 表的索引
    op.drop_index('idx_user_activities_user_id', table_name='user_activities')
    op.drop_index('idx_user_activities_event_type', table_name='user_activities')
    op.drop_index('idx_user_activities_created_at', table_name='user_activities')
    
    # 删除 analytics_metrics 表的索引
    op.drop_index('idx_analytics_metrics_metric_name', table_name='analytics_metrics')
    op.drop_index('idx_analytics_metrics_metric_date', table_name='analytics_metrics')
    op.drop_index('idx_analytics_metrics_dimension', table_name='analytics_metrics')
    
    # 删除 user_behavior 表的索引
    op.drop_index('idx_user_behavior_user_id', table_name='user_behavior')
    op.drop_index('idx_user_behavior_behavior_type', table_name='user_behavior')
    
    # 删除 support_tickets 表的索引
    op.drop_index('idx_support_tickets_user_id', table_name='support_tickets')
    op.drop_index('idx_support_tickets_status', table_name='support_tickets')
    op.drop_index('idx_support_tickets_priority', table_name='support_tickets')
    op.drop_index('idx_support_tickets_created_at', table_name='support_tickets')
    
    # 删除 ticket_messages 表的索引
    op.drop_index('idx_ticket_messages_ticket_id', table_name='ticket_messages')
    op.drop_index('idx_ticket_messages_created_at', table_name='ticket_messages')
    
    # 删除 chatbot_conversations 表的索引
    op.drop_index('idx_chatbot_conversations_user_id', table_name='chatbot_conversations')
    op.drop_index('idx_chatbot_conversations_session_id', table_name='chatbot_conversations')
    
    # 删除 chatbot_messages 表的索引
    op.drop_index('idx_chatbot_messages_conversation_id', table_name='chatbot_messages')
    op.drop_index('idx_chatbot_messages_created_at', table_name='chatbot_messages')
