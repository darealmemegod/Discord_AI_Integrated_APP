import aiohttp
import base64
import os
import time
from config import STABILITY_API_KEY, STABLE_DIFFUSION_API, GENERATED_IMAGES_DIR
from utils.cache import image_cache
from core.logger import logger

class ImageGenerator:
    def __init__(self):
        self.api_key = STABILITY_API_KEY
        self.api_url = STABLE_DIFFUSION_API
        self.available = bool(self.api_key)
        if not self.available:
            logger.warning("Stability AI API key not set — image generation disabled")

    async def generate(self, prompt: str, user_id: int, seed: int | None = None) -> str | None:
        """
        Генерирует изображение по промпту.
        Возвращает путь к файлу или None.
        """
        if not self.available:
            return None

        # Кэш по промпту + user_id (чтобы одинаковые запросы не спамили API)
        cache_key = f"img:{user_id}:{hash(prompt.lower())}"
        if cached_path := image_cache.get(cache_key):
            logger.info(f"Image cache hit for user {user_id}")
            return cached_path

        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": "blurry, bad anatomy, extra limbs, low quality, artifact", "weight": -1.0}
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
            "style_preset": "digital-art"  # можно менять: photographic, anime и т.д.
        }
        if seed:
            payload["seed"] = seed

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=60) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        image_b64 = data["artifacts"][0]["base64"]
                        image_bytes = base64.b64decode(image_b64)

                        filename = f"gen_{user_id}_{int(time.time())}.png"
                        filepath = os.path.join(GENERATED_IMAGES_DIR, filename)

                        with open(filepath, "wb") as f:
                            f.write(image_bytes)

                        image_cache.set(cache_key, filepath)
                        logger.info(f"Image generated and saved: {filepath}")
                        return filepath
                    else:
                        error_text = await resp.text()
                        logger.error(f"Stability AI error {resp.status}: {error_text[:200]}")
                        return None
        except Exception as e:
            logger.error(f"Image generation exception: {e}")
            return None