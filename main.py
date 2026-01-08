import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from services.ai_client import AIClient
from services.tts_service import TTSService
from services.web_search import WebSearchService
from core.logger import logger
from commands.image_commands import generate_image, enhance_image
from commands.tts_commands import tts_chat

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ai = AIClient()
tts = TTSService()
search = WebSearchService()

@bot.event
async def on_ready():
    logger.info(f"{bot.user} готов!")
    await bot.tree.sync()
    logger.info("Команды синхронизированы")

# Регистрация команд
from commands.ai_commands import ask, ask_helpful
from commands.search_commands import search
from commands.info_commands import status, help_cmd
from commands.video_commands import generate_video, enhance_video


bot.tree.add_command(ask)
bot.tree.add_command(ask_helpful)
bot.tree.add_command(tts_chat)
bot.tree.add_command(search)
bot.tree.add_command(status)
bot.tree.add_command(help_cmd)
bot.tree.add_command(generate_image)
bot.tree.add_command(enhance_image)
bot.tree.add_command(generate_video)
bot.tree.add_command(enhance_video)

bot.run(DISCORD_TOKEN)