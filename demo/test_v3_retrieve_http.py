"""V3 API HTTP 记忆检索测试

通过HTTP接口测试V3 API的所有检索功能：
1. Episode 检索（中文查询）
2. Event Log 检索（英文查询）
3. Semantic Memory 检索（中文查询）
4. 用户过滤测试
5. Memory Scope 测试（个人/群组）
"""
import asyncio
import httpx
from typing import Dict, List, Any


# V3 API 基础URL
BASE_URL = "http://localhost:8001"
RETRIEVE_URL = f"{BASE_URL}/api/v3/agentic/retrieve_lightweight"
RETRIEVE_AGENTIC_URL = f"{BASE_URL}/api/v3/agentic/retrieve_agentic"


async def call_retrieve_api(
    query: str,
    user_id: str = "user_001",
    top_k: int = 3,
    data_source: str = "memcell",
    retrieval_mode: str = "embedding",
    memory_scope: str = "all",
) -> Dict[str, Any]:
    """调用V3 API的检索接口"""
    payload = {
        "query": query,
        "user_id": user_id,
        "top_k": top_k,
        "data_source": data_source,
        "retrieval_mode": retrieval_mode,
        "memory_scope": memory_scope,
    }
    
    try:
        # 使用verify=False来跳过SSL证书验证（仅用于本地开发环境）
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(RETRIEVE_URL, json=payload)
            response.raise_for_status()  # 检查HTTP状态码
            return response.json()
    except httpx.HTTPStatusError as e:
        # HTTP错误（4xx, 5xx）
        return {
            "status": "error",
            "message": f"HTTP {e.response.status_code}: {e.response.text}",
            "error_type": "HTTPStatusError"
        }
    except Exception as e:
        # 其他错误
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }


async def call_retrieve_agentic_api(
    query: str,
    user_id: str = "user_001",
    group_id: str = None,
    top_k: int = 3,
    time_range_days: int = 365,
    llm_config: Dict[str, str] = None,
) -> Dict[str, Any]:
    """调用V3 API的 Agentic 检索接口
    
    Args:
        query: 查询文本
        user_id: 用户ID
        group_id: 群组ID
        top_k: 返回结果数量
        time_range_days: 时间范围（天）
        llm_config: LLM 配置（可选）
            - api_key: API Key
            - base_url: API 地址
            - model: 模型名称
    
    Returns:
        检索结果字典
    """
    payload = {
        "query": query,
        "user_id": user_id,
        "top_k": top_k,
        "time_range_days": time_range_days,
    }
    
    if group_id:
        payload["group_id"] = group_id
    
    if llm_config:
        payload["llm_config"] = llm_config
    
    try:
        # Agentic 检索耗时较长，设置60秒超时
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            response = await client.post(RETRIEVE_AGENTIC_URL, json=payload)
            response.raise_for_status()  # 检查HTTP状态码
            return response.json()
    except httpx.HTTPStatusError as e:
        # HTTP错误（4xx, 5xx）
        return {
            "status": "error",
            "message": f"HTTP {e.response.status_code}: {e.response.text}",
            "error_type": "HTTPStatusError"
        }
    except httpx.TimeoutException:
        # 超时错误
        return {
            "status": "error",
            "message": "请求超时（超过60秒）",
            "error_type": "TimeoutException"
        }
    except Exception as e:
        # 其他错误
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }


