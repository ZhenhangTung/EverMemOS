from __future__ import annotations

from typing import Any, List
import logging

from datetime import datetime
import jieba
from typing import Dict, Any

from memory_layer.types import Memory
from biz_layer.mem_memorize import memorize
from memory_layer.memory_manager import MemorizeRequest
from .fetch_mem_service import get_fetch_memory_service
from .retrieve_mem_service import get_retrieve_mem_service
from .dtos.memory_query import (
    FetchMemRequest,
    FetchMemResponse,
    RetrieveMemRequest,
    RetrieveMemResponse,
    Metadata,
)
from core.di import get_bean_by_type
from infra_layer.adapters.out.search.repository.episodic_memory_es_repository import (
    EpisodicMemoryEsRepository,
)
from core.observation.tracing.decorators import trace_logger
from core.nlp.stopwords_utils import filter_stopwords
from common_utils.datetime_utils import from_iso_format
from infra_layer.adapters.out.persistence.repository.memcell_raw_repository import (
    MemCellRawRepository,
)
from infra_layer.adapters.out.persistence.repository.group_user_profile_memory_raw_repository import (
    GroupUserProfileMemoryRawRepository,
)
from infra_layer.adapters.out.search.repository.episodic_memory_milvus_repository import (
    EpisodicMemoryMilvusRepository,
)
from .vectorize_service import get_vectorize_service
from .rerank_service import get_rerank_service

logger = logging.getLogger(__name__)


