import discord
from discord import app_commands
from services.ai_client import AIClient
from services.tts_service import TTSService
from services.image_generator import ImageGenerator
# from services.video_generator import VideoGenerator  # если добавишь

ai_client = AIClient()
tts_service = TTSService()
image_gen = ImageGenerator()
# video_gen = VideoGenerator()

@app_commands.command(name="status", description="Статус всех сервисов бота")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Статус бота", color=0x9b59b6)

    embed.add_field(name="🤖 AI (локальный LLM)", value="✅ Работает" if await ai_client.test_connection() else "❌ Нет соединения", inline=False)
    embed.add_field(name="🔊 Text-to-Speech", value="✅ Доступно" if tts_service.available else "❌ Не установлен", inline=True)
    embed.add_field(name="🎨 Генерация изображений", value="✅ Доступно" if image_gen.available else "⚠️ Нет API-ключа", inline=True)
    # embed.add_field(name="🎬 Генерация видео", value="✅ Доступно" if video_gen.available else "⚠️ Нет ключа", inline=True)

    embed.set_footer(text="Все функции работают через API или локально — без облачных LLM")
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="help", description="Помощь по командам")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="❓ Помощь по командам", color=0x3498db, description="Вот все доступные команды:")

    embed.add_field(
        name="🤖 AI Чат",
        value="`/ask [вопрос]` — грубый и саркастичный ответ\n"
              "`/ask_helpful [вопрос]` — подробный и полезный ответ",
        inline=False
    )
    embed.add_field(
        name="🔊 Озвучка",
        value="`/tts [текст] [preset]` — MP3-файл с голосом\n"
              "Пресеты: normal, fast, calm",
        inline=False
    )
    embed.add_field(
        name="🎨 Изображения",
        value="`/generate_image [prompt]` — генерация по промпту\n"
              "`/enhance_image [идея]` — AI улучшает промпт → изображение",
        inline=False
    )
    embed.add_field(
        name="🔍 Поиск",
        value="`/search [запрос]` — поиск с фильтрами (время, safe, регион)",
        inline=False
    )
    embed.add_field(
        name="ℹ️ Информация",
        value="`/status` — статус сервисов\n"
              "`/help` — эта справка",
        inline=False
    )

    embed.set_footer(text="Бот полностью модульный и готов к расширению")
    await interaction.response.send_message(embed=embed, ephemeral=True)