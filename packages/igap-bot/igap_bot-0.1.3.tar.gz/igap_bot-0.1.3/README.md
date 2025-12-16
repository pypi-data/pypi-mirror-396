# igap-bot

Unofficial Python client for iGap Bot API.

## Installation
```bash
pip install igap-bot

Usage

from igap_bot.bot import BotClient, filters, Message

bot = BotClient(token="YOUR_TOKEN")

# ساده‌ترین حالت: پاسخ به هر پیام
@bot.on_message()
async def handle_message(message: Message):
    await bot.send_message(message.room_id, "Hello from iGap bot!")

# استفاده از فیلتر: فقط وقتی پیام کامند /start باشه
@bot.on_message(filters.commands("/start"))
async def handle_start(message: Message):
    await bot.send_message(message.room_id, "Welcome! Your bot is ready 🚀")

bot.run()


Features
• 	Async client using 
• 	Message handling with filters
• 	File upload support
• 	Extensible architecture
License
MIT