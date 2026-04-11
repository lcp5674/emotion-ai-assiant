#!/usr/bin/env python3
"""
定时任务执行脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.task_service import run_scheduled_tasks

if __name__ == "__main__":
    print("开始执行定时任务...")
    run_scheduled_tasks()
    print("定时任务执行完成")