def print_results(query: str, mode: str, response: Dict[str, Any], scope: str = "all"):
    """打印检索结果"""
    if response.get("status") == "ok":
        result = response.get("result", {})
        memories = result.get("memories", [])
        metadata = result.get("metadata", {})
        
        status = "✅" if len(memories) > 0 else "⚠️"
        scope_text = f" [{scope}]" if scope != "all" else ""
        print(f"{status} '{query}' ({mode}){scope_text}: {len(memories)} 条, "
              f"耗时: {metadata.get('total_latency_ms', 0):.2f}ms")
        
        for i, mem in enumerate(memories[:3], 1):  # 只显示前3条
            score = mem.get('score', 0)
            content = (mem.get('episode') or mem.get('content') or 
                      mem.get('atomic_fact', ''))[:80]
            event_id = mem.get('event_id', 'N/A')
            print(f"  [{i}] 分数: {score:.4f} | event_id: {event_id}")
            print(f"      {content}...")
    else:
        error_msg = response.get("message", "未知错误")
        error_type = response.get("error_type", "")
        # 打印完整的错误信息
        if error_type:
            print(f"❌ '{query}' ({mode}): [{error_type}] {error_msg}")
        else:
            print(f"❌ '{query}' ({mode}): {error_msg}")
        
        # 如果有详细信息，也打印出来
        if "detail" in response:
            print(f"   详细: {response['detail']}")
        elif response.get("status") == "error" and "error_type" not in ["ConnectError"]:
            # 对于非连接错误，显示完整响应
            print(f"   完整响应: {response}")


def print_agentic_results(query: str, response: Dict[str, Any]):
    """打印 Agentic 检索结果（带详细元数据）"""
    if response.get("status") == "ok":
        result = response.get("result", {})
        memories = result.get("memories", [])
        metadata = result.get("metadata", {})
        
        status = "✅" if len(memories) > 0 else "⚠️"
        print(f"{status} '{query}' (Agentic): {len(memories)} 条, "
              f"耗时: {metadata.get('total_latency_ms', 0):.2f}ms")
        
        # 打印 Agentic 特有的元数据
        is_multi_round = metadata.get("is_multi_round", False)
        is_sufficient = metadata.get("is_sufficient")
        
        print(f"  📊 多轮检索: {'是' if is_multi_round else '否'}")
        print(f"  📊 Round 1 结果数: {metadata.get('round1_count', 0)}")
        
        if is_sufficient is not None:
            print(f"  📊 充分性判断: {'充分' if is_sufficient else '不充分'}")
            
            if not is_sufficient:
                reasoning = metadata.get("reasoning", "")
                refined_queries = metadata.get("refined_queries", [])
                
                if reasoning:
                    print(f"  💡 原因: {reasoning}")
                
                if refined_queries:
                    print(f"  🔍 改进查询: {refined_queries}")
                
                print(f"  📊 Round 2 结果数: {metadata.get('round2_count', 0)}")
        
        # 显示前3条记忆
        for i, mem in enumerate(memories[:3], 1):
            score = mem.get('score', 0)
            content = (mem.get('episode') or mem.get('content') or 
                      mem.get('atomic_fact', ''))[:80]
            event_id = mem.get('event_id', 'N/A')
            print(f"  [{i}] 分数: {score:.4f} | event_id: {event_id}")
            print(f"      {content}...")
    else:
        error_msg = response.get("message", "未知错误")
        error_type = response.get("error_type", "")
        
        if error_type:
            print(f"❌ '{query}' (Agentic): [{error_type}] {error_msg}")
        else:
            print(f"❌ '{query}' (Agentic): {error_msg}")
        
        if "detail" in response:
            print(f"   详细: {response['detail']}")
        elif response.get("status") == "error" and error_type not in ["ConnectError", "TimeoutException"]:
            print(f"   完整响应: {response}")


async def test_episode_retrieval():
    """测试 Episode 检索（中文查询）"""
    print("\n" + "=" * 100)
    print("🔍 测试1: Episode 检索（中文查询）")
    print("=" * 100)
    
    test_cases = [
        ("北京旅游", "embedding"),
        ("北京旅游", "bm25"),
        ("北京旅游", "rrf"),
    ]
    
    for query, mode in test_cases:
        print(f"\n【查询: '{query}' | 模式: {mode}】")
        try:
            response = await call_retrieve_api(
                query=query,
                data_source="memcell",
                retrieval_mode=mode,
            )
            print_results(query, mode, response)
        except httpx.ConnectError:
            print(f"❌ 连接失败: 无法连接到 {BASE_URL}")
            print(f"   请确保 V3 API 服务已启动: uv run python src/bootstrap.py start_server.py")
            return False
        except Exception as e:
            print(f"❌ 检索失败: {e}")
    
    return True


