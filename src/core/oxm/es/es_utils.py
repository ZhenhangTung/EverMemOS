from common_utils.datetime_utils import get_now_with_timezone
from typing import Type, List, Optional, TYPE_CHECKING
import os

from core.observation.logger import get_logger

if TYPE_CHECKING:
    from core.oxm.es.doc_base import DocBase

logger = get_logger(__name__)


def generate_index_name(cls: Type['DocBase']) -> str:
    """生成带时间戳的索引名"""
    now = get_now_with_timezone()
    alias = cls.get_index_name()
    return f"{alias}-{now.strftime('%Y%m%d%H%M%S%f')}"


def get_index_ns() -> str:
    """获取索引命名空间"""
    return os.getenv("SELF_ES_INDEX_NS") or ""


def is_abstract_doc_class(doc_class: Type['DocBase']) -> bool:
    """
    检查文档类是否是抽象类

    通过检查 Meta.abstract 属性判断是否是抽象类，
    抽象类不应该被初始化索引。

    Args:
        doc_class: 文档类

    Returns:
        bool: 是否是抽象类
    """
    # 检查 Meta 类的 abstract 属性
    pattern = getattr(doc_class, 'PATTERN', None) or None
    return (not pattern) or "Generated" in doc_class.__name__


class EsIndexInitializer:
    """
    Elasticsearch 索引初始化工具类

    用于批量初始化 ES 文档类对应的索引和别名。
    使用 doc_class._get_connection() 获取连接，支持租户感知。
    """

    def __init__(self):
        self._initialized_classes: List[Type['DocBase']] = []

    async def initialize_indices(
        self, document_classes: Optional[List[Type['DocBase']]] = None
    ) -> None:
        """
        初始化多个文档类的索引

        Args:
            document_classes: 文档类列表
        """
        if not document_classes:
            logger.info("没有需要初始化的文档类")
            return

        try:
            logger.info(
                "正在初始化 Elasticsearch 索引，共 %d 个文档类", len(document_classes)
            )

            for doc_class in document_classes:
                await self.init_document_index(doc_class)

            self._initialized_classes.extend(document_classes)

            logger.info(
                "✅ Elasticsearch 索引初始化成功，处理了 %d 个文档类",
                len(document_classes),
            )

            for doc_class in document_classes:
                logger.info(
                    "📋 初始化索引: class=%s -> index=%s",
                    doc_class.__name__,
                    doc_class.get_index_name(),
                )

        except Exception as e:
            logger.error("❌ Elasticsearch 索引初始化失败: %s", e)
            raise

    async def init_document_index(self, doc_class: Type['DocBase']) -> None:
        """
        初始化单个文档类的索引

        Args:
            doc_class: 文档类
        """
        try:
            # 获取别名名称
            alias = doc_class.get_index_name()

            if not alias:
                logger.info("文档类没有索引别名，跳过初始化 %s", doc_class.__name__)
                return

            # 检查是否是抽象类
            if is_abstract_doc_class(doc_class):
                logger.debug("文档类是抽象类，跳过初始化 %s", doc_class.__name__)
                return

            # 通过文档类获取连接（支持租户感知）
            client = doc_class._get_connection()

            # 检查别名是否存在
            logger.info("正在检查索引别名: %s (文档类: %s)", alias, doc_class.__name__)
            alias_exists = await client.indices.exists(index=alias)

            if not alias_exists:
                # 生成目标索引名
                dst = doc_class.dest()

                # 创建索引
                await doc_class.init(index=dst, using=client)

                # 创建别名
                await client.indices.update_aliases(
                    body={
                        "actions": [
                            {
                                "add": {
                                    "index": dst,
                                    "alias": alias,
                                    "is_write_index": True,
                                }
                            }
                        ]
                    }
                )
                logger.info("✅ 创建索引和别名: %s -> %s", dst, alias)
            else:
                logger.info("📋 索引别名已存在: %s", alias)

        except Exception as e:
            logger.error("❌ 初始化文档类 %s 的索引失败: %s", doc_class.__name__, e)
            raise

    @property
    def initialized_classes(self) -> List[Type['DocBase']]:
        """获取已初始化的文档类列表"""
        return self._initialized_classes


async def initialize_document_indices(
    document_classes: Optional[List[Type['DocBase']]] = None,
) -> None:
    """
    便捷函数：初始化多个文档类的索引

    Args:
        document_classes: 文档类列表
    """
    initializer = EsIndexInitializer()
    await initializer.initialize_indices(document_classes)


async def init_single_document_index(doc_class: Type['DocBase']) -> None:
    """
    便捷函数：初始化单个文档类的索引

    Args:
        doc_class: 文档类
    """
    initializer = EsIndexInitializer()
    await initializer.init_document_index(doc_class)