class MemoryManager:
    """Unified memory interface.

    提供以下主要功能:
    - memorize: 接受原始数据并持久化存储
    - fetch_mem: 通过键检索记忆字段，支持多种记忆类型
    - retrieve_mem: 基于提示词检索方法的记忆读取
    """

    def __init__(self) -> None:
        # 获取记忆服务实例
        self._fetch_service = get_fetch_memory_service()

        logger.info(
            "MemoryManager initialized with fetch_mem_service and retrieve_mem_service"
        )

    # --------- Write path (raw data -> memorize) ---------
    @trace_logger(operation_name="agentic_layer 记忆存储")
    async def memorize(self, memorize_request: MemorizeRequest) -> List[Memory]:
        """Memorize a heterogeneous list of raw items.

        Accepts list[Any], where each item can be one of the typed raw dataclasses
        (ChatRawData / EmailRawData / MemoRawData / LincDocRawData) or any dict-like
        object. Each item is stored as a MemoryCell with a synthetic key.
        """
        memories = await memorize(memorize_request)
        return memories

    # --------- Read path (query -> fetch_mem) ---------
    # 基于kv的记忆读取，包括静态与动态记忆
    @trace_logger(operation_name="agentic_layer 记忆读取")
    async def fetch_mem(self, request: FetchMemRequest) -> FetchMemResponse:
        """获取记忆数据，支持多种记忆类型

        Args:
            request: FetchMemRequest 包含查询参数

        Returns:
            FetchMemResponse 包含查询结果
        """
        logger.debug(
            f"fetch_mem called with request: user_id={request.user_id}, memory_type={request.memory_type}"
        )

        # repository 支持 MemoryType.MULTIPLE 类型，默认就是corememory
        response = await self._fetch_service.find_by_user_id(
            user_id=request.user_id,
            memory_type=request.memory_type,
            version_range=request.version_range,
            limit=request.limit,
        )

        # 注意：response.metadata 已经通过 _get_employee_metadata 包含了完整的员工信息
        # 包括 source, user_id, memory_type, limit, email, phone, full_name
        # 这里不需要再次更新，因为 fetch_mem_service 已经提供了正确的信息

        logger.debug(
            f"fetch_mem returned {len(response.memories)} memories for user {request.user_id}"
        )
        return response

    # 基于retrieve_method的记忆读取，包括静态与动态记忆
    @trace_logger(operation_name="agentic_layer 记忆检索")
    async def retrieve_mem(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> RetrieveMemResponse:
        """检索记忆数据，根据 retrieve_method 分发到不同的检索方法

        Args:
            retrieve_mem_request: RetrieveMemRequest 包含检索参数

        Returns:
            RetrieveMemResponse 包含检索结果
        """
        try:
            # 验证请求参数
            if not retrieve_mem_request:
                raise ValueError("retrieve_mem_request is required for retrieve_mem")

            # 根据 retrieve_method 分发到不同的检索方法
            from .memory_models import RetrieveMethod

            retrieve_method = retrieve_mem_request.retrieve_method

            logger.info(
                f"retrieve_mem 分发请求: user_id={retrieve_mem_request.user_id}, "
                f"retrieve_method={retrieve_method}, query={retrieve_mem_request.query}"
            )

            # 根据检索方法分发
            if retrieve_method == RetrieveMethod.KEYWORD:
                # 关键词检索
                return await self.retrieve_mem_keyword(retrieve_mem_request)
            elif retrieve_method == RetrieveMethod.VECTOR:
                # 向量检索
                return await self.retrieve_mem_vector(retrieve_mem_request)
            elif retrieve_method == RetrieveMethod.HYBRID:
                # 混合检索
                return await self.retrieve_mem_hybrid(retrieve_mem_request)
            else:
                raise ValueError(f"不支持的检索方法: {retrieve_method}")

        except Exception as e:
            logger.error(f"Error in retrieve_mem: {e}", exc_info=True)
            return RetrieveMemResponse(
                memories=[],
                original_data=[],
                scores=[],
                importance_scores=[],
                total_count=0,
                has_more=False,
                query_metadata=Metadata(
                    source="retrieve_mem_service",
                    user_id=(
                        retrieve_mem_request.user_id if retrieve_mem_request else ""
                    ),
                    memory_type="retrieve",
                ),
                metadata=Metadata(
                    source="retrieve_mem_service",
                    user_id=(
                        retrieve_mem_request.user_id if retrieve_mem_request else ""
                    ),
                    memory_type="retrieve",
                ),
            )

    # 关键词检索方法（原来的 retrieve_mem 逻辑）
    @trace_logger(operation_name="agentic_layer 关键词记忆检索")
    async def retrieve_mem_keyword(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> RetrieveMemResponse:
        """基于关键词的记忆检索（原 retrieve_mem 的实现）

        Args:
            retrieve_mem_request: RetrieveMemRequest 包含检索参数

        Returns:
            RetrieveMemResponse 包含检索结果
        """
        try:
            # 从 Request 中获取参数
            if not retrieve_mem_request:
                raise ValueError(
                    "retrieve_mem_request is required for retrieve_mem_keyword"
                )

            search_results = await self.get_keyword_search_results(retrieve_mem_request)

            if not search_results:
                logger.warning(
                    f"关键词检索未找到结果: user_id={retrieve_mem_request.user_id}, query={retrieve_mem_request.query}"
                )
                return RetrieveMemResponse(
                    memories=[],
                    original_data=[],
                    scores=[],
                    importance_scores=[],
                    total_count=0,
                    has_more=False,
                    query_metadata=Metadata(
                        source="episodic_memory_es_repository",
                        user_id=retrieve_mem_request.user_id,
                        memory_type="retrieve_keyword",
                    ),
                    metadata=Metadata(
                        source="episodic_memory_es_repository",
                        user_id=retrieve_mem_request.user_id,
                        memory_type="retrieve_keyword",
                    ),
                )

            # 使用通用的分组处理策略
            memories, scores, importance_scores, original_data, total_count = (
                await self.group_by_groupid_stratagy(search_results, source_type="es")
            )

            logger.debug(
                f"EpisodicMemoryEsRepository multi_search returned {len(memories)} groups for query: {retrieve_mem_request.query}"
            )

            return RetrieveMemResponse(
                memories=memories,
                scores=scores,
                importance_scores=importance_scores,
                original_data=original_data,
                total_count=total_count,
                has_more=False,
                query_metadata=Metadata(
                    source="episodic_memory_es_repository",
                    user_id=retrieve_mem_request.user_id,
                    memory_type="retrieve_keyword",
                ),
                metadata=Metadata(
                    source="episodic_memory_es_repository",
                    user_id=retrieve_mem_request.user_id,
                    memory_type="retrieve_keyword",
                ),
            )

        except Exception as e:
            logger.error(f"Error in retrieve_mem_keyword: {e}", exc_info=True)
            return RetrieveMemResponse(
                memories=[],
                original_data=[],
                scores=[],
                importance_scores=[],
                total_count=0,
                has_more=False,
                query_metadata=Metadata(
                    source="retrieve_mem_keyword_service",
                    user_id=(
                        retrieve_mem_request.user_id if retrieve_mem_request else ""
                    ),
                    memory_type="retrieve_keyword",
                ),
                metadata=Metadata(
                    source="retrieve_mem_keyword_service",
                    user_id=(
                        retrieve_mem_request.user_id if retrieve_mem_request else ""
                    ),
                    memory_type="retrieve_keyword",
                ),
            )

    async def get_keyword_search_results(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> Dict[str, Any]:
        try:
            # 从 Request 中获取参数
            if not retrieve_mem_request:
                raise ValueError("retrieve_mem_request is required for retrieve_mem")

            top_k = retrieve_mem_request.top_k
            query = retrieve_mem_request.query
            user_id = retrieve_mem_request.user_id
            start_time = retrieve_mem_request.start_time
            end_time = retrieve_mem_request.end_time

            # 获取 EpisodicMemoryEsRepository 实例
            es_repo = get_bean_by_type(EpisodicMemoryEsRepository)

            # 将查询字符串转换为搜索词列表
            # 使用jieba进行搜索模式分词，然后过滤停用词
            if query:
                raw_words = list(jieba.cut_for_search(query))
                query_words = filter_stopwords(raw_words, min_length=2)
            else:
                query_words = []

            logger.debug(f"query_words: {query_words}")

            # 构建时间范围过滤条件，处理 None 值
            date_range = {}
            if start_time is not None:
                date_range["gte"] = start_time
            if end_time is not None:
                date_range["lte"] = end_time

            # 调用 multi_search 方法
            search_results = await es_repo.multi_search(
                query=query_words,
                user_id=user_id,
                size=top_k,
                from_=0,
                date_range=date_range,
            )
            return search_results
        except Exception as e:
            logger.error(f"Error in get_keyword_search_results: {e}")
            return {}

    # 基于向量的记忆检索
    @trace_logger(operation_name="agentic_layer 向量记忆检索")
    async def retrieve_mem_vector(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> RetrieveMemResponse:
        """基于向量相似性的记忆检索

        Args:
            request: Request 包含检索参数，包括 query 和 retrieve_mem_request

        Returns:
            RetrieveMemResponse 包含检索结果
        """
        try:
            # 从 Request 中获取参数
            logger.debug(
                f"retrieve_mem_vector called with retrieve_mem_request: {retrieve_mem_request}"
            )
            if not retrieve_mem_request:
                raise ValueError(
                    "retrieve_mem_request is required for retrieve_mem_vector"
                )

            query = retrieve_mem_request.query
            if not query:
                raise ValueError("query is required for retrieve_mem_vector")

            user_id = retrieve_mem_request.user_id
            top_k = retrieve_mem_request.top_k
            start_time = retrieve_mem_request.start_time
            end_time = retrieve_mem_request.end_time

            logger.debug(
                f"retrieve_mem_vector called with query: {query}, user_id: {user_id}, top_k: {top_k}"
            )

            # 获取向量化服务
            vectorize_service = get_vectorize_service()

            # 将查询文本转换为向量
            logger.debug(f"开始向量化查询文本: {query}")
            query_vector = await vectorize_service.get_embedding(query)
            query_vector_list = query_vector.tolist()  # 转换为列表格式
            logger.debug(f"查询文本向量化完成，向量维度: {len(query_vector_list)}")

            # 获取 EpisodicMemoryMilvusRepository 实例
            milvus_repo = get_bean_by_type(EpisodicMemoryMilvusRepository)

            # 处理时间范围过滤条件
            start_time_dt = None
            end_time_dt = None

            if start_time is not None:
                if isinstance(start_time, str):
                    # 如果是日期格式 "2024-01-01"，转换为当天的开始时间
                    start_time_dt = datetime.strptime(start_time, "%Y-%m-%d")
                else:
                    start_time_dt = start_time

            if end_time is not None:
                if isinstance(end_time, str):
                    # 如果是日期格式 "2024-12-31"，转换为当天的结束时间
                    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d")
                    # 设置为当天的23:59:59，确保包含整天
                    end_time_dt = end_time_dt.replace(hour=23, minute=59, second=59)
                else:
                    end_time_dt = end_time

            # 调用 Milvus 的向量搜索
            search_results = await milvus_repo.vector_search(
                query_vector=query_vector_list,
                user_id=user_id,
                start_time=start_time_dt,
                end_time=end_time_dt,
                limit=top_k,
                score_threshold=0.0,
            )

            logger.debug(f"Milvus向量搜索返回 {len(search_results)} 条结果")

            # 使用通用的分组处理策略
            memories, scores, importance_scores, original_data, total_count = (
                await self.group_by_groupid_stratagy(
                    search_results, source_type="milvus"
                )
            )

            logger.debug(
                f"EpisodicMemoryMilvusRepository vector_search returned {len(memories)} groups for query: {query}"
            )

            return RetrieveMemResponse(
                memories=memories,
                scores=scores,
                importance_scores=importance_scores,
                original_data=original_data,
                total_count=total_count,
                has_more=False,
                query_metadata=Metadata(
                    source="episodic_memory_milvus_repository",
                    user_id=user_id,
                    memory_type="retrieve_vector",
                ),
                metadata=Metadata(
                    source="episodic_memory_milvus_repository",
                    user_id=user_id,
                    memory_type="retrieve_vector",
                ),
            )

        except Exception as e:
            logger.error(f"Error in retrieve_mem_vector: {e}")
            return RetrieveMemResponse(
                memories=[],
                original_data=[],
                scores=[],
                importance_scores=[],
                total_count=0,
                has_more=False,
                query_metadata=Metadata(
                    source="retrieve_mem_vector_service",
                    user_id=user_id if 'user_id' in locals() else "",
                    memory_type="retrieve_vector",
                ),
                metadata=Metadata(
                    source="retrieve_mem_vector_service",
                    user_id=user_id if 'user_id' in locals() else "",
                    memory_type="retrieve_vector",
                ),
            )

    async def get_vector_search_results(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> Dict[str, Any]:
        try:
            # 从 Request 中获取参数
            logger.debug(
                f"get_vector_search_results called with retrieve_mem_request: {retrieve_mem_request}"
            )
            if not retrieve_mem_request:
                raise ValueError(
                    "retrieve_mem_request is required for get_vector_search_results"
                )
            query = retrieve_mem_request.query
            if not query:
                raise ValueError("query is required for retrieve_mem_vector")

            user_id = retrieve_mem_request.user_id
            top_k = retrieve_mem_request.top_k
            start_time = retrieve_mem_request.start_time
            end_time = retrieve_mem_request.end_time

            logger.debug(
                f"retrieve_mem_vector called with query: {query}, user_id: {user_id}, top_k: {top_k}"
            )

            # 获取向量化服务
            vectorize_service = get_vectorize_service()

            # 将查询文本转换为向量
            logger.debug(f"开始向量化查询文本: {query}")
            query_vector = await vectorize_service.get_embedding(query)
            query_vector_list = query_vector.tolist()  # 转换为列表格式
            logger.debug(f"查询文本向量化完成，向量维度: {len(query_vector_list)}")

            # 获取 EpisodicMemoryMilvusRepository 实例
            milvus_repo = get_bean_by_type(EpisodicMemoryMilvusRepository)

            # 处理时间范围过滤条件
            start_time_dt = None
            end_time_dt = None

            if start_time is not None:
                if isinstance(start_time, str):
                    # 如果是日期格式 "2024-01-01"，转换为当天的开始时间
                    start_time_dt = datetime.strptime(start_time, "%Y-%m-%d")
                else:
                    start_time_dt = start_time

            if end_time is not None:
                if isinstance(end_time, str):
                    # 如果是日期格式 "2024-12-31"，转换为当天的结束时间
                    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d")
                    # 设置为当天的23:59:59，确保包含整天
                    end_time_dt = end_time_dt.replace(hour=23, minute=59, second=59)
                else:
                    end_time_dt = end_time

            # 调用 Milvus 的向量搜索
            search_results = await milvus_repo.vector_search(
                query_vector=query_vector_list,
                user_id=user_id,
                start_time=start_time_dt,
                end_time=end_time_dt,
                limit=top_k,
                score_threshold=0.0,
            )
            return search_results
        except Exception as e:
            logger.error(f"Error in get_vector_search_results: {e}")
            return {}

    # 混合记忆检索
    @trace_logger(operation_name="agentic_layer 混合记忆检索")
    async def retrieve_mem_hybrid(
        self, retrieve_mem_request: 'RetrieveMemRequest'
    ) -> RetrieveMemResponse:
        """基于关键词和向量的混合记忆检索

        Args:
            retrieve_mem_request: RetrieveMemRequest 包含检索参数

        Returns:
            RetrieveMemResponse 包含混合检索结果
        """
        try:
            logger.debug(
                f"retrieve_mem_hybrid called with retrieve_mem_request: {retrieve_mem_request}"
            )
            if not retrieve_mem_request:
                raise ValueError(
                    "retrieve_mem_request is required for retrieve_mem_hybrid"
                )

            query = retrieve_mem_request.query
            if not query:
                raise ValueError("query is required for retrieve_mem_hybrid")

            user_id = retrieve_mem_request.user_id
            top_k = retrieve_mem_request.top_k
            start_time = retrieve_mem_request.start_time
            end_time = retrieve_mem_request.end_time

            logger.debug(
                f"retrieve_mem_hybrid called with query: {query}, user_id: {user_id}, top_k: {top_k}"
            )

            # 创建关键词检索请求
            keyword_request = RetrieveMemRequest(
                user_id=user_id,
                memory_types=retrieve_mem_request.memory_types,
                top_k=top_k,
                filters=retrieve_mem_request.filters,
                include_metadata=retrieve_mem_request.include_metadata,
                start_time=start_time,
                end_time=end_time,
                query=query,
            )

            # 创建向量检索请求
            vector_request = RetrieveMemRequest(
                user_id=user_id,
                memory_types=retrieve_mem_request.memory_types,
                top_k=top_k,
                filters=retrieve_mem_request.filters,
                include_metadata=retrieve_mem_request.include_metadata,
                start_time=start_time,
                end_time=end_time,
                query=query,
            )

            # 并行执行两种检索，获取原始搜索结果
            keyword_search_results = await self.get_keyword_search_results(
                keyword_request
            )
            vector_search_results = await self.get_vector_search_results(vector_request)

            logger.debug(f"关键词检索返回 {len(keyword_search_results)} 条原始结果")
            logger.debug(f"向量检索返回 {len(vector_search_results)} 条原始结果")

            # 合并原始搜索结果并进行rerank
            hybrid_result = await self._merge_and_rerank_search_results(
                keyword_search_results, vector_search_results, top_k, user_id, query
            )

            logger.debug(f"混合检索最终返回 {len(hybrid_result.memories)} 个群组")

            return hybrid_result

        except Exception as e:
            logger.error(f"Error in retrieve_mem_hybrid: {e}")
            return RetrieveMemResponse(
                memories=[],
                original_data=[],
                scores=[],
                importance_scores=[],
                total_count=0,
                has_more=False,
                query_metadata=Metadata(
                    source="retrieve_mem_hybrid_service",
                    user_id=user_id if 'user_id' in locals() else "",
                    memory_type="retrieve_hybrid",
                ),
                metadata=Metadata(
                    source="retrieve_mem_hybrid_service",
                    user_id=user_id if 'user_id' in locals() else "",
                    memory_type="retrieve_hybrid",
                ),
            )

    def _extract_score_from_hit(self, hit: Dict[str, Any]) -> float:
        """从hit中提取得分

        Args:
            hit: 搜索结果hit

        Returns:
            得分
        """
        if '_score' in hit:
            return hit['_score']
        elif 'score' in hit:
            return hit['score']
        return 1.0

    async def _merge_and_rerank_search_results(
        self,
        keyword_search_results: List[Dict[str, Any]],
        vector_search_results: List[Dict[str, Any]],
        top_k: int,
        user_id: str,
        query: str,
    ) -> RetrieveMemResponse:
        """合并关键词和向量检索的原始搜索结果，并进行重新排序

        Args:
            keyword_search_results: 关键词检索的原始搜索结果
            vector_search_results: 向量检索的原始搜索结果
            top_k: 返回的最大群组数量
            user_id: 用户ID
            query: 查询文本

        Returns:
            RetrieveMemResponse: 合并和重新排序后的结果
        """
        # 提取搜索结果
        keyword_hits = keyword_search_results
        vector_hits = vector_search_results

        logger.debug(f"关键词检索原始结果: {len(keyword_hits)} 条")
        logger.debug(f"向量检索原始结果: {len(vector_hits)} 条")

        # 合并所有搜索结果并标记来源
        all_hits = []

        # 添加关键词检索结果，标记来源
        for hit in keyword_hits:
            hit_copy = hit.copy()
            hit_copy['_search_source'] = 'keyword'
            all_hits.append(hit_copy)

        # 添加向量检索结果，标记来源
        for hit in vector_hits:
            hit_copy = hit.copy()
            hit_copy['_search_source'] = 'vector'
            all_hits.append(hit_copy)

        logger.debug(f"合并后总结果数: {len(all_hits)} 条")

        # 使用rerank服务进行重排序
        try:
            rerank_service = get_rerank_service()
            reranked_hits = await rerank_service._rerank_all_hits(
                query, all_hits, top_k
            )

            logger.debug(f"使用rerank服务后取top_k结果数: {len(reranked_hits)} 条")

        except Exception as e:
            logger.error(f"使用rerank服务失败，回退到简单排序: {e}")
            # 如果rerank失败，回退到简单的得分排序
            reranked_hits = sorted(
                all_hits, key=self._extract_score_from_hit, reverse=True
            )[:top_k]

        # 对rerank后的结果进行分组处理
        memories, scores, importance_scores, original_data, total_count = (
            await self.group_by_groupid_stratagy(reranked_hits, source_type="hybrid")
        )

        # 构建最终结果
        return RetrieveMemResponse(
            memories=memories,
            scores=scores,
            importance_scores=importance_scores,
            original_data=original_data,
            total_count=total_count,
            has_more=False,
            query_metadata=Metadata(
                source="hybrid_retrieval",
                user_id=user_id,
                memory_type="retrieve_hybrid",
            ),
            metadata=Metadata(
                source="hybrid_retrieval",
                user_id=user_id,
                memory_type="retrieve_hybrid",
            ),
        )

    async def group_by_groupid_stratagy(
        self, search_results: List[Dict[str, Any]], source_type: str = "milvus"
    ) -> tuple:
        """通用的搜索结果分组处理策略

        Args:
            search_results: 搜索结果列表
            source_type: 数据源类型，支持 "es" 或 "milvus"

        Returns:
            tuple: (memories, scores, importance_scores, original_data, total_count)
        """
        memories_by_group = (
            {}
        )  # {group_id: {'memories': [Memory], 'scores': [float], 'importance_evidence': dict}}
        original_data_by_group = {}

        for hit in search_results:
            # 根据数据源类型提取数据
            if source_type == "es":
                # ES 搜索结果格式
                source = hit.get('_source', {})
                score = hit.get('_score', 1.0)
                user_id = source.get('user_id', '')
                group_id = source.get('group_id', '')
                timestamp_raw = source.get('timestamp', '')
                episode = source.get('episode', '')
                memcell_event_id_list = source.get('memcell_event_id_list', [])
                subject = source.get('subject', '')
                summary = source.get('summary', '')
                participants = source.get('participants', [])
                hit_id = source.get('event_id', '')
                search_source = hit.get('_search_source', 'keyword')  # 默认为关键词检索
            elif source_type == "hybrid":
                # 混合检索结果格式，需要根据_search_source字段判断
                search_source = hit.get('_search_source', 'unknown')
                if search_source == 'keyword':
                    # 关键词检索结果格式
                    source = hit.get('_source', {})
                    score = hit.get('_score', 1.0)
                    user_id = source.get('user_id', '')
                    group_id = source.get('group_id', '')
                    timestamp_raw = source.get('timestamp', '')
                    episode = source.get('episode', '')
                    memcell_event_id_list = source.get('memcell_event_id_list', [])
                    subject = source.get('subject', '')
                    summary = source.get('summary', '')
                    participants = source.get('participants', [])
                    hit_id = source.get('event_id', '')
                else:
                    # 向量检索结果格式
                    hit_id = hit.get('id', '')
                    score = hit.get('score', 1.0)
                    user_id = hit.get('user_id', '')
                    group_id = hit.get('group_id', '')
                    timestamp_raw = hit.get('timestamp')
                    episode = hit.get('episode', '')
                    metadata = hit.get('metadata', {})
                    memcell_event_id_list = metadata.get('memcell_event_id_list', [])
                    subject = metadata.get('subject', '')
                    summary = metadata.get('summary', '')
                    participants = metadata.get('participants', [])
            else:
                # Milvus 搜索结果格式
                hit_id = hit.get('id', '')
                score = hit.get('score', 1.0)
                user_id = hit.get('user_id', '')
                group_id = hit.get('group_id', '')
                timestamp_raw = hit.get('timestamp')
                episode = hit.get('episode', '')
                metadata = hit.get('metadata', {})
                memcell_event_id_list = metadata.get('memcell_event_id_list', [])
                subject = metadata.get('subject', '')
                summary = metadata.get('summary', '')
                participants = metadata.get('participants', [])
                search_source = 'vector'  # 默认为向量检索

            # 处理时间戳
            if timestamp_raw:
                if isinstance(timestamp_raw, datetime):
                    timestamp = timestamp_raw.replace(tzinfo=None)
                elif isinstance(timestamp_raw, (int, float)):
                    try:
                        timestamp = datetime.fromtimestamp(timestamp_raw)
                    except Exception as e:
                        logger.warning(
                            f"timestamp为数字但转换失败: {timestamp_raw}, error: {e}"
                        )
                        timestamp = datetime.now().replace(tzinfo=None)
                elif isinstance(timestamp_raw, str):
                    try:
                        timestamp = from_iso_format(timestamp_raw).replace(tzinfo=None)
                    except Exception as e:
                        logger.warning(
                            f"timestamp格式转换失败: {timestamp_raw}, error: {e}"
                        )
                        timestamp = datetime.now().replace(tzinfo=None)
                else:
                    logger.warning(
                        f"未知类型的timestamp_raw: {type(timestamp_raw)}, 使用当前时间"
                    )
                    timestamp = datetime.now().replace(tzinfo=None)
            else:
                timestamp = datetime.now().replace(tzinfo=None)

            # 获取 memcell 数据
            memcells = []
            if memcell_event_id_list:
                memcell_repo = get_bean_by_type(MemCellRawRepository)
                for event_id in memcell_event_id_list:
                    memcell = await memcell_repo.get_by_event_id(event_id)
                    if memcell:
                        memcells.append(memcell)
                    else:
                        logger.warning(f"未找到 memcell: event_id={event_id}")
                        continue

            # 为每个 memcell 添加原始数据
            for memcell in memcells:
                if group_id not in original_data_by_group:
                    original_data_by_group[group_id] = []
                original_data_by_group[group_id].append(memcell.original_data)

            # 创建 Memory 对象
            memory = Memory(
                memory_type="episode_summary",  # 情景记忆类型
                user_id=user_id,
                timestamp=timestamp,
                ori_event_id_list=[hit_id],
                subject=subject,
                summary=summary,
                episode=episode,
                group_id=group_id,
                participants=participants,
                memcell_event_id_list=memcell_event_id_list,
            )

            # 添加搜索来源信息到 extend 字段
            if not hasattr(memory, 'extend') or memory.extend is None:
                memory.extend = {}
            memory.extend['_search_source'] = search_source

            # 读取group_user_profile_memory获取group_importance_evidence
            group_importance_evidence = None
            if user_id and group_id:
                try:
                    group_user_profile_repo = get_bean_by_type(
                        GroupUserProfileMemoryRawRepository
                    )
                    group_user_profile = (
                        await group_user_profile_repo.get_by_user_group(
                            user_id, group_id
                        )
                    )

                    if (
                        group_user_profile
                        and hasattr(group_user_profile, 'group_importance_evidence')
                        and group_user_profile.group_importance_evidence
                    ):
                        group_importance_evidence = (
                            group_user_profile.group_importance_evidence
                        )
                        # 将group_importance_evidence添加到memory的extend字段中
                        if not hasattr(memory, 'extend') or memory.extend is None:
                            memory.extend = {}
                        memory.extend['group_importance_evidence'] = (
                            group_importance_evidence
                        )
                        logger.debug(
                            f"为memory添加group_importance_evidence: user_id={user_id}, group_id={group_id}"
                        )
                    else:
                        logger.debug(
                            f"未找到group_importance_evidence: user_id={user_id}, group_id={group_id}"
                        )
                except Exception as e:
                    logger.warning(
                        f"读取group_user_profile_memory失败: user_id={user_id}, group_id={group_id}, error={e}"
                    )

            # 按group_id分组
            if group_id not in memories_by_group:
                memories_by_group[group_id] = {
                    'memories': [],
                    'scores': [],
                    'importance_evidence': group_importance_evidence,
                }

            memories_by_group[group_id]['memories'].append(memory)
            memories_by_group[group_id]['scores'].append(score)  # 保存原始得分
            # 更新group_importance_evidence（如果当前memory有更新的证据）
            if group_importance_evidence:
                memories_by_group[group_id][
                    'importance_evidence'
                ] = group_importance_evidence

        def calculate_importance_score(importance_evidence):
            """计算群组重要性得分"""
            if not importance_evidence or not isinstance(importance_evidence, dict):
                return 0.0

            evidence_list = importance_evidence.get('evidence_list', [])
            if not evidence_list:
                return 0.0

            total_speak_count = 0
            total_refer_count = 0
            total_conversation_count = 0

            for evidence in evidence_list:
                if isinstance(evidence, dict):
                    total_speak_count += evidence.get('speak_count', 0)
                    total_refer_count += evidence.get('refer_count', 0)
                    total_conversation_count += evidence.get('conversation_count', 0)

            if total_conversation_count == 0:
                return 0.0

            return (total_speak_count + total_refer_count) / total_conversation_count

        # 为每个group内的memories按时间戳排序，并计算重要性得分
        group_scores = []
        for group_id, group_data in memories_by_group.items():
            # 按时间戳排序memories
            group_data['memories'].sort(
                key=lambda m: m.timestamp if m.timestamp else ''
            )

            # 计算重要性得分
            importance_score = calculate_importance_score(
                group_data['importance_evidence']
            )
            group_scores.append((group_id, importance_score))

        # 按重要性得分排序groups
        group_scores.sort(key=lambda x: x[1], reverse=True)

        # 构建最终结果
        memories = []
        scores = []
        importance_scores = []
        original_data = []
        for group_id, importance_score in group_scores:
            group_data = memories_by_group[group_id]
            group_memories = group_data['memories']
            group_scores_list = group_data['scores']
            group_original_data = original_data_by_group.get(group_id, [])
            memories.append({group_id: group_memories})
            # scores结构与memories保持一致：List[Dict[str, List[float]]]
            scores.append({group_id: group_scores_list})
            # original_data结构与memories保持一致：List[Dict[str, List[Dict[str, Any]]]]
            original_data.append({group_id: group_original_data})
            importance_scores.append(importance_score)

        total_count = sum(
            len(group_data['memories']) for group_data in memories_by_group.values()
        )
        return memories, scores, importance_scores, original_data, total_count
