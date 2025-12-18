"""
AI 模型包 - 大语言模型和多模态模型客户端

整合了LLM基础功能和MLLM多模态功能
"""

# 多模态模型功能
from .mllm_client import MllmClient
from .table_processor import MllmTableProcessor
from .folder_processor import MllmFolderProcessor

# LLM基础功能
from .base_client import LLMClientBase
from .openaiclient import OpenAIClient
from .geminiclient import GeminiClient
from .llm_client import LLMClient
from .llm_parser import *

# Token 计数和成本估算
from .token_counter import (
    count_tokens,
    count_messages_tokens,
    estimate_cost,
    estimate_batch_cost,
    messages_hash,
    MODEL_PRICING,
)

# 响应缓存
from .response_cache import ResponseCache, ResponseCacheConfig

# Provider 路由
from .provider_router import ProviderRouter, ProviderConfig, create_router_from_urls

__all__ = [
    # 客户端
    'LLMClientBase',
    'MllmClient',
    'MllmTableProcessor',
    'MllmFolderProcessor',
    'OpenAIClient',
    'GeminiClient',
    'LLMClient',
    # Token 计数
    'count_tokens',
    'count_messages_tokens',
    'estimate_cost',
    'estimate_batch_cost',
    'messages_hash',
    'MODEL_PRICING',
    # 缓存
    'ResponseCache',
    'ResponseCacheConfig',
    # Provider 路由
    'ProviderRouter',
    'ProviderConfig',
    'create_router_from_urls',
]
