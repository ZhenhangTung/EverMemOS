"""
租户感知的 Elasticsearch AsyncDocument

本模块通过继承 AliasSupportDoc 并覆盖关键方法来实现租户感知能力。
核心思路：根据租户上下文动态返回正确的连接和索引名称。
"""

from typing import Optional, Any, Dict, Type
from fnmatch import fnmatch
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl.async_connections import connections as async_connections

from core.observation.logger import get_logger
from core.tenants.tenant_contextvar import get_current_tenant
from core.tenants.tenant_models import TenantPatchKey
from core.tenants.tenantize.oxm.es.config_utils import (
    get_tenant_es_config,
    get_es_connection_cache_key,
    load_es_config_from_env,
    get_tenant_aware_index_name,
)
from core.tenants.tenantize.tenant_cache_utils import get_or_compute_tenant_cache
from core.oxm.es.doc_base import AliasSupportDoc

logger = get_logger(__name__)


class TenantAwareAsyncDocument(AliasSupportDoc):
    """
    租户感知的 Elasticsearch AsyncDocument

    通过继承 AliasSupportDoc 并覆盖关键方法来实现租户感知。
    核心功能：根据当前租户上下文，自动选择并返回正确的 ES 连接和索引。

    核心特性：
    1. 租户隔离：不同租户使用不同的 ES 连接（通过 alias 别名区分）
    2. 索引隔离：不同租户使用不同的索引名（添加租户前缀）
    3. 连接复用：相同配置的租户共享同一个连接（通过 cache_key 缓存）
    4. 自动注册：首次访问时自动注册租户连接
    5. 后备连接：非租户模式或无租户上下文时使用默认连接

    使用方式：
        >>> # 定义租户感知的文档类
        >>> class MyDoc(TenantAwareAsyncDocument):
        ...     title = field.Text()
        ...
        ...     class Index:
        ...         name = "my_index"

    注意事项：
    - 传入的 using 参数会被忽略，实际使用的是租户感知的连接别名
    - 第一次访问时会自动注册连接
    - 连接别名和配置会缓存在 tenant_info_patch 中，避免重复计算
    """

    class Meta:
        abstract = True

    # ============================================================
    # 租户感知的连接管理
    # ============================================================

    @classmethod
    def _get_using(cls, using: Optional[str] = None) -> str:
        """
        覆盖父类方法，返回租户感知的连接别名

        忽略传入的 using 参数，根据租户上下文返回正确的连接别名。

        Args:
            using: 连接别名（会被忽略）

        Returns:
            str: 租户感知的连接别名
        """
        return cls._get_tenant_aware_using()

    @classmethod
    def _get_connection(cls, using: Optional[str] = None) -> AsyncElasticsearch:
        """
        覆盖父类方法，返回租户感知的连接

        这是核心方法：每次需要访问 ES 时都会调用此方法获取连接。
        我们在这里根据租户上下文动态返回正确的连接。

        Args:
            using: 连接别名（会被忽略）

        Returns:
            AsyncElasticsearch: 租户感知的 ES 客户端
        """
        # 动态获取当前租户的连接别名
        tenant_using = cls._get_tenant_aware_using()

        # 确保连接已注册
        cls._ensure_connection_registered(tenant_using)

        # 返回对应的连接
        return async_connections.get_connection(tenant_using)

    @classmethod
    def _get_tenant_aware_using(cls) -> str:
        """
        获取租户感知的连接别名

        根据配置和上下文决定返回哪个连接别名：
        1. 如果启用非租户模式，返回 "default"
        2. 如果启用租户模式，根据当前租户配置返回对应的连接别名
        3. 如果租户模式下没有租户上下文，返回 "default"

        Returns:
            str: elasticsearch-dsl 连接别名（using）
        """

        def compute_using() -> str:
            """计算租户连接别名"""
            # 从租户配置中获取 ES 配置
            es_config = get_tenant_es_config()
            if not es_config:
                raise RuntimeError("租户缺少 Elasticsearch 配置")

            # 基于连接参数生成唯一的连接别名
            cache_key = get_es_connection_cache_key(es_config)
            return f"tenant_{cache_key}"

        return get_or_compute_tenant_cache(
            patch_key=TenantPatchKey.ES_CONNECTION_CACHE_KEY,
            compute_func=compute_using,
            fallback="default",  # 具体值，不需要延迟计算
            cache_description="Elasticsearch 连接别名",
        )

    @classmethod
    def _ensure_connection_registered(cls, using: str) -> None:
        """
        确保指定的连接别名已注册

        如果连接尚未注册，会自动注册连接。

        Args:
            using: 连接别名

        注意：
            - 对于 "default" 连接，假设已经在应用启动时注册
            - 对于租户连接（tenant_*），如果未注册则自动注册
        """
        # 检查连接是否已存在
        try:
            async_connections.get_connection(using)
            # 连接已存在，直接返回
            return
        except Exception:
            # 连接不存在，需要注册
            pass

        # 如果是默认连接，尝试从环境变量注册
        if using == "default":
            logger.info("📋 注册默认 Elasticsearch 连接")
            config = load_es_config_from_env()
            cls._register_connection(config, using)
            return

        # 租户连接：从租户配置注册
        try:
            tenant_info = get_current_tenant()
            if not tenant_info:
                raise RuntimeError("无法注册租户连接：未设置租户上下文")

            es_config = get_tenant_es_config()
            if not es_config:
                raise RuntimeError(
                    f"无法注册租户连接：租户 {tenant_info.tenant_id} 缺少 Elasticsearch 配置"
                )

            logger.info(
                "📋 为租户 [%s] 注册 Elasticsearch 连接 [using=%s]",
                tenant_info.tenant_id,
                using,
            )

            cls._register_connection(es_config, using)

        except Exception as e:
            logger.error("注册租户连接失败 [using=%s]: %s", using, e)
            raise

    @classmethod
    def _register_connection(cls, config: Dict[str, Any], using: str) -> None:
        """
        注册 Elasticsearch 连接

        Args:
            config: Elasticsearch 连接配置
            using: 连接别名

        注意：
            - 使用 elasticsearch-dsl 的 connections 管理器来创建连接
            - 这样可以复用现有的连接池管理逻辑
        """
        try:
            # 构建连接参数
            conn_params = {
                "hosts": config.get("hosts", ["http://localhost:9200"]),
                "timeout": config.get("timeout", 120),
                "max_retries": 3,
                "retry_on_timeout": True,
                "verify_certs": config.get("verify_certs", False),
                "ssl_show_warn": False,
            }

            # 添加认证信息
            api_key = config.get("api_key")
            username = config.get("username")
            password = config.get("password")

            if api_key:
                conn_params["api_key"] = api_key
            elif username and password:
                conn_params["basic_auth"] = (username, password)

            # 通过 async_connections.create_connection 创建连接
            async_connections.create_connection(alias=using, **conn_params)

            logger.info(
                "✅ Elasticsearch 连接已注册 [using=%s, hosts=%s]",
                using,
                conn_params["hosts"],
            )

        except Exception as e:
            logger.error("注册 Elasticsearch 连接失败 [using=%s]: %s", using, e)
            raise

    # ============================================================
    # 租户感知的索引管理
    # ============================================================

    @classmethod
    def get_original_index_name(cls) -> str:
        """
        获取原始索引名称（不带租户前缀）

        从 cls._index._name 获取原始配置的索引名。

        Returns:
            str: 原始索引名称
        """
        if hasattr(cls, '_index') and hasattr(cls._index, '_name'):
            return cls._index._name
        raise ValueError(f"文档类 {cls.__name__} 没有正确的索引配置")

    @classmethod
    def get_index_name(cls) -> str:
        """
        覆盖父类方法，返回租户感知的索引名称

        根据当前租户上下文为索引名称添加租户前缀。
        如果在非租户模式或无租户上下文，返回原始名称。

        Returns:
            str: 租户感知的索引名称
        """
        original_name = cls.get_original_index_name()
        return get_tenant_aware_index_name(original_name)

    @classmethod
    def _matches(cls, hit: Dict[str, Any]) -> bool:
        """
        覆盖父类方法，匹配租户感知的索引模式

        用于从 ES 响应中过滤属于当前租户的文档。

        Args:
            hit: ES 命中结果

        Returns:
            bool: 是否匹配当前文档类
        """
        # 获取租户感知的索引名
        tenant_index_name = cls.get_index_name()

        # 构建匹配模式
        pattern = f"{tenant_index_name}-*"

        return fnmatch(hit.get("_index", ""), pattern)

    @classmethod
    def _default_index(cls, index: Optional[str] = None) -> str:
        """
        覆盖父类方法，返回租户感知的默认索引名

        Args:
            index: 可选的索引名覆盖

        Returns:
            str: 租户感知的索引名
        """
        if index:
            return index
        return cls.get_index_name()

    def _get_index(
        self, index: Optional[str] = None, required: bool = True
    ) -> Optional[str]:
        """
        覆盖父类方法，返回租户感知的索引名

        Args:
            index: 可选的索引名覆盖
            required: 是否必须返回索引名

        Returns:
            Optional[str]: 索引名

        Raises:
            ValidationException: 如果 required=True 且无法获取索引名
        """
        # 如果显式提供了 index，直接使用
        if index is not None:
            return index

        # 尝试从 meta 中获取
        if hasattr(self, 'meta') and hasattr(self.meta, 'index'):
            meta_index = getattr(self.meta, 'index', None)
            if meta_index:
                return meta_index

        # 返回租户感知的默认索引名
        tenant_index = self.get_index_name()
        if tenant_index:
            return tenant_index

        # 如果必须返回索引名但无法获取，抛出异常
        if required:
            from elasticsearch.dsl.exceptions import ValidationException

            raise ValidationException("No index")

        return None

    @classmethod
    def dest(cls) -> str:
        """
        覆盖父类方法，生成租户感知的目标索引名（带时间戳）

        Returns:
            str: 带时间戳的目标索引名
        """
        # 使用租户感知的索引名生成目标名
        tenant_index_name = cls.get_index_name()
        from common_utils.datetime_utils import get_now_with_timezone

        now = get_now_with_timezone()
        return f"{tenant_index_name}-{now.strftime('%Y%m%d%H%M%S%f')}"


