"""
Web 服务示例 - 分离部署模式
仅负责数据库操作和发布事件到 Redis Stream
不启动 APScheduler
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_scheduler_manager import WebSchedulerManager
from flask_scheduler_manager.migrations import migrate_database

# 创建Flask应用
app = Flask(__name__)

# 数据库配置（使用共享数据库）
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
app.config['SCHEDULER_STREAM_MAXLEN'] = 10000

# 初始化数据库
db = SQLAlchemy(app)

# 初始化 Web 调度器管理器（不启动 APScheduler）
scheduler_manager = WebSchedulerManager(app, db)

# 初始化数据库表
with app.app_context():
    migrate_database(app, db)
    scheduler_manager.init_db()


# API路由
@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask Scheduler Manager - Web服务（分离部署模式）',
        'mode': 'web',
        'description': '此服务仅负责任务的CRUD操作，不执行任务',
        'endpoints': {
            'GET /jobs': '获取所有任务',
            'GET /jobs/<job_id>': '获取单个任务',
            'POST /jobs': '创建任务',
            'PUT /jobs/<job_id>': '更新任务',
            'DELETE /jobs/<job_id>': '删除任务',
            'POST /jobs/<job_id>/enable': '启用任务',
            'POST /jobs/<job_id>/disable': '禁用任务',
            'GET /jobs/<job_id>/status': '获取任务状态',
            'POST /reload': '重载所有任务',
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


@app.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """获取任务状态"""
    try:
        status = scheduler_manager.get_job_status(job_id)
        return jsonify(status)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/reload', methods=['POST'])
def reload_all_jobs():
    """通知调度器重载所有任务"""
    scheduler_manager.reload_all_jobs()
    return jsonify({'message': '已发送重载所有任务事件'})


if __name__ == '__main__':
    print("=" * 60)
    print("启动 Web 服务（分离部署模式）")
    print("=" * 60)
    print("此服务仅负责：")
    print("  - 任务的 CRUD 操作（存储到数据库）")
    print("  - 发布事件到 Redis Stream")
    print("")
    print("注意：此服务不执行任务！")
    print("请另外启动 scheduler_worker.py 来执行任务")
    print("=" * 60)
    print("")
    print("访问 http://127.0.0.1:5000 查看API文档")

    app.run(debug=True, host='0.0.0.0', port=5000)

