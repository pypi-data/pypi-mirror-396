"""
OpenAI 兼容 API 客户端

支持 OpenAI、vLLM、通义千问、DeepSeek 等兼容 OpenAI API 的服务。
"""

from typing import TYPE_CHECKING, List, Optional

from loguru import logger

from .base_client import LLMClientBase
from .processors.messages_processor import batch_process_messages
from .response_cache import ResponseCacheConfig

if TYPE_CHECKING:
    from maque.async_api.interface import RequestResult


class OpenAIClient(LLMClientBase):
    """
    OpenAI 兼容 API 客户端

    Example:
        >>> client = OpenAIClient(
        ...     base_url="https://api.openai.com/v1",
        ...     api_key="your-key",
        ...     model="gpt-4",
        ... )
        >>> result = await client.chat_completions(messages)
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "EMPTY",
        model: str = None,
        concurrency_limit: int = 10,
        max_qps: int = 1000,
        timeout: int = 100,
        retry_times: int = 3,
        retry_delay: float = 0.55,
        cache_image: bool = False,
        cache_dir: str = "image_cache",
        cache: Optional[ResponseCacheConfig] = None,
        **kwargs,
    ):
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            model=model,
            concurrency_limit=concurrency_limit,
            max_qps=max_qps,
            timeout=timeout,
            retry_times=retry_times,
            retry_delay=retry_delay,
            cache_image=cache_image,
            cache_dir=cache_dir,
            cache=cache,
            **kwargs,
        )
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    # ========== 实现基类核心方法 ==========

    def _get_url(self, model: str, stream: bool = False) -> str:
        return f"{self._base_url}/chat/completions"

    def _get_headers(self) -> dict:
        return self._headers

    def _build_request_body(
        self, messages: List[dict], model: str, stream: bool = False, max_tokens: int = None, **kwargs
    ) -> dict:
        body = {"messages": messages, "model": model, "stream": stream}
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        body.update(kwargs)
        return body

    def _extract_content(self, response_data: dict) -> Optional[str]:
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.warning(f"Failed to extract content: {e}")
            return None

    def _extract_stream_content(self, data: dict) -> Optional[str]:
        try:
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("delta", {}).get("content")
        except Exception:
            pass
        return None

    # ========== OpenAI 特有方法 ==========

    async def iter_chat_completions_batch(
        self,
        messages_list: List[list],
        model: str,
        url: str = None,
        batch_size: int = None,
        return_raw: bool = False,
        show_progress: bool = True,
        preprocess_msg: bool = False,
        return_summary: bool = False,
        **kwargs,
    ):
        """迭代式批量聊天完成，边请求边返回结果"""
        if preprocess_msg:
            messages_list = await batch_process_messages(
                messages_list, preprocess_msg=preprocess_msg, max_concurrent=self._concurrency_limit
            )

        request_params = [
            {"json": self._build_request_body(m, model, **kwargs), "headers": self._headers}
            for m in messages_list
        ]

        async for batch_result in self._client.aiter_stream_requests(
            request_params=request_params,
            url=url or self._get_url(model),
            method="POST",
            show_progress=show_progress,
            batch_size=batch_size,
        ):
            for result in batch_result.completed_requests:
                content = result.data if return_raw else self._extract_content(result.data) if result.data else None
                summary = batch_result.progress.summary(print_to_console=False) if return_summary else None
                yield (content, summary) if return_summary else content

    def model_list(self) -> List[str]:
        from openai import OpenAI
        client = OpenAI(base_url=self._base_url, api_key=self._api_key)
        return [i.id for i in client.models.list()]
