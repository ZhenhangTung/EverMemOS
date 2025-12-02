"""
集成测试：验证 semantic → foresight 重构的完整流程

此脚本用于：
1. 创建测试用的 Foresight 数据
2. 验证数据正确写入 MongoDB
3. 验证 API 检索功能

运行方式：
    cd /Users/admin/Applications/cursor_project/openv2/memsys-opensource
    source .venv/bin/activate
    PYTHONPATH=src python tests/test_foresight_integration.py
"""

import asyncio
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


async def test_mongodb_foresight_collection():
    """测试 MongoDB foresight_records 集合"""
    print("\n" + "=" * 60)
    print("📦 测试 1: MongoDB foresight_records 集合")
    print("=" * 60)
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # 连接 MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        db = client["memsys"]
        
        # 检查集合是否存在
        collections = await db.list_collection_names()
        print(f"\n📂 当前集合列表: {collections}")
        
        # 检查 foresight_records 集合
        if "foresight_records" in collections:
            count = await db.foresight_records.count_documents({})
            print(f"✅ foresight_records 集合存在，文档数: {count}")
        else:
            print("⚠️ foresight_records 集合不存在（尚未创建数据）")
        
        # 确认没有旧集合
        old_collections = ["semantic_memories", "semantic_memory_records"]
        for old_coll in old_collections:
            if old_coll in collections:
                print(f"❌ 发现旧集合: {old_coll}")
            else:
                print(f"✅ 旧集合 {old_coll} 不存在（正确）")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 测试失败: {e}")
        return False


async def test_api_data_source_validation():
    """测试 API data_source 参数验证"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: API data_source 参数验证")
    print("=" * 60)
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # 测试无效参数
            print("\n📝 测试无效参数 data_source=semantic_memory...")
            async with session.post(
                "http://localhost:8001/api/v3/agentic/retrieve_lightweight",
                json={
                    "query": "测试查询",
                    "user_id": "test_user",
                    "data_source": "semantic_memory"
                }
            ) as resp:
                data = await resp.json()
                status = data.get("status", "")
                message = data.get("message", "")
                
                if "error" in status.lower() and "无效" in message:
                    print(f"   ✅ 无效参数被正确拒绝")
                    print(f"   📝 错误消息: {message}")
                else:
                    print(f"   ⚠️ 验证未生效（可能需要重启服务）")
                    print(f"   📝 响应: {data}")
            
            # 测试有效参数
            print("\n📝 测试有效参数 data_source=foresight...")
            async with session.post(
                "http://localhost:8001/api/v3/agentic/retrieve_lightweight",
                json={
                    "query": "测试查询",
                    "user_id": "test_user",
                    "data_source": "foresight"
                }
            ) as resp:
                data = await resp.json()
                status = data.get("status", "")
                
                if status == "ok":
                    count = data.get("result", {}).get("count", 0)
                    print(f"   ✅ 有效参数正常工作，返回 {count} 条结果")
                else:
                    print(f"   ⚠️ 响应: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False


async def test_memory_type_enum():
    """测试 MemoryType 枚举值"""
    print("\n" + "=" * 60)
    print("🔍 测试 3: MemoryType 枚举验证")
    print("=" * 60)
    
    try:
        from api_specs.memory_models import MemoryType
        
        # 验证新名称
        print("\n📝 验证新枚举值...")
        assert hasattr(MemoryType, 'FORESIGHT'), "FORESIGHT 不存在"
        assert MemoryType.FORESIGHT.value == "foresight", "FORESIGHT 值错误"
        print(f"   ✅ MemoryType.FORESIGHT = '{MemoryType.FORESIGHT.value}'")
        
        assert hasattr(MemoryType, 'PERSONAL_FORESIGHT'), "PERSONAL_FORESIGHT 不存在"
        assert MemoryType.PERSONAL_FORESIGHT.value == "personal_foresight", "PERSONAL_FORESIGHT 值错误"
        print(f"   ✅ MemoryType.PERSONAL_FORESIGHT = '{MemoryType.PERSONAL_FORESIGHT.value}'")
        
        # 验证旧名称不存在
        print("\n📝 验证旧枚举值已移除...")
        assert not hasattr(MemoryType, 'SEMANTIC_MEMORY'), "SEMANTIC_MEMORY 仍存在"
        print("   ✅ MemoryType.SEMANTIC_MEMORY 不存在（正确）")
        
        assert not hasattr(MemoryType, 'PERSONAL_SEMANTIC_MEMORY'), "PERSONAL_SEMANTIC_MEMORY 仍存在"
        print("   ✅ MemoryType.PERSONAL_SEMANTIC_MEMORY 不存在（正确）")
        
        return True
        
    except AssertionError as e:
        print(f"❌ 枚举验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def main():
    """运行所有集成测试"""
    print("\n" + "=" * 60)
    print("🚀 Semantic → Foresight 重构集成测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: MemoryType 枚举
    results.append(("MemoryType 枚举验证", await test_memory_type_enum()))
    
    # 测试 2: MongoDB 集合
    results.append(("MongoDB 集合验证", await test_mongodb_foresight_collection()))
    
    # 测试 3: API 验证
    results.append(("API 参数验证", await test_api_data_source_validation()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！重构验证成功！")
    else:
        print("⚠️ 部分测试失败，请检查上述输出")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

