import aiohttp
import asyncio
import json


async def call_api_stream(url: str, headers=None, payload=None, timeout_s: int = 600):
    """流式调用模型接口（SSE 或 chunk 模式）"""

    timeout = aiohttp.ClientTimeout(
        total=timeout_s,
        sock_read=timeout_s,   # 最关键：等待 chunk 允许最长 600 秒
    )

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    detail = await resp.text()
                    yield {"error": resp.status, "detail": detail}
                    return

                async for line_bytes in resp.content:
                    line = line_bytes.decode("utf-8").strip()
                    if not line:
                        continue

                    # SSE 格式: data: {...}
                    if line.startswith("data:"):
                        data = line[5:].strip()

                        if data == "[DONE]":
                            return

                        try:
                            obj = json.loads(data)
                        except Exception:
                            continue

                        # 兼容 OpenAI / Qwen 格式
                        delta = None
                        try:
                            delta = obj["choices"][0]["delta"].get("content")
                        except Exception:
                            pass

                        yield delta or ""

                    else:
                        # fallback（保险机制）
                        yield line

        except asyncio.TimeoutError:
            yield {"error": "timeout", "detail": "client timeout"}

        except aiohttp.ClientError as e:
            yield {"error": "client_error", "detail": str(e)}
