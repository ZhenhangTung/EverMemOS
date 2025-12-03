"""
Elasticsearch 客户端工厂

基于环境变量提供 Elasticsearch 客户端缓存和管理功能。
"""

import os
import asyncio
from typing import Dict, Optional, List, Any
from hashlib import md5
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl.async_connections import connections as async_connections

from core.di.decorators import component
from core.observation.logger import get_logger

logger = get_logger(__name__)


def get_default_es_config() -> Dict[str, Any]:
    """
    基于环境变量获取默认的 Elasticsearch 配置

    环境变量：
    - ES_HOST: Elasticsearch 主机，默认 localhost
    - ES_PORT: Elasticsearch 端口，默认 9200
    - ES_HOSTS: Elasticsearch 主机列表，逗号分隔，优先级高于 ES_HOST
    - ES_USERNAME: 用户名
    - ES_PASSWORD: 密码
    - ES_API_KEY: API密钥
    - ES_TIMEOUT: 超时时间（秒），默认 120

    Returns:
        Dict[str, Any]: 配置字典
    """
    # 获取主机信息
    es_hosts_str = os.getenv("ES_HOSTS")
    if es_hosts_str:
        # ES_HOSTS 已经包含完整的 URL（https://host:port），直接使用
        es_hosts = [host.strip() for host in es_hosts_str.split(",")]
    else:
        # 回退到单个主机配置
        es_host = os.getenv("ES_HOST", "localhost")
        es_port = int(os.getenv("ES_PORT", "9200"))
        es_hosts = [f"http://{es_host}:{es_port}"]

    # 认证信息
    es_username = os.getenv("ES_USERNAME")
    es_password = os.getenv("ES_PASSWORD")
    es_api_key = os.getenv("ES_API_KEY")

    # 连接参数
    es_timeout = int(os.getenv("ES_TIMEOUT", "120"))
    es_verify_certs = os.getenv("ES_VERIFY_CERTS", "false").lower() == "true"

    config = {
        "hosts": es_hosts,
        "timeout": es_timeout,
        "username": es_username,
        "password": es_password,
        "api_key": es_api_key,
        "verify_certs": es_verify_certs,
    }

    logger.info("获取默认 Elasticsearch 配置:")
    logger.info("  主机: %s", es_hosts)
    logger.info("  超时: %s 秒", es_timeout)
    logger.info(
        "  认证: %s", "API Key" if es_api_key else ("Basic" if es_username else "无")
    )

    return config


