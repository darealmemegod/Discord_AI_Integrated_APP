import discord
from discord import app_commands
from services.ai_client import AIClient

ai_client = AIClient()

@app_commands.command(name="ask", description="Саркастичный и грубый ответ от RudeGPT")
@app_commands.describe(question="Твой вопрос или сообщение")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    response = await ai_client.generate(question, interaction.user.id, mode="rude")

    embed = discord.Embed(
        title="😈 RudeGPT отвечает",
        description=response[:4096],  # Discord limit
        color=0xe74c3c
    )
    embed.set_footer(text=f"Запрошено: {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)


@app_commands.command(name="ask_helpful", description="Подробный и полезный ответ от AI")
@app_commands.describe(question="Твой вопрос или сообщение")
async def ask_helpful(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    response = await ai_client.generate(question, interaction.user.id, mode="helpful")

    embed = discord.Embed(
        title="🤓 Полезный AI отвечает",
        description=response[:4096],
        color=0x2ecc71
    )
    embed.set_footer(text=f"Запрошено: {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)