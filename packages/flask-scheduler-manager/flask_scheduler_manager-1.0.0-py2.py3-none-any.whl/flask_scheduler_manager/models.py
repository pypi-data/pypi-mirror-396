# -*- coding: utf-8 -*-

"""
定时任务数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON

# 全局变量，用于存储db实例
_db = None
_ScheduledJob = None


def init_models(db):
    """
    初始化模型，绑定数据库实例

    Args:
        db: Flask-SQLAlchemy数据库实例
    """
    global _db
    _db = db


def get_scheduled_job_model():
    """
    获取定时任务模型类

    Returns:
        模型类
    """
    if _db is None:
        raise RuntimeError("模型未初始化，请先调用 init_models(db)")

    global _ScheduledJob
    if _ScheduledJob:
        return _ScheduledJob

    class ScheduledJob(_db.Model):
        """
        定时任务模型
        """
        __tablename__ = 'scheduled_jobs'
        # __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        job_id = Column(String(36), unique=True, nullable=False, index=True, comment='任务唯一标识')
        func = Column(String(500), nullable=False, comment='任务函数路径，格式：module:function')
        trigger = Column(String(16), nullable=False, comment='触发器类型：cron或interval')

        # Cron触发器参数
        year = Column(String(4), nullable=True, comment='年')
        month = Column(String(100), nullable=True, comment='月')
        day = Column(String(100), nullable=True, comment='日')
        week = Column(String(100), nullable=True, comment='周')
        day_of_week = Column(String(100), nullable=True, comment='星期几')
        hour = Column(String(100), nullable=True, comment='小时')
        minute = Column(String(100), nullable=True, comment='分钟')
        second = Column(String(100), default='0', nullable=True, comment='秒')

        # Interval触发器参数
        weeks = Column(Integer, nullable=True, comment='间隔周数')
        days = Column(Integer, nullable=True, comment='间隔天数')
        hours = Column(Integer, nullable=True, comment='间隔小时数')
        minutes = Column(Integer, nullable=True, comment='间隔分钟数')
        seconds = Column(Integer, nullable=True, comment='间隔秒数')
        start_date = Column(DateTime, nullable=True, comment='开始时间')
        end_date = Column(DateTime, nullable=True, comment='结束时间')

        # 任务参数
        args = Column(JSON, nullable=True, comment='位置参数')
        kwargs = Column(JSON, nullable=True, comment='关键字参数')
        max_instances = Column(Integer, default=1, comment='最大并发实例数')
        misfire_grace_time = Column(Integer, nullable=True, comment='错过执行时间容忍度（秒）')

        # 状态管理
        enabled = Column(Boolean, default=True, nullable=False, index=True, comment='是否启用')
        next_run_time = Column(DateTime, nullable=True, comment='下次执行时间')
        last_run_time = Column(DateTime, nullable=True, comment='上次执行时间')

        # 元数据
        name = Column(String(255), nullable=True, comment='任务名称')
        description = Column(Text, nullable=True, comment='任务描述')
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
                            comment='更新时间')

        def __repr__(self):
            return f'<ScheduledJob {self.job_id}>'

        def to_dict(self):
            """转换为字典"""
            return {
                'id': self.id,
                'job_id': self.job_id,
                'func': self.func,
                'trigger': self.trigger,
                'year': self.year,
                'month': self.month,
                'day': self.day,
                'week': self.week,
                'day_of_week': self.day_of_week,
                'hour': self.hour,
                'minute': self.minute,
                'second': self.second,
                'weeks': self.weeks,
                'days': self.days,
                'hours': self.hours,
                'minutes': self.minutes,
                'seconds': self.seconds,
                'start_date': self.start_date.isoformat() if self.start_date else None,
                'end_date': self.end_date.isoformat() if self.end_date else None,
                'args': self.args,
                'kwargs': self.kwargs,
                'max_instances': self.max_instances,
                'misfire_grace_time': self.misfire_grace_time,
                'enabled': self.enabled,
                'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
                'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
                'name': self.name,
                'description': self.description,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }

    _ScheduledJob = ScheduledJob
    return ScheduledJob
