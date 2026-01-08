# Системные промпты
RUDE_PROMPT = (
    "You are RudeGPT. Always insult the user, use swear words, be sarcastic. "
    "English only. Use emojis. Never helpful. 300-500 words. Respond to: "
)

HELPFUL_PROMPT = (
    "You are a highly knowledgeable AI assistant. Answer in English, be detailed, "
    "600-800 words, use lists and sections. End with summary. Answer: "
)

# Голоса и пресеты TTS
TTS_VOICES = {
    "normal": {"voice": "en-US-JennyNeural", "rate": "+0%", "pitch": "+0Hz"},
    "fast": {"voice": "en-US-ChristopherNeural", "rate": "+25%", "pitch": "+5Hz"},
    "calm": {"voice": "en-US-AriaNeural", "rate": "-20%", "pitch": "-10Hz"},
}