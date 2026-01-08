import discord
from discord import app_commands
from services.web_search import WebSearchService

search_service = WebSearchService()

@app_commands.command(name="search", description="Поиск в интернете с фильтрами")
@app_commands.describe(
    query="Что искать",
    time="Временной диапазон",
    safe="Безопасный поиск",
    region="Регион/язык"
)
@app_commands.choices(
    time=[
        app_commands.Choice(name="Любое время", value="any"),  # Используем строку вместо None
        app_commands.Choice(name="День", value="day"),
        app_commands.Choice(name="Неделя", value="week"),
        app_commands.Choice(name="Месяц", value="month"),
        app_commands.Choice(name="Год", value="year"),
    ],
    safe=[
        app_commands.Choice(name="Выключен", value="0"),
        app_commands.Choice(name="Умеренный", value="1"),
        app_commands.Choice(name="Строгий", value="2"),
    ],
    region=[
        app_commands.Choice(name="Все языки", value="all"),
        app_commands.Choice(name="Русский", value="ru"),
        app_commands.Choice(name="Английский", value="en"),
        app_commands.Choice(name="Немецкий", value="de"),
        app_commands.Choice(name="Французский", value="fr"),
        app_commands.Choice(name="Испанский", value="es"),
    ]
)
async def search(
    interaction: discord.Interaction,
    query: str,
    time: str = "any",  # По умолчанию строка "any"
    safe: str = "1",
    region: str = "all"
):
    """Поиск в интернете через SearXNG"""
    await interaction.response.defer(thinking=True)
    
    try:
        # Конвертируем "any" в None для SearXNG
        time_range = None if time == "any" else time
        
        # Выполняем поиск
        result = await search_service.search(
            query=query,
            safesearch=safe,
            time_range=time_range,
            language=region
        )
        
        # Создаем embed с результатами
        embed = discord.Embed(
            title=f"🔍 Результаты поиска: {query}",
            color=0x5865F2
        )
        
        # Добавляем информацию о фильтрах в описание
        filters_text = []
        if time_range:
            time_map = {"day": "день", "week": "неделя", "month": "месяц", "year": "год"}
            filters_text.append(f"**Время:** {time_map.get(time_range, time_range)}")
        
        safe_map = {"0": "выключен", "1": "умеренный", "2": "строгий"}
        filters_text.append(f"**Безопасный поиск:** {safe_map.get(safe, safe)}")
        
        if region != "all":
            lang_map = {"ru": "русский", "en": "английский", "de": "немецкий", 
                       "fr": "французский", "es": "испанский"}
            filters_text.append(f"**Язык:** {lang_map.get(region, region)}")
        
        # Добавляем фильтры в начало результата
        if filters_text:
            filters_section = "📊 **Фильтры:** " + " | ".join(filters_text) + "\n\n"
            full_result = filters_section + result
        else:
            full_result = result
        
        # Проверяем длину и отправляем
        if len(full_result) > 4096:
            # Обрезаем до допустимой длины
            full_result = full_result[:4090] + "..."
        
        embed.description = full_result
        
        await interaction.followup.send(embed=embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Ошибка поиска",
            description=f"Произошла ошибка при поиске:\n```{str(e)[:200]}```",
            color=0xFF0000
        )
        await interaction.followup.send(embed=error_embed)