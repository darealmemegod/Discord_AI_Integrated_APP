import discord
from discord import app_commands
from services.video_generator import VideoGenerator
from services.ai_client import AIClient
import os

video_gen = VideoGenerator()
ai_client = AIClient()

@app_commands.command(name="generate_video", description="Сгенерировать короткое видео по промпту (Pika Labs)")
@app_commands.describe(prompt="Описание видео (на английском для лучшего качества)")
async def generate_video(interaction: discord.Interaction, prompt: str):
    if not video_gen.available:
        await interaction.response.send_message("❌ Видео-генерация отключена (нет FAL.ai ключа)", ephemeral=True)
        return

    await interaction.response.defer()

    status = await interaction.followup.send(
        embed=discord.Embed(title="🎬 Генерация видео...", description=f"**Промпт:** {prompt[:100]}...", color=0xff6b6b)
    )

    filepath = await video_gen.generate(prompt, interaction.user.id)

    if filepath and os.path.exists(filepath):
        file_size = os.path.getsize(filepath) / (1024*1024)  # MB
        if file_size > 8:  # Discord limit 8MB for non-boosted
            await status.edit(embed=discord.Embed(title="❌ Видео слишком большое (>8MB)", color=0xe74c3c))
            return

        with open(filepath, "rb") as f:
            video_file = discord.File(f, filename="video.mp4")

        embed = discord.Embed(title="🎬 Видео сгенерировано!", color=0x2ecc71)
        embed.set_video(url="attachment://video.mp4")  # Discord не показывает превью видео в эмбеде, но файл прикрепится
        embed.add_field(name="Промпт", value=prompt, inline=False)

        await status.edit(embed=embed, attachments=[video_file])
    else:
        await status.edit(embed=discord.Embed(title="❌ Ошибка генерации видео", description="Попробуй позже или упрости промпт.", color=0xe74c3c))

@app_commands.command(name="enhance_video", description="AI улучшит промпт для видео, потом сгенерирует")
@app_commands.describe(idea="Короткая идея видео")
async def enhance_video(interaction: discord.Interaction, idea: str):
    # Аналогично enhance_image, но для видео
    await interaction.response.defer()

    status = await interaction.followup.send(embed=discord.Embed(title="✨ Улучшаю промпт для видео...", description=idea, color=0x3498db))

    enhance_prompt = f"Create a highly detailed, cinematic video prompt (80–150 words) in English for Pika Labs. Topic: {idea}. Include camera movements, lighting, style, mood, actions."

    enhanced = await ai_client.generate(enhance_prompt, interaction.user.id, mode="helpful")

    await status.edit(embed=discord.Embed(title="🎬 Генерация видео по улучшенному промпту...", description=f"``` {enhanced[:500]}... ```", color=0xf39c12))

    filepath = await video_gen.generate(enhanced, interaction.user.id)
