import edge_tts
import asyncio
import os
import uuid
from core.logger import logger
from config import TTS_CACHE_DIR

os.makedirs(TTS_CACHE_DIR, exist_ok=True)

class TTSService:
    def __init__(self):
        self.available = True
        try:
            # Просто импортируем, чтобы проверить
            import edge_tts  # noqa: F401
        except ImportError:
            logger.warning("edge-tts не установлен. Установи: pip install edge-tts")
            self.available = False

    async def generate(self, text: str, user_id: int, preset: str = "normal") -> str | None:
        if not self.available:
            return None

        try:
            # Выбор голоса в зависимости от пресета
            voice_map = {
                "normal": "ru-RU-SvetlanaNeural",   # Приятный женский русский
                "fast": "ru-RU-DmitryNeural",       # Мужской, чуть быстрее
                "calm": "ru-RU-SvetlanaNeural"      # Тот же спокойный
            }
            voice = voice_map.get(preset, "ru-RU-SvetlanaNeural")

            # Параметры скорости
            rate_map = {
                "normal": "+0%",
                "fast": "+30%",
                "calm": "-10%"
            }
            rate = rate_map.get(preset, "+0%")

            filename = f"tts_{user_id}_{uuid.uuid4().hex[:8]}.mp3"
            filepath = os.path.join(TTS_CACHE_DIR, filename)

            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(filepath)

            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.info(f"TTS сгенерирован: {filepath} (голос: {voice}, rate: {rate})")
                return filepath
            else:
                logger.error("TTS файл пустой или не создан")
                return None

        except Exception as e:
            logger.error(f"Ошибка TTS: {e}")
            return None