"""
Elasticsearch 租户化 OXM 模块

本模块提供 Elasticsearch 的租户化支持，包括：
- TenantAwareAsyncDocument: 租户感知的异步文档类
- TenantAwareAliasDoc: 租户感知的别名文档类工厂函数
- 配置工具函数：获取租户 ES 配置、生成连接缓存键等
"""