async def test_eventlog_retrieval():
    """测试 Event Log 检索（英文查询）"""
    print("\n" + "=" * 100)
    print("🔍 测试2: Event Log 检索（英文查询）")
    print("=" * 100)
    
    test_cases = [
        ("Beijing travel recommendations", "embedding"),
        ("Forbidden City and Temple of Heaven", "bm25"),
        ("tourist attractions food", "rrf"),
    ]
    
    for query, mode in test_cases:
        print(f"\n【Query: '{query}' | Mode: {mode}】")
        try:
            response = await call_retrieve_api(
                query=query,
                data_source="event_log",
                retrieval_mode=mode,
            )
            print_results(query, mode, response)
        except Exception as e:
            print(f"❌ 检索失败: {e}")


async def test_semantic_memory_retrieval():
    """测试 Semantic Memory 检索（中文查询）"""
    print("\n" + "=" * 100)
    print("🔍 测试3: Semantic Memory 检索（中文查询）")
    print("=" * 100)
    
    test_cases = [
        ("用户喜好", "embedding"),
        ("用户喜好", "bm25"),
        ("用户喜好", "rrf"),
    ]
    
    for query, mode in test_cases:
        print(f"\n【查询: '{query}' | 模式: {mode}】")
        try:
            response = await call_retrieve_api(
                query=query,
                data_source="semantic_memory",
                retrieval_mode=mode,
            )
            print_results(query, mode, response)
        except Exception as e:
            print(f"❌ 检索失败: {e}")


async def test_user_filtering():
    """测试用户过滤"""
    print("\n" + "=" * 100)
    print("🔍 测试4: 用户过滤（Episode检索）")
    print("=" * 100)
    
    test_cases = [
        ("user_001", "向量"),
        ("robot_001", "向量"),
    ]
    
    for user_id, mode_name in test_cases:
        print(f"\n【用户: {user_id} | 模式: {mode_name}】")
        try:
            response = await call_retrieve_api(
                query="旅游",
                user_id=user_id,
                data_source="memcell",
                retrieval_mode="embedding",
                top_k=5,
            )
            print_results(f"{user_id}的记忆", mode_name, response)
        except Exception as e:
            print(f"❌ 检索失败: {e}")


async def test_memory_scope():
    """测试 Memory Scope（个人/群组）"""
    print("\n" + "=" * 100)
    print("🔍 测试5: Memory Scope 过滤")
    print("=" * 100)
    
    # Episode测试
    print("\n【Episode - 不同Scope】")
    for scope in ["all", "personal", "group"]:
        try:
            response = await call_retrieve_api(
                query="北京",
                data_source="memcell",
                retrieval_mode="embedding",
                memory_scope=scope,
                top_k=3,
            )
            print_results("北京", "向量", response, scope)
        except Exception as e:
            print(f"❌ Episode-{scope} 检索失败: {e}")
    
    # Event Log测试
    print("\n【Event Log - 不同Scope】")
    for scope in ["all", "personal", "group"]:
        try:
            response = await call_retrieve_api(
                query="travel",
                data_source="event_log",
                retrieval_mode="embedding",
                memory_scope=scope,
                top_k=3,
            )
            print_results("travel", "向量", response, scope)
        except Exception as e:
            print(f"❌ EventLog-{scope} 检索失败: {e}")
    
    # Semantic Memory测试
    print("\n【Semantic Memory - 不同Scope】")
    for scope in ["all", "personal", "group"]:
        try:
            response = await call_retrieve_api(
                query="用户",
                data_source="semantic_memory",
                retrieval_mode="embedding",
                memory_scope=scope,
                top_k=3,
            )
            print_results("用户", "向量", response, scope)
        except Exception as e:
            print(f"❌ SemanticMemory-{scope} 检索失败: {e}")


