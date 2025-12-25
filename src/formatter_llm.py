"""
LLM 排版模块
使用 OpenAI 兼容 API 对 OCR 结果进行智能排版和校对
"""
import logging
import asyncio
from typing import List

import httpx

from .models import OCRResult, FormattedResult
from .config import settings

logger = logging.getLogger(__name__)

# 排版 prompt
FORMAT_PROMPT = """你是一个专业的文档排版助手。请将以下 OCR 识别的文本进行排版和校对，输出格式化的 Markdown 文本。

要求：
1. 修正明显的 OCR 识别错误（如错别字、乱码）
2. 根据内容语义合理分段
3. 识别并标记标题（使用 # ## ### 等 Markdown 标题语法）
4. 保持原文内容的完整性，不要添加或删除信息
5. 如果有列表内容，使用 Markdown 列表格式
6. 直接输出排版后的 Markdown 文本，不要添加任何解释

OCR 识别的原始文本：
"""


async def format_with_llm(results: List[OCRResult]) -> FormattedResult:
    """
    使用 LLM 对 OCR 结果进行排版

    Args:
        results: OCR 结果列表

    Returns:
        FormattedResult 包含排版后的 markdown 文本
    """
    # 检查配置
    if not settings.is_llm_configured():
        return FormattedResult(
            markdown="",
            success=False,
            error="LLM 未配置，请在 .env 中设置 LLM_BASE_URL 和 LLM_API_KEY"
        )

    if not results:
        return FormattedResult(markdown="", success=True)

    try:
        # 提取纯文本（按顺序拼接）
        raw_text = "\n".join(r.rec_txt for r in results)

        # 构建请求
        messages = [
            {"role": "user", "content": FORMAT_PROMPT + raw_text}
        ]

        # 调用 LLM API
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "max_tokens": settings.llm_max_tokens,
                    "temperature": 0.3  # 较低温度保持输出稳定
                }
            )

            response.raise_for_status()
            data = response.json()

            # 提取响应内容
            if "choices" in data and len(data["choices"]) > 0:
                markdown = data["choices"][0]["message"]["content"].strip()
                logger.info(f"LLM 排版完成，输出长度: {len(markdown)}")
                return FormattedResult(markdown=markdown, success=True)
            else:
                return FormattedResult(
                    markdown="",
                    success=False,
                    error="LLM 响应格式异常"
                )

    except httpx.TimeoutException:
        error_msg = f"LLM 请求超时（{settings.llm_timeout}秒）"
        logger.error(error_msg)
        return FormattedResult(markdown="", success=False, error=error_msg)

    except httpx.HTTPStatusError as e:
        error_msg = f"LLM API 错误: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return FormattedResult(markdown="", success=False, error=error_msg)

    except Exception as e:
        error_msg = f"LLM 排版失败: {str(e)}"
        logger.error(error_msg)
        return FormattedResult(markdown="", success=False, error=error_msg)