def get_cache_key(
    hosts: List[str],
    username: Optional[str] = None,
    password: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    生成缓存键（同时作为 elasticsearch-dsl connections 的 alias）
    基于 hosts、认证信息生成唯一标识

    Args:
        hosts: Elasticsearch主机列表
        username: 用户名
        password: 密码
        api_key: API密钥

    Returns:
        str: 缓存键
    """
    hosts_str = ",".join(sorted(hosts))
    auth_str = ""
    if api_key:
        # 使用 api_key 的前8位作为标识
        auth_str = f"api_key:{api_key[:8]}..."
    elif username and password:
        # 使用 username 和 password 的 md5 作为标识
        auth_str = f"basic:{username}:{md5(password.encode()).hexdigest()[:8]}"
    elif username:
        # 只有 username 时，仅使用 username
        auth_str = f"basic:{username}"

    key_content = f"{hosts_str}:{auth_str}"
    return md5(key_content.encode()).hexdigest()


class ElasticsearchClientWrapper:
    """Elasticsearch 客户端包装器"""

    def __init__(self, async_client: AsyncElasticsearch, hosts: List[str]):
        self.async_client = async_client
        self.hosts = hosts

    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            await self.async_client.ping()
            logger.info("✅ Elasticsearch 连接测试成功: %s", self.hosts)
            return True
        except Exception as e:
            logger.error("❌ Elasticsearch 连接测试失败: %s, 错误: %s", self.hosts, e)
            return False

    async def close(self):
        """关闭连接"""
        try:
            if self.async_client:
                await self.async_client.close()
            logger.info("🔌 Elasticsearch 连接已关闭: %s", self.hosts)
        except Exception as e:
            logger.error("关闭 Elasticsearch 连接时出错: %s", e)


@component(name="elasticsearch_client_factory")
class ElasticsearchClientFactory:
    """
    Elasticsearch 客户端工厂
    ### AsyncElasticsearch 是有状态的，因此可以在多个地方使用同一个实例 ###

    提供基于配置的 Elasticsearch 客户端缓存和管理功能
    """

    def __init__(self):
        """初始化 Elasticsearch 客户端工厂"""
        self._clients: Dict[str, ElasticsearchClientWrapper] = {}
        self._lock = asyncio.Lock()
        self._default_config: Optional[Dict[str, Any]] = None
        self._default_client: Optional[ElasticsearchClientWrapper] = None
        logger.info("ElasticsearchClientFactory initialized")

    async def _create_client(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 120,
        **kwargs,
    ) -> ElasticsearchClientWrapper:
        """
        创建 Elasticsearch 客户端实例

        Args:
            hosts: Elasticsearch主机列表
            username: 用户名
            password: 密码
            api_key: API密钥
            timeout: 超时时间（秒）
            **kwargs: 其他连接参数

        Returns:
            ElasticsearchClientWrapper 实例
        """
        # 构建连接参数
        conn_params = {
            "hosts": hosts,
            "timeout": timeout,
            "max_retries": 3,
            "retry_on_timeout": True,
            "verify_certs": False,  # 禁用 SSL 证书验证
            "ssl_show_warn": False,  # 禁用 SSL 警告
            **kwargs,
        }

        # 添加认证信息
        if api_key:
            conn_params["api_key"] = api_key
        elif username and password:
            conn_params["basic_auth"] = (username, password)

        # 生成连接别名（用于 elasticsearch-dsl connections 管理）
        alias = get_cache_key(hosts, username, password, api_key)

        # 通过 async_connections.create_connection 创建异步客户端
        async_client = async_connections.create_connection(alias=alias, **conn_params)

        client_wrapper = ElasticsearchClientWrapper(async_client, hosts)

        logger.info("Created Elasticsearch client for %s with alias %s", hosts, alias)
        return client_wrapper

    async def _get_client(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> ElasticsearchClientWrapper:
        """
        获取 Elasticsearch 客户端实例

        Args:
            hosts: Elasticsearch主机列表
            username: 用户名
            password: 密码
            api_key: API密钥
            **kwargs: 其他配置参数

        Returns:
            ElasticsearchClientWrapper 实例
        """
        cache_key = get_cache_key(hosts, username, password, api_key)

        async with self._lock:
            # 检查缓存
            if cache_key in self._clients:
                logger.debug("Using cached Elasticsearch client for %s", hosts)
                return self._clients[cache_key]

            # 创建新的客户端实例
            logger.info("Creating new Elasticsearch client for %s", hosts)

            client_wrapper = await self._create_client(
                hosts=hosts,
                username=username,
                password=password,
                api_key=api_key,
                **kwargs,
            )

            self._clients[cache_key] = client_wrapper
            logger.info(
                "Elasticsearch client %s created and cached with key %s",
                hosts,
                cache_key,
            )

        return client_wrapper

    async def get_default_client(self) -> ElasticsearchClientWrapper:
        """
        获取基于环境变量配置的默认 Elasticsearch 客户端实例
        不支持获取默认客户端，禁止直接调用factory

        Returns:
            ElasticsearchClientWrapper 实例
        """
        raise NotImplementedError(
            "ElasticsearchClientFactory does not support get_default_client, use register_default_client instead"
        )

    async def register_default_client(self) -> ElasticsearchClientWrapper:
        """
        注册一个默认的客户端

        Returns:
            ElasticsearchClientWrapper 实例
        """
        # 获取或创建默认配置

        if self._default_client is not None:
            return self._default_client

        if self._default_config is None:
            self._default_config = get_default_es_config()

        config = self._default_config
        default_client = await self._get_client(
            hosts=config["hosts"],
            username=config.get("username"),
            password=config.get("password"),
            api_key=config.get("api_key"),
            timeout=config.get("timeout", 120),
        )

        # 注册一个默认的客户端
        async_connections.add_connection(
            alias="default", conn=default_client.async_client
        )
        self._default_client = default_client
        return default_client

    async def remove_client(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> bool:
        """
        移除指定的客户端

        Args:
            hosts: Elasticsearch主机列表
            username: 用户名
            password: 密码
            api_key: API密钥

        Returns:
            bool: 是否成功移除
        """
        cache_key = get_cache_key(hosts, username, password, api_key)

        async with self._lock:
            if cache_key in self._clients:
                client_wrapper = self._clients[cache_key]
                try:
                    await client_wrapper.close()
                except Exception as e:
                    logger.error(
                        "Error closing Elasticsearch client during removal: %s", e
                    )

                del self._clients[cache_key]
                logger.info("Elasticsearch client %s removed from cache", hosts)
                return True
            else:
                logger.warning("Elasticsearch client %s not found in cache", hosts)
                return False

    async def close_all_clients(self) -> None:
        """关闭所有缓存的客户端"""
        async with self._lock:
            for cache_key, client_wrapper in self._clients.items():
                try:
                    await client_wrapper.close()
                except Exception as e:
                    logger.error(
                        "Error closing Elasticsearch client %s: %s", cache_key, e
                    )

            self._clients.clear()
            logger.info("All Elasticsearch clients closed and cleared from cache")
