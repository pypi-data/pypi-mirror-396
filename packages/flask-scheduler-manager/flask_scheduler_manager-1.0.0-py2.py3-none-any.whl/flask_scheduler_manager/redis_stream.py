# -*- coding: utf-8 -*-

"""
Redis Stream 事件发布与消费模块
用于 Web 服务和调度器服务分离部署时的任务同步
"""
import json
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


class JobEventProducer:
    """
    任务事件生产者
    Web 服务使用此类将任务变更事件发布到 Redis Stream
    """

    def __init__(self, redis_client, stream_key: str = 'scheduler:job_events',
                 maxlen: int = 10000):
        """
        初始化生产者

        Args:
            redis_client: Redis 客户端实例
            stream_key: Stream 的键名
            maxlen: Stream 最大长度，超过后自动裁剪旧消息
        """
        self.redis = redis_client
        self.stream_key = stream_key
        self.maxlen = maxlen

    def publish(self, action: str, job_id: str = None) -> Optional[str]:
        """
        发布任务事件到 Stream

        Args:
            action: 事件动作类型 (add/update/delete/enable/disable/reload_all)
            job_id: 任务ID，reload_all 时可为空

        Returns:
            消息ID，失败时返回 None
        """
        try:
            message = {
                'action': action,
                'job_id': job_id or '',
                'timestamp': str(time.time())
            }

            # XADD 添加消息到 Stream，使用 MAXLEN 自动裁剪
            message_id = self.redis.xadd(
                self.stream_key,
                message,
                maxlen=self.maxlen,
                approximate=True  # 使用近似裁剪，性能更好
            )

            logger.info(f"已发布事件: action={action}, job_id={job_id}, message_id={message_id}")
            return message_id

        except Exception as e:
            logger.error(f"发布事件失败: {str(e)}")
            return None

    def publish_add(self, job_id: str) -> Optional[str]:
        """发布任务添加事件"""
        return self.publish('add', job_id)

    def publish_update(self, job_id: str) -> Optional[str]:
        """发布任务更新事件"""
        return self.publish('update', job_id)

    def publish_delete(self, job_id: str) -> Optional[str]:
        """发布任务删除事件"""
        return self.publish('delete', job_id)

    def publish_enable(self, job_id: str) -> Optional[str]:
        """发布任务启用事件"""
        return self.publish('enable', job_id)

    def publish_disable(self, job_id: str) -> Optional[str]:
        """发布任务禁用事件"""
        return self.publish('disable', job_id)

    def publish_reload_all(self) -> Optional[str]:
        """发布重载所有任务事件"""
        return self.publish('reload_all')


