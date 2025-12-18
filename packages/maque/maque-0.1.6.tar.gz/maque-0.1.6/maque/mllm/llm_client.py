"""
LLMClient - 统一的 LLM 客户端封装

自动根据配置选择 OpenAIClient 或 GeminiClient，提供统一接口。
"""

import asyncio
from typing import TYPE_CHECKING, List, Union, Optional, Literal

from .base_client import LLMClientBase
from .openaiclient import OpenAIClient
from .geminiclient import GeminiClient
from .response_cache import ResponseCacheConfig

if TYPE_CHECKING:
    from maque.async_api.interface import RequestResult


class LLMClient:
    """
    统一的 LLM 客户端，支持 OpenAI 兼容 API 和 Gemini API

    根据 provider 参数自动选择底层客户端：
    - "openai": 使用 OpenAIClient（适用于 OpenAI、vLLM、通义千问、DeepSeek 等）
    - "gemini": 使用 GeminiClient（适用于 Google Gemini）

    Example (OpenAI 兼容):
        >>> client = LLMClient(
        ...     provider="openai",
        ...     base_url="https://api.openai.com/v1",
        ...     api_key="your-key",
        ...     model="gpt-4",
        ... )
        >>> result = await client.chat_completions(messages)

    Example (Gemini):
        >>> client = LLMClient(
        ...     provider="gemini",
        ...     api_key="your-google-key",
        ...     model="gemini-2.5-flash",
        ... )
        >>> result = await client.chat_completions(messages)

    Example (自动推断):
        >>> # base_url 包含 "generativelanguage.googleapis.com" 或 "aiplatform.googleapis.com"
        >>> # 会自动选择 Gemini
        >>> client = LLMClient(
        ...     base_url="https://generativelanguage.googleapis.com/v1beta",
        ...     api_key="your-key",
        ...     model="gemini-2.5-flash",
        ... )
    """

    def __init__(
        self,
        provider: Literal["openai", "gemini", "auto"] = "auto",
        # 通用参数
        base_url: str = None,
        api_key: str = None,
        model: str = None,
        concurrency_limit: int = 10,
        max_qps: int = None,  # 不同 provider 有不同默认值
        timeout: int = 120,
        retry_times: int = 3,
        retry_delay: float = 1.0,
        cache_image: bool = False,
        cache_dir: str = "image_cache",
        # Gemini/Vertex AI 专用
        use_vertex_ai: bool = False,
        project_id: str = None,
        location: str = "us-central1",
        credentials=None,
        # 响应缓存配置
        cache: Optional[ResponseCacheConfig] = None,
        **kwargs,
    ):
        """
        初始化统一 LLM 客户端

        Args:
            provider: 指定使用的 provider
                - "openai": OpenAI 兼容 API
                - "gemini": Google Gemini API
                - "auto": 根据 base_url 自动推断
            base_url: API 基础 URL
            api_key: API 密钥
            model: 默认模型名称
            concurrency_limit: 并发请求限制
            max_qps: 最大 QPS（openai 默认 1000，gemini 默认 60）
            timeout: 请求超时时间
            retry_times: 重试次数
            retry_delay: 重试延迟
            cache_image: 是否缓存图片
            cache_dir: 图片缓存目录
            use_vertex_ai: 是否使用 Vertex AI（仅 Gemini）
            project_id: GCP 项目 ID（仅 Vertex AI）
            location: GCP 区域（仅 Vertex AI）
            credentials: Google Cloud 凭证（仅 Vertex AI）
            cache: 响应缓存配置，默认启用（24小时TTL）
        """
        # 自动推断 provider
        if provider == "auto":
            provider = self._infer_provider(base_url, use_vertex_ai)

        self._provider = provider
        self._model = model

        if provider == "gemini":
            self._client = GeminiClient(
                api_key=api_key,
                model=model,
                base_url=base_url,
                concurrency_limit=concurrency_limit,
                max_qps=max_qps if max_qps is not None else 60,
                timeout=timeout,
                retry_times=retry_times,
                retry_delay=retry_delay,
                cache_image=cache_image,
                cache_dir=cache_dir,
                cache=cache,
                use_vertex_ai=use_vertex_ai,
                project_id=project_id,
                location=location,
                credentials=credentials,
                **kwargs,
            )
        else:  # openai
            if not base_url:
                raise ValueError("OpenAI provider 需要提供 base_url")
            self._client = OpenAIClient(
                base_url=base_url,
                api_key=api_key or "EMPTY",
                model=model,
                concurrency_limit=concurrency_limit,
                max_qps=max_qps if max_qps is not None else 1000,
                timeout=timeout,
                retry_times=retry_times,
                retry_delay=retry_delay,
                cache_image=cache_image,
                cache_dir=cache_dir,
                cache=cache,
                **kwargs,
            )

    @staticmethod
    def _infer_provider(base_url: str, use_vertex_ai: bool) -> str:
        """根据 base_url 推断 provider"""
        if use_vertex_ai:
            return "gemini"
        if base_url:
            url_lower = base_url.lower()
            if "generativelanguage.googleapis.com" in url_lower:
                return "gemini"
            if "aiplatform.googleapis.com" in url_lower:
                return "gemini"
        return "openai"

    @property
    def provider(self) -> str:
        """返回当前使用的 provider"""
        return self._provider

    @property
    def client(self) -> LLMClientBase:
        """返回底层客户端实例（用于访问特定功能）"""
        return self._client

    # ========== 统一接口 ==========

    async def chat_completions(
        self,
        messages: List[dict],
        model: str = None,
        return_raw: bool = False,
        show_progress: bool = False,
        **kwargs,
    ) -> Union[str, "RequestResult"]:
        """
        单条聊天完成

        Args:
            messages: 消息列表（OpenAI 格式）
            model: 模型名称（可选，使用初始化时的默认值）
            return_raw: 是否返回原始响应
            show_progress: 是否显示进度
            **kwargs: 其他参数

        Returns:
            生成的文本或原始响应对象
        """
        return await self._client.chat_completions(
            messages=messages,
            model=model,
            return_raw=return_raw,
            show_progress=show_progress,
            **kwargs,
        )

    def chat_completions_sync(
        self,
        messages: List[dict],
        model: str = None,
        return_raw: bool = False,
        **kwargs,
    ) -> Union[str, "RequestResult"]:
        """同步版本的聊天完成"""
        return self._client.chat_completions_sync(
            messages=messages,
            model=model,
            return_raw=return_raw,
            **kwargs,
        )

    async def chat_completions_batch(
        self,
        messages_list: List[List[dict]],
        model: str = None,
        return_raw: bool = False,
        show_progress: bool = True,
        return_summary: bool = False,
        use_cache: bool = False,
        output_file: Optional[str] = None,
        flush_interval: float = 1.0,
        **kwargs,
    ) -> Union[List[str], tuple]:
        """
        批量聊天完成（支持断点续传）

        Args:
            messages_list: 消息列表的列表
            model: 模型名称
            return_raw: 是否返回原始响应
            show_progress: 是否显示进度条
            return_summary: 是否返回统计摘要
            use_cache: 是否使用缓存（相同 prompt 去重）
            output_file: 输出文件路径（JSONL），用于断点续传和持久化
            flush_interval: 文件刷新间隔（秒），默认 1 秒
            **kwargs: 其他参数

        Returns:
            生成的文本列表，或 (文本列表, 摘要)
        """
        return await self._client.chat_completions_batch(
            messages_list=messages_list,
            model=model,
            return_raw=return_raw,
            show_progress=show_progress,
            return_summary=return_summary,
            use_cache=use_cache,
            output_file=output_file,
            flush_interval=flush_interval,
            **kwargs,
        )

    def chat_completions_batch_sync(
        self,
        messages_list: List[List[dict]],
        model: str = None,
        return_raw: bool = False,
        show_progress: bool = True,
        return_summary: bool = False,
        use_cache: bool = False,
        output_file: Optional[str] = None,
        flush_interval: float = 1.0,
        **kwargs,
    ) -> Union[List[str], tuple]:
        """同步版本的批量聊天完成"""
        return self._client.chat_completions_batch_sync(
            messages_list=messages_list,
            model=model,
            return_raw=return_raw,
            show_progress=show_progress,
            return_summary=return_summary,
            use_cache=use_cache,
            output_file=output_file,
            flush_interval=flush_interval,
            **kwargs,
        )

    async def chat_completions_stream(
        self,
        messages: List[dict],
        model: str = None,
        **kwargs,
    ):
        """
        流式聊天完成 - 逐 token 返回响应

        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数

        Yields:
            str: 流式返回的 token 片段
        """
        async for chunk in self._client.chat_completions_stream(
            messages=messages,
            model=model,
            **kwargs,
        ):
            yield chunk

    def model_list(self) -> List[str]:
        """获取可用模型列表"""
        return self._client.model_list()

    # ========== OpenAI 专有方法（Gemini 会抛出 NotImplementedError）==========

    async def iter_chat_completions_batch(
        self,
        messages_list: List[List[dict]],
        model: str = None,
        batch_size: int = None,
        return_raw: bool = False,
        show_progress: bool = True,
        return_summary: bool = False,
        **kwargs,
    ):
        """
        迭代式批量聊天完成（仅 OpenAI provider 支持）

        边请求边返回结果，适合处理大批量数据时节省内存

        Args:
            messages_list: 消息列表的列表
            model: 模型名称
            batch_size: 每批返回的数量
            return_raw: 是否返回原始响应
            show_progress: 是否显示进度
            return_summary: 是否返回统计摘要
            **kwargs: 其他参数

        Yields:
            生成的文本或 (文本, 摘要)
        """
        if self._provider != "openai":
            raise NotImplementedError(
                f"iter_chat_completions_batch 仅 OpenAI provider 支持，"
                f"当前 provider: {self._provider}"
            )
        async for result in self._client.iter_chat_completions_batch(
            messages_list=messages_list,
            model=model or self._model,
            batch_size=batch_size,
            return_raw=return_raw,
            show_progress=show_progress,
            return_summary=return_summary,
            **kwargs,
        ):
            yield result

    def __repr__(self) -> str:
        return f"LLMClient(provider='{self._provider}', model='{self._model}')"
