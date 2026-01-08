import discord
from discord import app_commands
from services.tts_service import TTSService
from services.ai_client import AIClient
import os
from core.logger import logger

tts_service = TTSService()
ai_client = AIClient()  # Если нужно для проверки или кэша, но в основном не обязателен

@app_commands.command(name="tts_chat", description="Озвучить последний ответ AI голосом")
async def tts_chat(interaction: discord.Interaction):
    if not tts_service.available:
        await interaction.response.send_message(
            "❌ TTS-сервис недоступен. Установи: `pip install edge-tts`",
            ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)

    # Ищем последний ответ бота в истории канала
    bot_response_text = None
    async for message in interaction.channel.history(limit=20):
        if message.author == interaction.client.user:  # Сообщение от бота
            if message.embeds and message.embeds[0].description:
                # Ответы от /ask и /ask_helpful приходят в embed.description
                bot_response_text = message.embeds[0].description
                break
            elif message.content:
                # На всякий случай, если ответ в чистом тексте
                bot_response_text = message.content
                break

    if not bot_response_text:
        await interaction.followup.send(
            "❌ Не найден последний ответ AI. Сначала используй /ask или /ask_helpful",
            ephemeral=True
        )
        return

    # Обрезаем, если слишком длинный (edge-tts может зависнуть на очень длинном тексте)
    if len(bot_response_text) > 2000:
        bot_response_text = bot_response_text[:2000] + "…"

    status = await interaction.followup.send(
        embed=discord.Embed(title="🔊 Озвучиваю ответ AI...", color=0x3498db)
    )

    try:
        filepath = await tts_service.generate(bot_response_text, interaction.user.id, preset="normal")

        if not filepath or not os.path.exists(filepath):
            raise Exception("Файл не создан")

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if file_size_mb > 8:
            await status.edit(embed=discord.Embed(
                title="❌ Файл слишком большой (>8 MB)",
                description=f"Размер: {file_size_mb:.1f} MB",
                color=0xe74c3c
            ))
            if os.path.exists(filepath):
                os.remove(filepath)
            return

        with open(filepath, "rb") as f:
            audio_file = discord.File(f, filename="ai_response.mp3")

        embed = discord.Embed(title="🔊 Ответ AI озвучен!", color=0x2ecc71)
        embed.add_field(name="Текст", value=bot_response_text[:1000] + ("..." if len(bot_response_text) > 1000 else ""), inline=False)
        embed.set_footer(text=f"Запрошено: {interaction.user.display_name}")

        await status.edit(embed=embed, attachments=[audio_file])

        # Удаляем файл после отправки
        try:
            os.remove(filepath)
        except:
            pass

    except Exception as e:
        logger.error(f"TTS_chat error: {e}")
        await status.edit(embed=discord.Embed(
            title="❌ Ошибка озвучки",
            description="Не удалось сгенерировать аудио. Попробуй позже.",
            color=0xe74c3c
        ))