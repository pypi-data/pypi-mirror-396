# -*- coding: utf-8 -*-
"""
定时任务管理器
支持单体模式和分离部署模式（Web服务 + 调度器服务）
"""
import importlib
import logging
import time
import traceback
import uuid
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, List, Any, Callable
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError

from flask_scheduler_manager.models import init_models, get_scheduled_job_model

logger = logging.getLogger(__name__)


def transform_cron_value(value: str):
    if value == "*":
        return None
    return value


class BaseSchedulerManager:
    """
    调度器管理器基类
    提供数据库操作的公共方法
    """

    def __init__(self, app: Flask = None, db: SQLAlchemy = None):
        """
        初始化管理器

        Args:
            app: Flask应用实例
            db: SQLAlchemy数据库实例
        """
        self.app = app
        self.db = db
        self.ScheduledJob = None

        if app is not None:
            self._init_models(app, db)

    def with_app_context(self, func):
        """装饰器：确保函数在应用上下文中执行"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.app.app_context():
                return func(*args, **kwargs)

        return wrapper

    def _init_models(self, app: Flask, db: SQLAlchemy):
        """初始化模型"""
        self.app = app
        self.db = db
        init_models(db)
        self.ScheduledJob = get_scheduled_job_model()

    def init_db(self):
        """初始化数据库表"""
        with self.app.app_context():
            self.db.create_all()
            logger.info("数据库表初始化完成")

    def get_job(self, job_id: str):
        """获取任务"""
        return self.ScheduledJob.query.filter_by(job_id=job_id).first()

    def get_all_jobs(self, enabled_only: bool = False):
        """获取所有任务"""
        query = self.ScheduledJob.query
        if enabled_only:
            query = query.filter_by(enabled=True)
        return query.order_by(self.ScheduledJob.created_at.desc()).all()

    def _create_job_model(self, func: str, trigger: str,
                          enabled: bool, name: str, description: str,
                          **kwargs) -> "ScheduledJob":
        """
        创建任务模型（仅数据库操作）

        Returns:
            创建的任务模型
        """
        # # 检查任务是否已存在
        # existing_job = self.ScheduledJob.query.filter_by(job_id=job_id).first()
        # if existing_job:
        #     raise ValueError(f"任务 {job_id} 已存在")

        # 创建任务模型
        job_model = self.ScheduledJob(
            job_id=str(uuid.uuid4()),
            func=func,
            trigger=trigger,
            enabled=enabled,
            name=name,
            description=description,
        )

        # 设置触发器参数
        if trigger == 'cron':
            job_model.year = transform_cron_value(kwargs.get('year'))
            job_model.month = transform_cron_value(kwargs.get('month'))
            job_model.day = transform_cron_value(kwargs.get('day'))
            job_model.week = transform_cron_value(kwargs.get('week'))
            job_model.day_of_week = transform_cron_value(kwargs.get('day_of_week'))
            job_model.hour = transform_cron_value(kwargs.get('hour'))
            job_model.minute = transform_cron_value(kwargs.get('minute'))
            job_model.second = kwargs.get('second', '0')
            job_model.start_date = kwargs.get('start_date')
            job_model.end_date = kwargs.get('end_date')
        elif trigger == 'interval':
            job_model.weeks = kwargs.get('weeks')
            job_model.days = kwargs.get('days')
            job_model.hours = kwargs.get('hours')
            job_model.minutes = kwargs.get('minutes')
            job_model.seconds = kwargs.get('seconds')
            job_model.start_date = kwargs.get('start_date')
            job_model.end_date = kwargs.get('end_date')
        elif trigger == 'date':
            job_model.start_date = kwargs.get('start_date') or kwargs.get('run_date')
            if not job_model.start_date:
                raise ValueError("date触发器必须指定start_date或run_date")

        # 设置任务参数
        job_model.args = kwargs.get('args')
        job_model.kwargs = kwargs.get('kwargs')
        job_model.max_instances = kwargs.get('max_instances', 1)
        job_model.misfire_grace_time = kwargs.get('misfire_grace_time')

        # 保存到数据库
        self.db.session.add(job_model)
        self.db.session.commit()

        return job_model

    def _update_job_model(self, job_id: str, **kwargs):
        """
        更新任务模型（仅数据库操作）

        Returns:
            更新后的任务模型
        """
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(job_model, key):
                setattr(job_model, key, value)

        job_model.updated_at = datetime.utcnow()
        self.db.session.commit()

        return job_model

    def _delete_job_model(self, job_id: str):
        """
        删除任务模型（仅数据库操作）
        """
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        self.db.session.delete(job_model)
        self.db.session.commit()


class WebSchedulerManager(BaseSchedulerManager):
    """
    Web服务调度器管理器
    仅负责数据库操作和发布事件到Redis Stream
    不启动APScheduler，适用于分离部署的Web服务端
    """

    def __init__(self, app: Flask = None, db: SQLAlchemy = None,
                 redis_client=None):
        """
        初始化Web调度器管理器

        Args:
            app: Flask应用实例
            db: SQLAlchemy数据库实例
            redis_client: 可选，外部传入的Redis客户端实例
        """
        super().__init__(app, db)
        self._producer = None
        self._redis_client = redis_client

        if app is not None:
            self.init_app(app, db, redis_client)

    def init_app(self, app: Flask, db: SQLAlchemy, redis_client=None):
        """
        初始化应用

        Args:
            app: Flask应用实例
            db: SQLAlchemy数据库实例
            redis_client: 可选，外部传入的Redis客户端实例
        """
        self._init_models(app, db)

        # 优先使用外部传入的客户端
        if redis_client is not None:
            self._redis_client = redis_client
            self._init_redis_producer_with_client(app)
        elif self._redis_client is not None:
            # 使用构造函数传入的客户端
            self._init_redis_producer_with_client(app)
        else:
            # 根据配置自动创建客户端
            redis_url = app.config.get('SCHEDULER_REDIS_URL')
            cluster_nodes = app.config.get('SCHEDULER_REDIS_CLUSTER_NODES')

            if redis_url or cluster_nodes:
                self._init_redis_producer(app)
            else:
                logger.warning("未配置 Redis，事件发布功能已禁用")

    def _init_redis_producer_with_client(self, app: Flask):
        """使用已有的Redis客户端初始化生产者"""
        try:
            from flask_scheduler_manager.redis_stream import JobEventProducer

            stream_key = app.config.get('SCHEDULER_STREAM_KEY', 'scheduler:job_events')
            maxlen = app.config.get('SCHEDULER_STREAM_MAXLEN', 10000)

            self._producer = JobEventProducer(
                self._redis_client,
                stream_key=stream_key,
                maxlen=maxlen
            )
            logger.info(f"Redis Stream生产者已初始化(外部客户端): stream_key={stream_key}")

        except Exception as e:
            logger.error(f"初始化Redis生产者失败: {str(e)}")

    def _init_redis_producer(self, app: Flask):
        """初始化Redis Stream生产者（支持单机和集群模式）"""
        try:
            from flask_scheduler_manager.redis_stream import (
                JobEventProducer, RedisClientFactory
            )

            stream_key = app.config.get('SCHEDULER_STREAM_KEY', 'scheduler:job_events')
            maxlen = app.config.get('SCHEDULER_STREAM_MAXLEN', 10000)

            # 使用工厂方法创建客户端（自动支持单机/集群模式）
            self._redis_client = RedisClientFactory.create_from_app_config(app.config)
            self._producer = JobEventProducer(
                self._redis_client,
                stream_key=stream_key,
                maxlen=maxlen
            )

            cluster_mode = app.config.get('SCHEDULER_REDIS_CLUSTER', False)
            mode_str = "集群模式" if cluster_mode else "单机模式"
            logger.info(f"Redis Stream生产者已初始化: stream_key={stream_key}, mode={mode_str}")

        except ImportError:
            logger.error("导入redis_stream模块失败，请确保已安装redis包")
        except Exception as e:
            logger.error(f"初始化Redis生产者失败: {str(e)}")

    def set_redis_client(self, redis_client):
        """
        设置Redis客户端（运行时动态设置）

        Args:
            redis_client: Redis客户端实例
        """
        self._redis_client = redis_client
        if self.app:
            self._init_redis_producer_with_client(self.app)

    def _publish_event(self, action: str, job_id: str = None):
        """发布事件到Redis Stream"""
        if self._producer:
            self._producer.publish(action, job_id)

    def add_job(self, func: str, trigger: str = 'cron',
                enabled: bool = True, name: str = None, description: str = None,
                **kwargs):
        """
        添加定时任务

        Args:
            func: 任务函数路径，格式：module:function
            trigger: 触发器类型（cron/interval/date）
            enabled: 是否启用
            name: 任务名称
            description: 任务描述
            **kwargs: 触发器参数和其他任务参数

        Returns:
            创建的任务模型
        """
        job_model = self._create_job_model(
            func, trigger, enabled, name, description, **kwargs
        )

        # 发布添加事件
        if enabled:
            self._publish_event('add', job_model.job_id)

        logger.info(f"任务已添加: {job_model.job_id}")
        return job_model

    def update_job(self, job_id: str, **kwargs):
        """
        更新任务

        Args:
            job_id: 任务ID
            **kwargs: 要更新的字段

        Returns:
            更新后的任务模型
        """
        job_model = self._update_job_model(job_id, **kwargs)

        # 发布更新事件
        self._publish_event('update', job_id)

        logger.info(f"任务已更新: {job_id}")
        return job_model

    def enable_job(self, job_id: str) -> bool:
        """启用任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        if job_model.enabled:
            return True

        job_model.enabled = True
        self.db.session.commit()

        # 发布启用事件
        self._publish_event('enable', job_id)

        logger.info(f"任务已启用: {job_id}")
        return True

    def disable_job(self, job_id: str) -> bool:
        """禁用任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        if not job_model.enabled:
            return True

        job_model.enabled = False
        self.db.session.commit()

        # 发布禁用事件
        self._publish_event('disable', job_id)

        logger.info(f"任务已禁用: {job_id}")
        return True

    def remove_job(self, job_id: str) -> bool:
        """删除任务"""
        # 先发布删除事件（需要在删除前发布）
        self._publish_event('delete', job_id)

        self._delete_job_model(job_id)

        logger.info(f"任务已删除: {job_id}")
        return True

    def reload_all_jobs(self):
        """
        通知调度器重新加载所有任务
        """
        self._publish_event('reload_all')
        logger.info("已发送重载所有任务事件")

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态（仅数据库状态）"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        return {
            'job_id': job_id,
            'enabled': job_model.enabled,
            'next_run_time': job_model.next_run_time.isoformat() if job_model.next_run_time else None,
            'last_run_time': job_model.last_run_time.isoformat() if job_model.last_run_time else None,
        }


class SchedulerManager(BaseSchedulerManager):
    """
    定时任务管理器
    负责管理基于SQLAlchemy持久化的定时任务
    支持单体模式和分离部署模式（作为调度器服务）
    """

    def __init__(self, app: Flask = None, db: SQLAlchemy = None,
                 redis_client=None):
        """
        初始化调度器管理器

        Args:
            app: Flask应用实例
            db: SQLAlchemy数据库实例
            redis_client: 可选，外部传入的Redis客户端实例
        """
        super().__init__(app, db)
        self.scheduler = None
        self._consumer = None
        self._redis_client = redis_client

        if app is not None:
            self.init_app(app, db, redis_client)

    def init_app(self, app: Flask, db: SQLAlchemy, redis_client=None):
        """
        初始化应用

        Args:
            app: Flask应用实例
            db: SQLAlchemy数据库实例
            redis_client: 可选，外部传入的Redis客户端实例
        """
        self._init_models(app, db)

        # 配置APScheduler
        app.config.setdefault('SCHEDULER_API_ENABLED', True)
        app.config.setdefault('SCHEDULER_JOBSTORES', {
            'default': {
                'type': 'sqlalchemy',
                'url': app.config.get('SQLALCHEMY_DATABASE_URI')
            }
        })

        # 初始化APScheduler
        self.scheduler = APScheduler()
        self.scheduler.init_app(app)
        self.scheduler.start()

        # 从数据库加载任务
        self._load_jobs_from_db()

        # 初始化Redis消费者
        if redis_client is not None:
            self._redis_client = redis_client
            self._init_redis_consumer_with_client(app)
        elif self._redis_client is not None:
            self._init_redis_consumer_with_client(app)
        else:
            redis_url = app.config.get('SCHEDULER_REDIS_URL')
            cluster_nodes = app.config.get('SCHEDULER_REDIS_CLUSTER_NODES')

            if redis_url or cluster_nodes:
                self._init_redis_consumer(app)

    def _init_redis_consumer_with_client(self, app: Flask):
        """使用已有的Redis客户端初始化消费者"""
        try:
            from flask_scheduler_manager.redis_stream import JobEventConsumer

            stream_key = app.config.get('SCHEDULER_STREAM_KEY', 'scheduler:job_events')
            group_name = app.config.get('SCHEDULER_CONSUMER_GROUP', 'scheduler_workers')
            consumer_name = app.config.get('SCHEDULER_CONSUMER_NAME', 'worker_1')

            self._consumer = JobEventConsumer(
                self._redis_client,
                stream_key=stream_key,
                group_name=group_name,
                consumer_name=consumer_name
            )
            logger.info(f"Redis Stream消费者已初始化(外部客户端): group={group_name}, consumer={consumer_name}")

        except Exception as e:
            logger.error(f"初始化Redis消费者失败: {str(e)}")

    def _init_redis_consumer(self, app: Flask):
        """初始化Redis Stream消费者（支持单机和集群模式）"""
        try:
            from flask_scheduler_manager.redis_stream import (
                JobEventConsumer, RedisClientFactory
            )

            stream_key = app.config.get('SCHEDULER_STREAM_KEY', 'scheduler:job_events')
            group_name = app.config.get('SCHEDULER_CONSUMER_GROUP', 'scheduler_workers')
            consumer_name = app.config.get('SCHEDULER_CONSUMER_NAME', 'worker_1')

            # 使用工厂方法创建客户端（自动支持单机/集群模式）
            self._redis_client = RedisClientFactory.create_from_app_config(app.config)
            self._consumer = JobEventConsumer(
                self._redis_client,
                stream_key=stream_key,
                group_name=group_name,
                consumer_name=consumer_name
            )

            cluster_mode = app.config.get('SCHEDULER_REDIS_CLUSTER', False)
            mode_str = "集群模式" if cluster_mode else "单机模式"
            logger.info(f"Redis Stream消费者已初始化: group={group_name}, consumer={consumer_name}, mode={mode_str}")

        except ImportError:
            logger.error("导入redis_stream模块失败，请确保已安装redis包")
        except Exception as e:
            logger.error(f"初始化Redis消费者失败: {str(e)}")

    def set_redis_client(self, redis_client):
        """
        设置Redis客户端（运行时动态设置）

        Args:
            redis_client: Redis客户端实例
        """
        self._redis_client = redis_client
        if self.app:
            self._init_redis_consumer_with_client(self.app)

    def start_event_listener(self):
        """
        启动事件监听器
        开始消费Redis Stream中的任务变更事件
        """
        if not self._consumer:
            logger.warning("Redis消费者未初始化，无法启动事件监听")
            return

        self._consumer.start(self._handle_event)
        logger.info("事件监听器已启动")

    def forever(self):
        """
        运行调度器，并保持运行
        """
        self.start_event_listener()
        try:
            while True:
                if not self._consumer.is_running:
                    logger.error("Scheduler stopped unexpectedly!")
                    self.start_event_listener()
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Scheduler mule process stopped by user")
            self.stop_event_listener()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            logger.error(traceback.format_exc())

    def stop_event_listener(self):
        """停止事件监听器"""
        if self._consumer:
            self._consumer.stop()
            logger.info("事件监听器已停止")

    def _handle_event(self, action: str, job_id: Optional[str]):
        """
        处理任务变更事件

        Args:
            action: 事件动作
            job_id: 任务ID
        """
        logger.info(f"收到事件: action={action}, job_id={job_id}")

        try:
            with self.app.app_context():
                if action == 'add':
                    self._handle_add_event(job_id)
                elif action == 'update':
                    self._handle_update_event(job_id)
                elif action == 'delete':
                    self._handle_delete_event(job_id)
                elif action == 'enable':
                    self._handle_enable_event(job_id)
                elif action == 'disable':
                    self._handle_disable_event(job_id)
                elif action == 'reload_all':
                    self._handle_reload_all_event()
                else:
                    logger.warning(f"未知的事件类型: {action}")
        except Exception as e:
            logger.error(f"处理事件失败: action={action}, job_id={job_id}, error={str(e)}")

    def _handle_add_event(self, job_id: str):
        """处理添加任务事件"""
        job_model = self.get_job(job_id)
        if job_model and job_model.enabled:
            self._add_job_to_scheduler(job_model)
            logger.info(f"事件处理完成: 任务已添加到调度器 {job_id}")

    def _handle_update_event(self, job_id: str):
        """处理更新任务事件"""
        job_model = self.get_job(job_id)
        if not job_model:
            return

        # 先移除旧任务
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass

        # 如果启用则重新添加
        if job_model.enabled:
            self._add_job_to_scheduler(job_model)

        logger.info(f"事件处理完成: 任务已更新 {job_id}")

    def _handle_delete_event(self, job_id: str):
        """处理删除任务事件"""
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass
        logger.info(f"事件处理完成: 任务已从调度器移除 {job_id}")

    def _handle_enable_event(self, job_id: str):
        """处理启用任务事件"""
        job_model = self.get_job(job_id)
        if job_model:
            self._add_job_to_scheduler(job_model)
            logger.info(f"事件处理完成: 任务已启用 {job_id}")

    def _handle_disable_event(self, job_id: str):
        """处理禁用任务事件"""
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass
        logger.info(f"事件处理完成: 任务已禁用 {job_id}")

    def _handle_reload_all_event(self):
        """处理重载所有任务事件"""
        # 获取当前调度器中的所有任务ID
        current_jobs = self.scheduler.get_jobs()
        for job in current_jobs:
            try:
                self.scheduler.remove_job(job.id)
            except JobLookupError:
                pass

        # 重新加载所有启用的任务
        self._load_jobs_from_db()
        logger.info("事件处理完成: 所有任务已重载")

    def _load_jobs_from_db(self):
        """从数据库加载所有启用的任务到调度器"""
        try:
            with self.app.app_context():
                jobs = self.ScheduledJob.query.filter_by(enabled=True).all()
                for job_model in jobs:
                    try:
                        self._add_job_to_scheduler(job_model)
                        logger.info(f"已加载任务: {job_model.job_id}")
                    except Exception as e:
                        logger.error(f"加载任务失败 {job_model.job_id}: {str(e)}")
        except Exception as e:
            logger.error(f"从数据库加载任务失败: {str(e)}")

    def _get_function(self, func_path: str) -> Callable:
        """根据函数路径获取函数对象"""
        try:
            module_path, func_name = func_path.rsplit(':', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            return func
        except (ValueError, ImportError, AttributeError) as e:
            raise ValueError(f"无法导入函数 {func_path}: {str(e)}")

    def _create_trigger(self, job_model):
        """根据任务模型创建触发器"""
        if job_model.trigger == 'cron':
            trigger_kwargs = {}
            if job_model.year:
                trigger_kwargs['year'] = job_model.year
            if job_model.month:
                trigger_kwargs['month'] = job_model.month
            if job_model.day:
                trigger_kwargs['day'] = job_model.day
            if job_model.week:
                trigger_kwargs['week'] = job_model.week
            if job_model.day_of_week:
                trigger_kwargs['day_of_week'] = job_model.day_of_week
            if job_model.hour:
                trigger_kwargs['hour'] = job_model.hour
            if job_model.minute:
                trigger_kwargs['minute'] = job_model.minute
            if job_model.second:
                trigger_kwargs['second'] = job_model.second
            if job_model.start_date:
                trigger_kwargs['start_date'] = job_model.start_date
            if job_model.end_date:
                trigger_kwargs['end_date'] = job_model.end_date
            return CronTrigger(**trigger_kwargs)

        elif job_model.trigger == 'interval':
            trigger_kwargs = {}
            if job_model.weeks:
                trigger_kwargs['weeks'] = job_model.weeks
            if job_model.days:
                trigger_kwargs['days'] = job_model.days
            if job_model.hours:
                trigger_kwargs['hours'] = job_model.hours
            if job_model.minutes:
                trigger_kwargs['minutes'] = job_model.minutes
            if job_model.seconds:
                trigger_kwargs['seconds'] = job_model.seconds
            if job_model.start_date:
                trigger_kwargs['start_date'] = job_model.start_date
            if job_model.end_date:
                trigger_kwargs['end_date'] = job_model.end_date
            return IntervalTrigger(**trigger_kwargs)

        elif job_model.trigger == 'date':
            if not job_model.start_date:
                raise ValueError("date触发器必须指定start_date")
            return DateTrigger(run_date=job_model.start_date)

        else:
            raise ValueError(f"不支持的触发器类型: {job_model.trigger}")

    def _add_job_to_scheduler(self, job_model):
        """将任务添加到调度器"""
        func = self._get_function(job_model.func)
        trigger = self._create_trigger(job_model)

        job_kwargs = {
            'id': job_model.job_id,
            'func': func,
            'trigger': trigger,
            'replace_existing': True,
        }

        if job_model.args:
            job_kwargs['args'] = job_model.args
        if job_model.kwargs:
            job_kwargs['kwargs'] = job_model.kwargs
        if job_model.max_instances:
            job_kwargs['max_instances'] = job_model.max_instances
        if job_model.misfire_grace_time:
            job_kwargs['misfire_grace_time'] = job_model.misfire_grace_time

        self.scheduler.add_job(**job_kwargs)

        # 更新下次执行时间
        try:
            scheduler_job = self.scheduler.get_job(job_model.job_id)
            if scheduler_job and scheduler_job.next_run_time:
                job_model.next_run_time = scheduler_job.next_run_time
                self.db.session.commit()
        except Exception as e:
            logger.warning(f"更新任务下次执行时间失败 {job_model.job_id}: {str(e)}")

    def add_job(self, func: str, trigger: str = 'cron',
                enabled: bool = True, name: str = None, description: str = None,
                **kwargs):
        """
        添加定时任务（单体模式使用）

        Args:
            job_id: 任务唯一标识
            func: 任务函数路径，格式：module:function
            trigger: 触发器类型（cron/interval/date）
            enabled: 是否启用
            name: 任务名称
            description: 任务描述
            **kwargs: 触发器参数和其他任务参数

        Returns:
            创建的任务模型
        """
        job_model = self._create_job_model(
            func, trigger, enabled, name, description, **kwargs
        )

        # 如果启用，添加到调度器
        if enabled:
            self._add_job_to_scheduler(job_model)

        logger.info(f"任务已添加: {job_model.job_id}")
        return job_model

    def update_job(self, job_id: str, **kwargs):
        """
        更新任务（单体模式使用）

        Args:
            job_id: 任务ID
            **kwargs: 要更新的字段

        Returns:
            更新后的任务模型
        """
        job_model = self._update_job_model(job_id, **kwargs)

        # 如果任务已启用，重新添加到调度器
        if job_model.enabled:
            try:
                # 先移除旧任务
                self.scheduler.remove_job(job_id)
            except JobLookupError:
                pass
            # 添加新任务
            self._add_job_to_scheduler(job_model)

        logger.info(f"任务已更新: {job_id}")
        return job_model

    def enable_job(self, job_id: str) -> bool:
        """启用任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        if job_model.enabled:
            return True

        job_model.enabled = True
        self.db.session.commit()

        # 添加到调度器
        self._add_job_to_scheduler(job_model)

        logger.info(f"任务已启用: {job_id}")
        return True

    def disable_job(self, job_id: str) -> bool:
        """禁用任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        if not job_model.enabled:
            return True

        job_model.enabled = False
        self.db.session.commit()

        # 从调度器移除
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass

        logger.info(f"任务已禁用: {job_id}")
        return True

    def remove_job(self, job_id: str) -> bool:
        """删除任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        # 从调度器移除
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass

        # 从数据库删除
        self._delete_job_model(job_id)

        logger.info(f"任务已删除: {job_id}")
        return True

    def run_job(self, job_id: str) -> bool:
        """立即执行任务"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        try:
            func = self._get_function(job_model.func)
            args = job_model.args or []
            kwargs = job_model.kwargs or {}
            func(*args, **kwargs)

            # 更新最后执行时间
            job_model.last_run_time = datetime.utcnow()
            self.db.session.commit()

            logger.info(f"任务已执行: {job_id}")
            return True
        except Exception as e:
            logger.error(f"执行任务失败 {job_id}: {str(e)}")
            raise

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        job_model = self.get_job(job_id)
        if not job_model:
            raise ValueError(f"任务 {job_id} 不存在")

        status = {
            'job_id': job_id,
            'enabled': job_model.enabled,
            'next_run_time': job_model.next_run_time.isoformat() if job_model.next_run_time else None,
            'last_run_time': job_model.last_run_time.isoformat() if job_model.last_run_time else None,
        }

        # 尝试从调度器获取实时状态
        try:
            scheduler_job = self.scheduler.get_job(job_id)
            if scheduler_job:
                status['scheduler_enabled'] = True
                status[
                    'next_run_time'] = scheduler_job.next_run_time.isoformat() if scheduler_job.next_run_time else None
            else:
                status['scheduler_enabled'] = False
        except Exception:
            status['scheduler_enabled'] = False

        return status
