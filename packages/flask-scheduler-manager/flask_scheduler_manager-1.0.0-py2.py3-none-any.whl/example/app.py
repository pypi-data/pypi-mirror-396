"""
示例应用 - 演示如何使用Flask Scheduler Manager
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_scheduler_manager import SchedulerManager
from flask_scheduler_manager.migrations import migrate_database
import time

# 创建Flask应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example_scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SCHEDULER_API_ENABLED'] = True

# 初始化数据库
db = SQLAlchemy(app)

# 初始化调度器管理器
scheduler_manager = SchedulerManager(app, db)

# 初始化数据库表
with app.app_context():
    migrate_database(app, db)
    scheduler_manager.init_db()


# 示例任务函数
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


# API路由
@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask Scheduler Manager 示例应用',
        'endpoints': {
            'GET /jobs': '获取所有任务',
            'GET /jobs/<job_id>': '获取单个任务',
            'POST /jobs': '创建任务',
            'PUT /jobs/<job_id>': '更新任务',
            'DELETE /jobs/<job_id>': '删除任务',
            'POST /jobs/<job_id>/enable': '启用任务',
            'POST /jobs/<job_id>/disable': '禁用任务',
            'POST /jobs/<job_id>/run': '立即执行任务',
            'GET /jobs/<job_id>/status': '获取任务状态',
        }
    })


@app.route('/jobs', methods=['GET'])
def get_jobs():
    """获取所有任务"""
    enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
    jobs = scheduler_manager.get_all_jobs(enabled_only=enabled_only)
    return jsonify({
        'count': len(jobs),
        'jobs': [job.to_dict() for job in jobs]
    })


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """获取单个任务"""
    job = scheduler_manager.get_job(job_id)
    if not job:
        return jsonify({'error': '任务不存在'}), 404
    return jsonify(job.to_dict())


@app.route('/jobs', methods=['POST'])
def create_job():
    """创建任务"""
    data = request.get_json()

    try:
        job = scheduler_manager.add_job(
            job_id=data['job_id'],
            func=data['func'],
            trigger=data.get('trigger', 'cron'),
            enabled=data.get('enabled', True),
            name=data.get('name'),
            description=data.get('description'),
            **{k: v for k, v in data.items() if
               k not in ['job_id', 'func', 'trigger', 'enabled', 'name', 'description']}
        )
        return jsonify(job.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """更新任务"""
    data = request.get_json()

    try:
        job = scheduler_manager.update_job(job_id, **data)
        return jsonify(job.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """删除任务"""
    try:
        scheduler_manager.remove_job(job_id)
        return jsonify({'message': '任务已删除'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/jobs/<job_id>/enable', methods=['POST'])
def enable_job(job_id):
    """启用任务"""
    try:
        scheduler_manager.enable_job(job_id)
        return jsonify({'message': '任务已启用'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/jobs/<job_id>/disable', methods=['POST'])
def disable_job(job_id):
    """禁用任务"""
    try:
        scheduler_manager.disable_job(job_id)
        return jsonify({'message': '任务已禁用'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/jobs/<job_id>/run', methods=['POST'])
def run_job(job_id):
    """立即执行任务"""
    try:
        scheduler_manager.run_job(job_id)
        return jsonify({'message': '任务已执行'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """获取任务状态"""
    try:
        status = scheduler_manager.get_job_status(job_id)
        return jsonify(status)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    # 添加一些示例任务
    with app.app_context():
        try:
            # 每5秒执行一次的任务
            scheduler_manager.add_job(
                job_id='task_hello',
                func='example.app:task_print_hello',
                trigger='interval',
                seconds=5,
                enabled=True,
                name='Hello任务',
                description='每5秒打印一次Hello'
            )

            # 每分钟执行一次的任务
            scheduler_manager.add_job(
                job_id='task_time',
                func='example.app:task_print_time',
                trigger='cron',
                minute='*',
                enabled=True,
                name='时间任务',
                description='每分钟打印当前时间'
            )

            # 带参数的任务（每10秒执行一次）
            scheduler_manager.add_job(
                job_id='task_with_args',
                func='example.app:task_with_args',
                trigger='interval',
                seconds=10,
                args=['Hello World'],
                kwargs={'count': 2},
                enabled=True,
                name='带参数任务',
                description='每10秒执行一次，带参数'
            )

            print("示例任务已添加")
        except Exception as e:
            print(f"添加示例任务失败（可能已存在）: {str(e)}")

    print("启动Flask应用...")
    print("访问 http://127.0.0.1:5000 查看API文档")
    app.run(debug=True, host='0.0.0.0', port=5000)

