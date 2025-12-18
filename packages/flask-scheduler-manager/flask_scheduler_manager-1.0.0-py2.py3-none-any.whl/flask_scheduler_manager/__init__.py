# -*- coding: utf-8 -*-
"""
Flask Scheduler Manager - 动态定时任务管理系统
支持单体模式和分离部署模式（Web服务 + 调度器服务）
支持 Redis 单机模式和集群（Cluster）模式
"""
from flask_scheduler_manager.manager import (
    SchedulerManager,
    WebSchedulerManager,
    BaseSchedulerManager
)
from flask_scheduler_manager.models import init_models, get_scheduled_job_model
from flask_scheduler_manager.redis_stream import (
    JobEventProducer,
    JobEventConsumer,
    create_redis_client,
    RedisClientFactory
)

__version__ = "1.2.0"
__all__ = [
    'SchedulerManager',
    'WebSchedulerManager',
    'BaseSchedulerManager',
    'init_models',
    'get_scheduled_job_model',
    'JobEventProducer',
    'JobEventConsumer',
    'create_redis_client',
    'RedisClientFactory'
]
