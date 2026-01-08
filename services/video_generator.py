import aiohttp
import asyncio
import os
import uuid
from config import POLLO_API_KEY, GENERATED_VIDEOS_DIR, POLLO_BASE_URL
from utils.cache import image_cache  # или video_cache
from core.logger import logger

class VideoGenerator:
    def __init__(self):
        self.api_key = POLLO_API_KEY
        self.base_url = POLLO_BASE_URL  # https://pollo.ai/api/platform/generation/sora/sora-2
        self.tasks_url = "https://pollo.ai/api/platform/tasks/"  # для polling статуса
        self.available = bool(self.api_key)
        if not self.available:
            logger.warning("Pollo.ai API key not set — video generation disabled")

    async def generate(self, prompt: str, user_id: int, image_url: str | None = None,
                       length: int = 8, aspect_ratio: str = "16:9") -> str | None:
        """
        Асинхронная генерация видео Sora 2 через Pollo.ai с polling.
        length: только 4, 8 или 12 секунд
        """
        if not self.available:
            return None

        # Валидация length
        ALLOWED_LENGTHS = {4, 8, 12}
        if length not in ALLOWED_LENGTHS:
            length = min(ALLOWED_LENGTHS, key=lambda x: abs(x - length))
            logger.warning(f"Invalid length {length} → fallback to {length}s for Sora 2")

        # Кэш (учитываем image_url если есть)
        image_part = f":img:{hash(image_url)}" if image_url else ""
        cache_key = f"vid:sora2:{user_id}:{hash(prompt)}:{length}:{aspect_ratio}{image_part}"

        if cached := image_cache.get(cache_key):
            logger.info(f"Sora 2 cache hit for user {user_id}")
            return cached

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "input": {
                "prompt": prompt,
                "length": length,
                "aspectRatio": aspect_ratio
            }
        }

        if image_url:
            payload["input"]["image"] = image_url

        # Опционально: добавь webhook если есть публичный эндпоинт
        # payload["webhookUrl"] = "https://your-bot.com/webhook/pollo"

        try:
            async with aiohttp.ClientSession() as session:
                # Шаг 1: Создаём задачу
                async with session.post(self.base_url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Pollo.ai create task error {resp.status}: {error_text}")
                        return None
                    data = await resp.json()
                    task_id = data.get("taskId")
                    if not task_id:
                        logger.error("No taskId in response")
                        return None
                    logger.info(f"Sora 2 task created: {task_id}")

                # Шаг 2: Polling статуса (max ~5 минут)
                poll_interval = 10  # секунд между проверками
                max_attempts = 30   # ~5 минут
                for attempt in range(max_attempts):
                    await asyncio.sleep(poll_interval)

                    async with session.get(f"{self.tasks_url}{task_id}", headers=headers) as status_resp:
                        if status_resp.status != 200:
                            logger.error(f"Status check error {status_resp.status}")
                            continue
                        status_data = await status_resp.json()

                        status = status_data.get("status")
                        logger.info(f"Task {task_id} status: {status}")

                        if status == "succeed":
                            video_url = status_data.get("video_url") or status_data.get("output", {}).get("url")
                            if not video_url:
                                logger.warning("No video_url in succeed response")
                                return None
                            break

                        if status == "failed":
                            logger.error(f"Task failed: {status_data}")
                            return None

                        # Если processing/waiting — продолжаем poll

                else:
                    logger.warning(f"Task {task_id} timeout after {max_attempts * poll_interval}s")
                    return None

                # Шаг 3: Скачиваем видео
                async with session.get(video_url) as vid_resp:
                    if vid_resp.status != 200:
                        logger.error(f"Video download error {vid_resp.status}")
                        return None

                    filename = f"sora2_{user_id}_{uuid.uuid4().hex[:8]}.mp4"
                    filepath = os.path.join(GENERATED_VIDEOS_DIR, filename)

                    with open(filepath, "wb") as f:
                        async for chunk in vid_resp.content.iter_chunked(1024 * 1024):
                            f.write(chunk)

                    image_cache.set(cache_key, filepath)
                    logger.info(f"Sora 2 video saved: {filepath}")
                    return filepath

        except Exception as e:
            logger.error(f"Sora 2 exception: {e}")
            return None