class JobEventConsumer:
    """
    任务事件消费者
    调度器服务使用此类消费 Redis Stream 中的任务变更事件
    支持消费者组模式，可多实例部署
    """

    def __init__(self, redis_client, stream_key: str = 'scheduler:job_events',
                 group_name: str = 'scheduler_workers',
                 consumer_name: str = 'worker_1',
                 block_ms: int = 5000,
                 batch_size: int = 10):
        """
        初始化消费者

        Args:
            redis_client: Redis 客户端实例
            stream_key: Stream 的键名
            group_name: 消费者组名称
            consumer_name: 消费者名称，多实例时需不同
            block_ms: 阻塞等待时间（毫秒）
            batch_size: 每次读取的消息数量
        """
        self.redis = redis_client
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.block_ms = block_ms
        self.batch_size = batch_size

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._handler: Optional[Callable] = None

    def _ensure_group(self):
        """
        确保消费者组存在
        如果不存在则创建，已存在则忽略错误
        """
        import redis
        try:
            # 尝试创建消费者组，从 Stream 开头开始消费
            # 使用 MKSTREAM 参数，如果 Stream 不存在则创建
            self.redis.xgroup_create(
                self.stream_key,
                self.group_name,
                id='0',  # 从头开始
                mkstream=True  # 如果 Stream 不存在则创建
            )
            logger.info(f"已创建消费者组: {self.group_name}")
        except redis.exceptions.ResponseError as e:
            # BUSYGROUP 错误表示组已存在，这是正常的
            if 'BUSYGROUP' in str(e):
                logger.debug(f"消费者组已存在: {self.group_name}")
            else:
                logger.error(f"创建消费者组失败: {str(e)}")
                raise

    def _process_pending(self, handler: Callable):
        """
        处理 pending 状态的消息（故障恢复）
        这些是之前读取但未 ACK 的消息

        Args:
            handler: 消息处理函数
        """
        try:
            # 读取当前消费者的 pending 消息
            # 使用 '0' 表示从 pending 列表开头读取
            pending_messages = self.redis.xreadgroup(
                self.group_name,
                self.consumer_name,
                {self.stream_key: '0'},  # '0' 读取 pending 消息
                count=self.batch_size,
                block=None  # 不阻塞，立即返回
            )

            if pending_messages:
                for stream_name, messages in pending_messages:
                    for message_id, data in messages:
                        self._handle_message(message_id, data, handler)

        except Exception as e:
            logger.error(f"处理 pending 消息失败: {str(e)}")

    def _handle_message(self, message_id: str, data: Dict[str, Any],
                        handler: Callable) -> bool:
        """
        处理单条消息

        Args:
            message_id: 消息ID
            data: 消息数据
            handler: 处理函数

        Returns:
            是否处理成功
        """
        try:
            # 解码消息数据（Redis 返回的是 bytes）
            decoded_data = {}
            for key, value in data.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                decoded_data[key] = value

            action = decoded_data.get('action')
            job_id = decoded_data.get('job_id')

            logger.debug(f"处理消息: message_id={message_id}, action={action}, job_id={job_id}")

            # 调用处理函数
            handler(action, job_id if job_id else None)

            # 确认消息已处理
            self.redis.xack(self.stream_key, self.group_name, message_id)
            logger.debug(f"消息已确认: {message_id}")

            return True

        except Exception as e:
            logger.error(f"处理消息失败 {message_id}: {str(e)}")
            return False

    def _consume_loop(self, handler: Callable):
        """
        消费循环

        Args:
            handler: 消息处理函数 (action: str, job_id: Optional[str]) -> None
        """
        logger.info(f"消费者启动: group={self.group_name}, consumer={self.consumer_name}")

        # 首先处理 pending 消息（故障恢复）
        self._process_pending(handler)

        while self._running:
            try:
                # 读取新消息，使用 '>' 表示只读取新消息
                messages = self.redis.xreadgroup(
                    self.group_name,
                    self.consumer_name,
                    {self.stream_key: '>'},  # '>' 只读取新消息
                    count=self.batch_size,
                    block=self.block_ms
                )

                if messages:
                    for stream_name, stream_messages in messages:
                        for message_id, data in stream_messages:
                            self._handle_message(message_id, data, handler)

            except Exception as e:
                if self._running:  # 只在运行状态下记录错误
                    logger.error(f"消费循环错误: {str(e)}")
                    time.sleep(1)  # 出错后短暂等待

        logger.info("消费者已停止")

    def start(self, handler: Callable):
        """
        启动消费者（非阻塞，启动后台线程）

        Args:
            handler: 消息处理函数，签名: (action: str, job_id: Optional[str]) -> None
        """
        if self._running:
            logger.warning("消费者已在运行中")
            return

        self._handler = handler
        self._running = True

        # 确保消费者组存在
        self._ensure_group()

        # 启动消费线程
        self._thread = threading.Thread(
            target=self._consume_loop,
            args=(handler,),
            daemon=True,
            name=f"JobEventConsumer-{self.consumer_name}"
        )
        self._thread.start()

        logger.info(f"消费者线程已启动: {self._thread.name}")

    def start_blocking(self, handler: Callable):
        """
        启动消费者（阻塞模式，用于独立运行的 worker）

        Args:
            handler: 消息处理函数
        """
        self._handler = handler
        self._running = True

        # 确保消费者组存在
        self._ensure_group()

        # 在当前线程运行消费循环
        self._consume_loop(handler)

    def stop(self):
        """
        停止消费者
        """
        if not self._running:
            return

        logger.info("正在停止消费者...")
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.block_ms / 1000 + 1)

        self._thread = None
        logger.info("消费者已停止")

    @property
    def is_running(self) -> bool:
        """消费者是否在运行"""
        return self._running


