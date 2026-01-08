This Discord bot runs off a local AI by default, but you can switch it to any cloud AI, e.g., GPT-5.2.

It currently supports:

Text generation via your chosen AI

Image generation using Stable Diffusion

Voice output via Edge TTS

A video-generation module (e.g., Sora 2) is included in the code, but I haven’t tested it due to budget constraints.

Setup

Install the required packages:

pip install -r requirements.txt


Create an .env file based on .env_example and add your AI keys.

Launch the bot on your server.

Development

The code is modular and designed for easy expansion.

Recommended: read through the code to understand the structure before adding new features.

WARNING: the ai is configured to be rude and unhelpful, in the ai_client.py you shall customise it as you wish



Этот Discord-бот работает на локальном ИИ по умолчанию, но его можно переключить на любой облачный ИИ, например GPT-5.2.

Поддерживает:

Генерацию текста через выбранный ИИ

Генерацию изображений через Stable Diffusion

Озвучку текста через Edge TTS

Модуль генерации видео (например, Sora 2) есть в коде, но я не тестировал его из-за отсутствия бюджета.

Установка

Установите зависимости:

pip install -r requirements.txt


Создайте файл .env на основе .env_example и добавьте туда ключи ваших ИИ.

Запустите бота на сервере.

Разработка

Код модульный и легко расширяемый.

Рекомендую сначала прочитать код, чтобы понять структуру, перед добавлением новых функций

ВНИМАНИЕ: ИИ настроен на очень грубое общение и быть безполезным, в файле ai_client.py вы можете изменить параметры разговора ИИ
