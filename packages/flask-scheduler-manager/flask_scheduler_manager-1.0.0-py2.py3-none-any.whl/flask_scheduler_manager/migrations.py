# -*- coding: utf-8 -*-
"""
数据库迁移工具
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_scheduler_manager.models import init_models, get_scheduled_job_model


def init_migration(app: Flask, db: SQLAlchemy):
    """
    初始化数据库迁移

    Args:
        app: Flask应用实例
        db: SQLAlchemy数据库实例
    """
    with app.app_context():
        # 初始化模型
        init_models(db)
        ScheduledJob = get_scheduled_job_model()

        # 创建所有表
        db.create_all()
        print("数据库表创建完成")


def migrate_database(app: Flask, db: SQLAlchemy):
    """
    执行数据库迁移（一键迁移）

    Args:
        app: Flask应用实例
        db: SQLAlchemy数据库实例
    """
    with app.app_context():
        try:
            # 初始化模型
            init_models(db)
            ScheduledJob = get_scheduled_job_model()

            # 检查表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if 'scheduled_jobs' not in existing_tables:
                print("创建 scheduled_jobs 表...")
                db.create_all()
                print("✓ 数据库迁移完成")
            else:
                print("表已存在，跳过创建")

        except Exception as e:
            print(f"数据库迁移失败: {str(e)}")
            raise


def reset_database(app: Flask, db: SQLAlchemy):
    """
    重置数据库（删除所有表并重新创建）

    Args:
        app: Flask应用实例
        db: SQLAlchemy数据库实例
    """
    with app.app_context():
        try:
            # 初始化模型
            init_models(db)
            ScheduledJob = get_scheduled_job_model()

            print("删除所有表...")
            db.drop_all()
            print("创建所有表...")
            db.create_all()
            print("✓ 数据库重置完成")
        except Exception as e:
            print(f"数据库重置失败: {str(e)}")
            raise