def create_redis_client(redis_url: str = None, cluster_nodes: list = None,
                        cluster_mode: bool = False, **kwargs):
    """
    创建 Redis 客户端（支持单机模式和集群模式）

    Args:
        redis_url: Redis 连接 URL（单机模式），如 redis://localhost:6379/0
        cluster_nodes: 集群节点列表（集群模式），格式：
            [
                {'host': '127.0.0.1', 'port': 7000},
                {'host': '127.0.0.1', 'port': 7001},
                ...
            ]
        cluster_mode: 是否使用集群模式，默认 False
        **kwargs: 其他 Redis 客户端参数

    Returns:
        Redis 客户端实例（Redis 或 RedisCluster）

    Examples:
        # 单机模式
        client = create_redis_client(redis_url='redis://localhost:6379/0')

        # 集群模式（通过节点列表）
        client = create_redis_client(
            cluster_nodes=[
                {'host': '127.0.0.1', 'port': 7000},
                {'host': '127.0.0.1', 'port': 7001},
            ],
            cluster_mode=True
        )

        # 集群模式（通过 URL，自动检测）
        client = create_redis_client(
            redis_url='redis://127.0.0.1:7000',
            cluster_mode=True
        )
    """
    import redis

    if cluster_mode or cluster_nodes:
        # 集群模式
        return _create_cluster_client(redis_url, cluster_nodes, **kwargs)
    else:
        # 单机模式
        if not redis_url:
            raise ValueError("单机模式需要提供 redis_url 参数")
        return redis.from_url(redis_url, decode_responses=False, **kwargs)


def _create_cluster_client(redis_url: str = None, cluster_nodes: list = None, **kwargs):
    """
    创建 Redis 集群客户端

    Args:
        redis_url: 集群中任一节点的 URL
        cluster_nodes: 集群节点列表
        **kwargs: 其他参数

    Returns:
        RedisCluster 客户端实例
    """
    from redis.cluster import RedisCluster, ClusterNode

    startup_nodes = []

    if cluster_nodes:
        # 使用节点列表
        for node in cluster_nodes:
            startup_nodes.append(ClusterNode(
                host=node.get('host', 'localhost'),
                port=node.get('port', 6379)
            ))
    elif redis_url:
        startup_nodes = [ClusterNode(*addr.split(":")) for addr in redis_url.split(",")]
    else:
        raise ValueError("集群模式需要提供 redis_url 或 cluster_nodes 参数")

    # 设置默认参数
    kwargs.setdefault('decode_responses', False)
    kwargs.setdefault('skip_full_coverage_check', True)

    return RedisCluster(startup_nodes=startup_nodes, **kwargs)


class RedisClientFactory:
    """
    Redis 客户端工厂类
    用于根据配置创建合适的 Redis 客户端
    """

    @staticmethod
    def create_from_config(config: dict):
        """
        根据配置字典创建 Redis 客户端

        Args:
            config: 配置字典，支持以下格式：
                单机模式：
                {
                    'url': 'redis://localhost:6379/0'
                }
                或
                {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'password': 'xxx'  # 可选
                }

                集群模式：
                {
                    'cluster': True,
                    'nodes': [
                        {'host': '127.0.0.1', 'port': 7000},
                        {'host': '127.0.0.1', 'port': 7001},
                    ]
                }
                或
                {
                    'cluster': True,
                    'url': 'redis://127.0.0.1:7000'  # 集群中任一节点
                }

        Returns:
            Redis 客户端实例
        """
        import redis

        cluster_mode = config.get('cluster', False)

        if cluster_mode:
            # 集群模式
            nodes = config.get('nodes')
            url = config.get('url')
            return create_redis_client(
                redis_url=url,
                cluster_nodes=nodes,
                cluster_mode=True,
                password=config.get('password')
            )
        else:
            # 单机模式
            url = config.get('url')
            if url:
                return redis.from_url(url, decode_responses=False)
            else:
                # 使用 host/port 配置
                return redis.Redis(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 6379),
                    db=config.get('db', 0),
                    password=config.get('password'),
                    decode_responses=False
                )

    @staticmethod
    def create_from_app_config(app_config: dict):
        """
        从 Flask 应用配置创建 Redis 客户端

        支持的配置项：
            SCHEDULER_REDIS_URL: Redis URL（单机模式）
            SCHEDULER_REDIS_CLUSTER: 是否集群模式（默认 False）
            SCHEDULER_REDIS_CLUSTER_NODES: 集群节点列表
            SCHEDULER_REDIS_PASSWORD: Redis 密码（可选）

        Args:
            app_config: Flask 应用配置字典

        Returns:
            Redis 客户端实例
        """
        cluster_mode = app_config.get('SCHEDULER_REDIS_CLUSTER', False)
        redis_url = app_config.get('SCHEDULER_REDIS_URL')
        cluster_nodes = app_config.get('SCHEDULER_REDIS_CLUSTER_NODES')
        password = app_config.get('SCHEDULER_REDIS_PASSWORD')

        extra_kwargs = {}
        if password:
            extra_kwargs['password'] = password

        return create_redis_client(
            redis_url=redis_url,
            cluster_nodes=cluster_nodes,
            cluster_mode=cluster_mode,
            **extra_kwargs
        )
