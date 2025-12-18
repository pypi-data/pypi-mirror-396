"""
调度器服务示例 - 分离部署模式
负责执行定时任务，监听 Redis Stream 中的任务变更事件
"""
import signal
import sys
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_scheduler_manager import SchedulerManager
from flask_scheduler_manager.migrations import migrate_database

# 创建Flask应用
app = Flask(__name__)

# 数据库配置（与 Web 服务共享同一数据库）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ============ Redis 配置 ============
# 方式一：单机模式（默认）
app.config['SCHEDULER_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['SCHEDULER_REDIS_CLUSTER'] = False  # 默认为 False

# 方式二：集群模式（取消下面的注释启用）
# app.config['SCHEDULER_REDIS_CLUSTER'] = True
# app.config['SCHEDULER_REDIS_CLUSTER_NODES'] = [
#     {'host': '127.0.0.1', 'port': 7000},
#     {'host': '127.0.0.1', 'port': 7001},
#     {'host': '127.0.0.1', 'port': 7002},
# ]
# app.config['SCHEDULER_REDIS_PASSWORD'] = None  # 如需密码

# Stream 配置
app.config['SCHEDULER_STREAM_KEY'] = 'scheduler:job_events'
app.config['SCHEDULER_CONSUMER_GROUP'] = 'scheduler_workers'
app.config['SCHEDULER_CONSUMER_NAME'] = 'worker_1'  # 多实例时使用不同的名称

# 初始化数据库
db = SQLAlchemy(app)

# 初始化调度器管理器（会启动 APScheduler）
scheduler_manager = SchedulerManager(app, db)

# 初始化数据库表
with app.app_context():
    migrate_database(app, db)
    scheduler_manager.init_db()


# ============ 示例任务函数 ============

def task_print_hello():
    """打印Hello的任务"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hello from scheduled task!")


def task_print_time():
    """打印当前时间的任务"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Current time: {time.time()}")


def task_with_args(message: str, count: int = 1):
    """带参数的任务"""
    for i in range(count):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Message {i + 1}: {message}")


# ============ 主程序 ============

def shutdown_handler(signum, frame):
    """优雅关闭处理"""
    print("\n收到关闭信号，正在停止...")
    scheduler_manager.stop_event_listener()
    sys.exit(0)


if __name__ == '__main__':
    # 注册信号处理
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print("=" * 60)
    print("启动调度器服务（分离部署模式）")
    print("=" * 60)
    print("此服务负责：")
    print("  - 执行定时任务（APScheduler）")
    print("  - 监听 Redis Stream 中的任务变更事件")
    print("")
    print(f"消费者组: {app.config['SCHEDULER_CONSUMER_GROUP']}")
    print(f"消费者名: {app.config['SCHEDULER_CONSUMER_NAME']}")
    print("=" * 60)
    print("")

    # 启动事件监听器
    scheduler_manager.start_event_listener()

    print("调度器服务已启动，等待任务...")
    print("按 Ctrl+C 停止服务")
    print("")

    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

