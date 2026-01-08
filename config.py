from dotenv import load_dotenv
import os

load_dotenv()

# === Ключи ===
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN не найден в .env! Проверь файл и имя переменной.")

PIAPI_KEY = os.getenv("PIAPI_KEY")
if PIAPI_KEY is None:
    raise ValueError("PIAPI_KEY не найден! Зарегистрируйся на https://piapi.ai и добавь ключ в .env")

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
FAL_KEY = os.getenv("FAL_KEY")

# === LLM ===
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")

# === API для видео через PiAPI (Kling) ===
PIAPI_BASE_URL = "https://api.piapi.ai/api/v1"

# === Папки ===
GENERATED_IMAGES_DIR = "generated_images"
GENERATED_VIDEOS_DIR = "generated_videos"
TTS_CACHE_DIR = "tts_cache"

os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

# Отладка
print("DISCORD_TOKEN загружен:", "Да" if DISCORD_TOKEN else "НЕТ")
print("PIAPI_KEY загружен:", "Да" if PIAPI_KEY else "НЕТ")
print("STABILITY_API_KEY:", "Да" if STABILITY_API_KEY else "Нет")
print("FAL_KEY:", "Да" if FAL_KEY else "Нет")

# === API для изображений (Stability AI) ===
STABLE_DIFFUSION_API = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

KIE_API_KEY = os.getenv("KIE_API_KEY")
if KIE_API_KEY is None:
    raise ValueError("KIE_API_KEY не найден! Зарегистрируйся на https://kie.ai")

KIE_BASE_URL = "https://api.kie.ai/v1"  # базовый, эндпоинты вроде /generate или /tasks — см. ниже

POLLO_API_KEY = os.getenv("POLLO_API_KEY")
if POLLO_API_KEY is None:
    raise ValueError("POLLO_API_KEY не найден! Зарегистрируйся на https://pollo.ai")

POLLO_BASE_URL = "https://pollo.ai/api/platform/generation/sora/sora-2"