async def test_agentic_retrieval():
    """测试 Agentic 检索（LLM 引导的多轮检索）"""
    print("\n" + "=" * 100)
    print("🔍 测试6: Agentic 检索（LLM 引导的多轮检索）")
    print("=" * 100)
    print("⚠️  注意：Agentic 检索需要配置 LLM API Key（OPENROUTER_API_KEY 或 OPENAI_API_KEY）")
    print("⚠️  如果未配置，测试将跳过")
    print()
    
    # 测试用例：简单查询和复杂查询
    test_cases = [
        {
            "query": "北京旅游",
            "description": "简单查询（可能充分）",
        },
        {
            "query": "用户喜欢吃什么？平时的饮食习惯是什么？",
            "description": "复杂查询（可能触发多轮检索）",
        },
        {
            "query": "用户的性格特点和兴趣爱好",
            "description": "多维度查询（可能触发多轮检索）",
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\n【测试 {i}: {description}】")
        print(f"查询: {query}")
        print()
        
        try:
            response = await call_retrieve_agentic_api(
                query=query,
                top_k=5,
            )
            print_agentic_results(query, response)
            
            # 如果是 API Key 错误，跳过后续测试
            if response.get("status") == "error":
                error_msg = response.get("message", "")
                if "API Key" in error_msg or "api_key" in error_msg.lower():
                    print("\n⚠️  检测到 API Key 未配置，跳过后续 Agentic 测试")
                    print("提示：请在 .env 文件中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY")
                    break
        
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


async def test_comprehensive():
    """综合测试：所有数据源 × 所有模式 × 所有Scope"""
    print("\n" + "=" * 100)
    print("🔍 测试7: 综合测试矩阵")
    print("=" * 100)
    
    test_matrix = {
        "memcell": {
            "query": "北京旅游",
            "modes": ["embedding", "bm25", "rrf"],
            "scopes": ["all", "personal", "group"],
        },
        "event_log": {
            "query": "Beijing travel",
            "modes": ["embedding", "bm25", "rrf"],
            "scopes": ["all", "personal", "group"],
        },
        "semantic_memory": {
            "query": "饮食习惯",
            "modes": ["embedding", "bm25", "rrf"],
            "scopes": ["all", "personal", "group"],
        },
    }
    
    total_tests = 0
    passed_tests = 0
    
    for data_source, config in test_matrix.items():
        print(f"\n【{data_source.upper()} 数据源】")
        
        for mode in config["modes"]:
            for scope in config["scopes"]:
                total_tests += 1
                test_name = f"{data_source}-{mode}-{scope}"
                
                try:
                    response = await call_retrieve_api(
                        query=config["query"],
                        data_source=data_source,
                        retrieval_mode=mode,
                        memory_scope=scope,
                        top_k=2,
                    )
                    
                    if response.get("status") == "ok":
                        result = response.get("result", {})
                        memories = result.get("memories", [])
                        if len(memories) > 0:
                            passed_tests += 1
                            print(f"  ✅ {test_name}: {len(memories)} 条")
                        else:
                            print(f"  ⚠️  {test_name}: 0 条")
                    else:
                        print(f"  ❌ {test_name}: {response.get('message', '失败')}")
                
                except Exception as e:
                    print(f"  ❌ {test_name}: 异常 - {e}")
    
    print(f"\n📊 综合测试结果: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")


async def main():
    """主测试流程"""
    print("\n" + "=" * 100)
    print("🧪 V3 API HTTP 记忆检索测试")
    print("=" * 100)
    print(f"目标服务: {BASE_URL}")
    print(f"检索接口: {RETRIEVE_URL}")
    print("=" * 100)
    
    # 测试1: Episode检索
    success = await test_episode_retrieval()
    if not success:
        print("\n⚠️  服务未启动，测试终止")
        return
    
    # 测试2: Event Log检索
    await test_eventlog_retrieval()
    
    # 测试3: Semantic Memory检索
    await test_semantic_memory_retrieval()
    
    # 测试4: 用户过滤
    await test_user_filtering()
    
    # 测试5: Memory Scope
    await test_memory_scope()
    
    # 测试6: Agentic 检索
    await test_agentic_retrieval()
    
    # 测试7: 综合测试
    await test_comprehensive()
    
    print("\n" + "=" * 100)
    print("✅ 所有测试完成！")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())

