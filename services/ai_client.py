import aiohttp
from config import API_BASE_URL, MODEL_NAME
from utils.cache import response_cache
from core.logger import logger
import hashlib
import asyncio

class AIClient:
    def __init__(self):
        self.url = f"{API_BASE_URL}/chat/completions"
        self.headers = {"Content-Type": "application/json"}

    def _make_cache_key(self, prompt: str, user_id: int, mode: str) -> str:
        content = f"{mode}:{prompt}:{user_id}"
        return hashlib.md5(content.encode()).hexdigest()

    async def generate(self, prompt: str, user_id: int, mode: str = "helpful") -> str:
        cache_key = self._make_cache_key(prompt, user_id, mode)
        if cached := response_cache.get(cache_key):
            logger.info(f"Cache hit for user {user_id}, mode {mode}")
            return cached

        # Явные system промпты с указанием языка
        system_prompts = {
            "helpful": "You are a helpful, detailed and friendly AI assistant. "
                       "Answer in the same language as the user's question. "
                       "Be clear, informative and kind.",
            "rude": "You are a sarcastic, rude and direct AI assistant called RudeGPT. "
                    "Answer in the same language as the user's question. "
                    "Use humor, sarcasm and be brutally honest."
        }

        system_content = system_prompts.get(mode, system_prompts["helpful"])

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.8 if mode == "helpful" else 1.0,  # rude чуть креативнее
            "stream": False
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                async with session.post(self.url, json=payload, headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data["choices"][0]["message"]["content"].strip()
                        response_cache.set(cache_key, text)
                        return text
                    else:
                        error_text = await resp.text()
                        logger.error(f"API error {resp.status}: {error_text}")
                        return "AI сейчас недоступен. Попробуй позже."

        except asyncio.TimeoutError:
            logger.error("AI request timeout")
            return "AI слишком долго думает. Упрости вопрос или попробуй позже."
        except Exception as e:
            logger.error(f"AI generate error: {e}")
            return "Временная ошибка AI. Попробуй позже."