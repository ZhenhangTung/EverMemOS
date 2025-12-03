"""
Elasticsearch 租户配置工具函数

本模块提供租户 Elasticsearch 配置相关的工具函数，用于从租户信息中提取 ES 配置。
"""

import os
from typing import Optional, Dict, Any
from hashlib import md5

from core.observation.logger import get_logger
from core.tenants.tenant_contextvar import get_current_tenant
from core.tenants.tenant_config import get_tenant_config

logger = get_logger(__name__)


def get_tenant_es_config() -> Optional[Dict[str, Any]]:
    """
    从当前租户上下文中获取 Elasticsearch 配置

    从租户信息的 storage_info 中提取 Elasticsearch 相关配置。
    如果租户配置不完整或缺失，会从环境变量中补充。

    配置结构示例：
    {
        "hosts": ["http://localhost:9200"],
        "username": "elastic",
        "password": "password",
        "api_key": None,
        "timeout": 120,
        "verify_certs": False
    }

    Returns:
        Elasticsearch 配置字典，如果不存在则返回 None

    Examples:
        >>> config = get_tenant_es_config()
        >>> if config:
        ...     print(f"ES Hosts: {config['hosts']}")
    """
    tenant_info = get_current_tenant()
    if not tenant_info:
        logger.debug("⚠️ 未设置租户上下文，无法获取租户 Elasticsearch 配置")
        return None

    # 从租户的 storage_info 中获取 ES 配置
    # 支持多种配置键名：elasticsearch, es_config, es
    es_config = tenant_info.get_storage_info("elasticsearch")
    if es_config is None:
        es_config = tenant_info.get_storage_info("es_config")
    if es_config is None:
        es_config = tenant_info.get_storage_info("es")

    # 获取环境变量配置作为后备
    env_fallback_config = load_es_config_from_env()

    if not es_config:
        # 租户配置中完全没有 ES 信息，使用环境变量配置
        final_config = {
            "hosts": env_fallback_config.get("hosts", ["http://localhost:9200"]),
            "username": env_fallback_config.get("username"),
            "password": env_fallback_config.get("password"),
            "api_key": env_fallback_config.get("api_key"),
            "timeout": env_fallback_config.get("timeout", 120),
            "verify_certs": env_fallback_config.get("verify_certs", False),
        }
        logger.info(
            "✅ 租户 [%s] 配置中缺少 Elasticsearch 信息，使用环境变量配置补全: hosts=%s",
            tenant_info.tenant_id,
            final_config["hosts"],
        )
        return final_config

    # 兼容逻辑：如果租户配置缺少某些字段，从环境变量中补充
    # 处理 hosts 字段的多种格式
    tenant_hosts = es_config.get("hosts")
    if tenant_hosts is None:
        # 尝试从 host/port 构建
        tenant_host = es_config.get("host")
        tenant_port = es_config.get("port", 9200)
        if tenant_host:
            tenant_hosts = [f"http://{tenant_host}:{tenant_port}"]

    final_config = {
        "hosts": tenant_hosts
        or env_fallback_config.get("hosts", ["http://localhost:9200"]),
        "username": es_config.get("username") or env_fallback_config.get("username"),
        "password": es_config.get("password") or env_fallback_config.get("password"),
        "api_key": es_config.get("api_key") or env_fallback_config.get("api_key"),
        "timeout": es_config.get("timeout") or env_fallback_config.get("timeout", 120),
        "verify_certs": es_config.get(
            "verify_certs", env_fallback_config.get("verify_certs", False)
        ),
    }

    logger.debug(
        "✅ 从租户 [%s] 获取 Elasticsearch 配置: hosts=%s",
        tenant_info.tenant_id,
        final_config["hosts"],
    )

    return final_config


def get_es_connection_cache_key(config: Dict[str, Any]) -> str:
    """
    基于 Elasticsearch 连接配置生成缓存键

    使用连接参数（hosts、认证信息）的哈希值作为缓存键。
    同时作为 elasticsearch-dsl connections 的 alias。

    Args:
        config: Elasticsearch 连接配置字典

    Returns:
        缓存键字符串（MD5 哈希值）

    Examples:
        >>> config = {"hosts": ["http://localhost:9200"], "username": "elastic", "password": "pwd"}
        >>> cache_key = get_es_connection_cache_key(config)
    """
    # 处理 hosts
    hosts = config.get("hosts", [])
    if isinstance(hosts, list):
        hosts_str = ",".join(sorted(hosts))
    else:
        hosts_str = str(hosts)

    # 处理认证信息
    auth_str = ""
    api_key = config.get("api_key")
    username = config.get("username")
    password = config.get("password")

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
    return md5(key_content.encode()).hexdigest()[:16]


def load_es_config_from_env() -> Dict[str, Any]:
    """
    从环境变量加载默认 Elasticsearch 配置

    读取以下环境变量：
    - ES_HOSTS: Elasticsearch 主机列表，逗号分隔（优先）
    - ES_HOST: Elasticsearch 主机地址，默认 localhost
    - ES_PORT: Elasticsearch 端口，默认 9200
    - ES_USERNAME: 用户名（可选）
    - ES_PASSWORD: 密码（可选）
    - ES_API_KEY: API密钥（可选）
    - ES_TIMEOUT: 超时时间（秒），默认 120
    - ES_VERIFY_CERTS: 是否验证证书，默认 false

    Returns:
        Elasticsearch 配置字典

    Examples:
        >>> config = load_es_config_from_env()
        >>> print(f"ES Hosts: {config['hosts']}")
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

    config = {
        "hosts": es_hosts,
        "username": os.getenv("ES_USERNAME"),
        "password": os.getenv("ES_PASSWORD"),
        "api_key": os.getenv("ES_API_KEY"),
        "timeout": int(os.getenv("ES_TIMEOUT", "120")),
        "verify_certs": os.getenv("ES_VERIFY_CERTS", "false").lower() == "true",
    }

    logger.debug("从环境变量加载默认 Elasticsearch 配置: hosts=%s", config["hosts"])

    return config


def get_tenant_aware_index_name(original_name: str) -> str:
    """
    生成租户感知的索引名称

    根据当前租户上下文为索引名称添加租户前缀。
    如果在非租户模式或无租户上下文，返回原始名称。

    命名规则：
    - 添加租户前缀：{tenant_id}_{original_name}
    - 替换特殊字符：将非法字符替换为 "_" 以符合 ES 索引命名规范

    ES 索引命名规范：
    - 只能包含小写字母、数字、下划线、连字符
    - 不能以下划线、连字符开头
    - 不能包含特殊字符

    Args:
        original_name: 原始的索引名称

    Returns:
        str: 租户感知的索引名称

    Examples:
        >>> # 租户模式下
        >>> set_current_tenant(TenantInfo(tenant_id="tenant-001", ...))
        >>> get_tenant_aware_index_name("my_index")
        'tenant-001-my_index'

        >>> # 非租户模式或无租户上下文
        >>> get_tenant_aware_index_name("my_index")
        'my_index'
    """
    try:
        # 检查是否为非租户模式
        config = get_tenant_config()
        if config.non_tenant_mode:
            return original_name

        # 获取当前租户信息
        tenant_info = get_current_tenant()
        if not tenant_info:
            return original_name

        # 生成租户前缀（ES 索引名允许连字符，保持原样）
        tenant_prefix = tenant_info.tenant_id.lower()

        # 返回租户感知的索引名
        return f"{tenant_prefix}-{original_name}"

    except Exception as e:
        logger.warning(
            "生成租户感知的索引名称失败，使用原始名称 [%s]: %s", original_name, e
        )
        return original_name
