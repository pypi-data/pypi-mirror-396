"""
Gemini API Client - Google Gemini 模型的批量调用客户端

与 OpenAIClient 保持相同的接口，方便上层代码无缝切换。
"""

import re
from typing import List, Optional, Any

from loguru import logger

from .base_client import LLMClientBase
from .response_cache import ResponseCacheConfig


class GeminiClient(LLMClientBase):
    """
    Google Gemini API 客户端

    支持 Gemini Developer API 和 Vertex AI。

    Example (Gemini Developer API):
        >>> client = GeminiClient(api_key="your-key", model="gemini-2.5-flash")
        >>> result = await client.chat_completions(messages)

    Example (Vertex AI):
        >>> client = GeminiClient(
        ...     project_id="your-project-id",
        ...     location="us-central1",
        ...     model="gemini-2.5-flash",
        ...     use_vertex_ai=True,
        ... )
    """

    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    VERTEX_AI_URL_TEMPLATE = "https://{location}-aiplatform.googleapis.com/v1"

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        concurrency_limit: int = 10,
        max_qps: int = 60,
        timeout: int = 120,
        retry_times: int = 3,
        retry_delay: float = 1.0,
        cache_image: bool = False,
        cache_dir: str = "image_cache",
        cache: Optional[ResponseCacheConfig] = None,
        use_vertex_ai: bool = False,
        project_id: str = None,
        location: str = "us-central1",
        credentials: Any = None,
        **kwargs,
    ):
        self._use_vertex_ai = use_vertex_ai
        self._project_id = project_id
        self._location = location
        self._credentials = credentials
        self._access_token = None
        self._token_expiry = None

        if use_vertex_ai:
            if not project_id:
                raise ValueError("Vertex AI 模式需要提供 project_id")
            effective_base_url = base_url or self.VERTEX_AI_URL_TEMPLATE.format(location=location)
        else:
            if not api_key:
                raise ValueError("Gemini Developer API 模式需要提供 api_key")
            effective_base_url = base_url or self.DEFAULT_BASE_URL

        super().__init__(
            base_url=effective_base_url,
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

    # ========== 实现基类核心方法 ==========

    def _get_url(self, model: str, stream: bool = False) -> str:
        action = "streamGenerateContent" if stream else "generateContent"
        if self._use_vertex_ai:
            return (
                f"{self._base_url}/projects/{self._project_id}"
                f"/locations/{self._location}/publishers/google/models/{model}:{action}"
            )
        return f"{self._base_url}/models/{model}:{action}?key={self._api_key}"

    def _get_stream_url(self, model: str) -> str:
        """Gemini 流式需要添加 alt=sse 参数"""
        url = self._get_url(model, stream=True)
        return url + ("&alt=sse" if "?" in url else "?alt=sse")

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self._use_vertex_ai:
            headers["Authorization"] = f"Bearer {self._get_access_token()}"
        return headers

    def _build_request_body(
        self,
        messages: List[dict],
        model: str,
        stream: bool = False,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        top_k: int = None,
        stop_sequences: List[str] = None,
        safety_settings: List[dict] = None,
        **kwargs,
    ) -> dict:
        contents, system_obj = self._convert_messages_to_contents(messages)
        body = {"contents": contents}

        if system_obj:
            body["systemInstruction"] = system_obj

        gen_config = {}
        if max_tokens is not None:
            gen_config["maxOutputTokens"] = max_tokens
        if temperature is not None:
            gen_config["temperature"] = temperature
        if top_p is not None:
            gen_config["topP"] = top_p
        if top_k is not None:
            gen_config["topK"] = top_k
        if stop_sequences:
            gen_config["stopSequences"] = stop_sequences

        if gen_config:
            body["generationConfig"] = gen_config
        if safety_settings:
            body["safetySettings"] = safety_settings

        return body

    def _extract_content(self, response_data: dict) -> Optional[str]:
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                if "promptFeedback" in response_data:
                    block_reason = response_data["promptFeedback"].get("blockReason", "UNKNOWN")
                    logger.warning(f"Request blocked by Gemini: {block_reason}")
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if "text" in p]
            return "".join(texts) if texts else None
        except Exception as e:
            logger.warning(f"Failed to extract response text: {e}")
            return None

    # ========== Gemini 特有方法 ==========

    def _get_access_token(self) -> str:
        """获取 Vertex AI 的 Access Token"""
        import time

        if self._access_token and self._token_expiry and time.time() < self._token_expiry - 60:
            return self._access_token

        try:
            import google.auth
            import google.auth.transport.requests

            credentials = self._credentials or google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )[0]

            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            self._access_token = credentials.token
            self._token_expiry = time.time() + 3600
            return self._access_token
        except ImportError:
            raise ImportError("Vertex AI 模式需要安装 google-auth: pip install google-auth")
        except Exception as e:
            raise RuntimeError(f"获取 Vertex AI 访问令牌失败: {e}")

    def _convert_messages_to_contents(
        self, messages: List[dict], system_instruction: str = None
    ) -> tuple[List[dict], Optional[dict]]:
        """将 OpenAI 格式的 messages 转换为 Gemini 格式"""
        contents = []
        extracted_system = system_instruction

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                if isinstance(content, str):
                    extracted_system = content
                elif isinstance(content, list):
                    texts = [p.get("text", "") for p in content if p.get("type") == "text"]
                    extracted_system = "\n".join(texts)
                continue

            gemini_role = "model" if role == "assistant" else "user"
            parts = self._convert_content_to_parts(content)

            if parts:
                contents.append({"role": gemini_role, "parts": parts})

        system_obj = {"parts": [{"text": extracted_system}]} if extracted_system else None
        return contents, system_obj

    def _convert_content_to_parts(self, content: Any) -> List[dict]:
        """将 OpenAI 格式的 content 转换为 Gemini 格式的 parts"""
        if content is None:
            return []
        if isinstance(content, str):
            return [{"text": content}]

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append({"text": item})
                elif isinstance(item, dict):
                    item_type = item.get("type", "text")
                    if item_type == "text" and item.get("text"):
                        parts.append({"text": item["text"]})
                    elif item_type == "image_url":
                        if img := self._convert_image_url(item.get("image_url", {})):
                            parts.append(img)
                    elif item_type == "image":
                        if img := self._convert_image_direct(item):
                            parts.append(img)
            return parts
        return []

    def _convert_image_url(self, image_url_obj: dict) -> Optional[dict]:
        """将 OpenAI 的 image_url 格式转换为 Gemini 的 inline_data 格式"""
        url = image_url_obj.get("url", "")
        if not url:
            return None

        if url.startswith("data:"):
            match = re.match(r"data:([^;]+);base64,(.+)", url)
            if match:
                return {"inline_data": {"mime_type": match.group(1), "data": match.group(2)}}

        logger.warning(f"Gemini API 不直接支持外部 URL，请先转换为 base64: {url[:50]}...")
        return None

    def _convert_image_direct(self, image_obj: dict) -> Optional[dict]:
        """处理直接的图片数据"""
        data = image_obj.get("data", "")
        if data:
            return {"inline_data": {"mime_type": image_obj.get("mime_type", "image/jpeg"), "data": data}}
        return None

    def model_list(self) -> List[str]:
        """获取可用模型列表"""
        import requests

        if self._use_vertex_ai:
            url = f"{self._base_url}/projects/{self._project_id}/locations/{self._location}/publishers/google/models"
            response = requests.get(url, headers=self._get_headers())
        else:
            response = requests.get(f"{self._base_url}/models?key={self._api_key}")

        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name", "").replace("models/", "") for m in models]
        logger.error(f"Failed to fetch model list: {response.text}")
        return []
