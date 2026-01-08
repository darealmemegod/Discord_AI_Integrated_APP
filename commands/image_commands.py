import discord
from discord import app_commands
from services.image_generator import ImageGenerator
from services.ai_client import AIClient
import os

image_gen = ImageGenerator()
ai_client = AIClient()

@app_commands.command(name="generate_image", description="Сгенерировать изображение по описанию")
@app_commands.describe(prompt="Подробное описание изображения")
async def generate_image(interaction: discord.Interaction, prompt: str):
    if not image_gen.available:
        await interaction.response.send_message(
            "❌ Генерация изображений отключена (нет API-ключа Stability AI)",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    status = await interaction.followup.send(
        embed=discord.Embed(title="🎨 Генерация изображения...", description=f"**Промпт:** {prompt[:100]}...", color=0x9b59b6)
    )

    filepath = await image_gen.generate(prompt, interaction.user.id)

    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as f:
            file = discord.File(f, filename="image.png")

        embed = discord.Embed(title="🎨 Изображение сгенерировано!", color=0x2ecc71)
        embed.set_image(url="attachment://image.png")
        embed.add_field(name="Промпт", value=prompt, inline=False)
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}")

        await status.edit(embed=embed, attachments=[file])
    else:
        await status.edit(
            embed=discord.Embed(
                title="❌ Ошибка генерации",
                description="Не удалось сгенерировать изображение. Попробуй позже или упрости промпт.",
                color=0xe74c3c
            )
        )

@app_commands.command(name="enhance_image", description="AI улучшит твой промпт, потом сгенерирует изображение")
@app_commands.describe(idea="Короткая идея (например: кот в космосе)")
async def enhance_image(interaction: discord.Interaction, idea: str):
    if not image_gen.available:
        await interaction.response.send_message(
            "❌ Генерация изображений отключена (нет API-ключа)",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    status = await interaction.followup.send(
        embed=discord.Embed(title="✨ Улучшаю промпт...", description=f"**Идея:** {idea}", color=0x3498db)
    )

    # Шаг 1: Пусть Mistral сделает крутой подробный промпт
    enhance_prompt = f"""
Ты — эксперт по созданию промптов для генерации изображений.
Создай ОЧЕНЬ подробный, профессиональный промпт (100–200 слов) на английском для Stable Diffusion.
Тема: {idea}

Включи:
- стиль (photorealistic, digital art, oil painting и т.д.)
- освещение, композицию, цвета
- детали фона, переднего плана
- качество: 8k, highly detailed, masterpiece

Промпт только текстом, без кавычек и объяснений.
"""

    enhanced = await ai_client.generate(enhance_prompt, interaction.user.id, mode="helpful")
    enhanced = enhanced.strip()

    await status.edit(
        embed=discord.Embed(
            title="🎨 Генерация по улучшенному промпту...",
            description=f"**Идея:** {idea}\n**Улучшенный промпт:** ```{enhanced[:500]}...```",
            color=0xf39c12
        )
    )

    # Шаг 2: Генерация
    filepath = await image_gen.generate(enhanced, interaction.user.id)

    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as f:
            file = discord.File(f, filename="enhanced.png")

        embed = discord.Embed(title="✨ Изображение сгенерировано с улучшенным промптом!", color=0x2ecc71)
        embed.add_field(name="Твоя идея", value=idea, inline=False)
        embed.add_field(name="Улучшенный промпт", value=f"```{enhanced[:1024]}```", inline=False)
        embed.set_image(url="attachment://enhanced.png")
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}")

        await status.edit(embed=embed, attachments=[file])
    else:
        await status.edit(
            embed=discord.Embed(
                title="❌ Ошибка генерации",
                description="Не удалось сгенерировать изображение.",
                color=0xe74c3c
            )
        )