def TenantAwareAliasDoc(
    doc_name: str, number_of_shards: int = 2
) -> Type[TenantAwareAsyncDocument]:
    """
    创建租户感知的支持别名模式的ES文档类

    这是一个工厂函数，用于创建租户感知的文档类。
    自动处理日期字段的时区和租户隔离。

    Args:
        doc_name: 文档名称（原始索引名）
        number_of_shards: 分片数量

    Returns:
        租户感知的文档类

    Examples:
        >>> # 创建租户感知的文档类
        >>> class MyDoc(TenantAwareAliasDoc("my_docs")):
        ...     title = field.Text()
        ...     content = field.Text()
    """
    from elasticsearch.dsl import MetaField
    from core.oxm.es.es_utils import get_index_ns

    # 如果有 namespace，添加到文档名
    if get_index_ns():
        doc_name = f"{doc_name}-{get_index_ns()}"

    class GeneratedTenantAwareDoc(TenantAwareAsyncDocument):
        # 保存原始文档名，供租户感知方法使用
        _ORIGINAL_DOC_NAME = doc_name
        PATTERN = f"{doc_name}-*"

        class Index:
            name = doc_name
            settings = {
                "number_of_shards": number_of_shards,
                "number_of_replicas": 1,
                "refresh_interval": "60s",
                "max_ngram_diff": 50,
                "max_shingle_diff": 10,
            }

        class Meta:
            dynamic = MetaField("strict")

        @classmethod
        def get_original_index_name(cls) -> str:
            """获取原始索引名（不带租户前缀）"""
            return doc_name

    return GeneratedTenantAwareDoc
