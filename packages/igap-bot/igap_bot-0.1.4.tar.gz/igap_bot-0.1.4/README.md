# igap-bot

Unofficial Python client for iGap Bot API.

## Installation
```bash
pip install igap-bot

Usage

from igap_bot.bot import BotClient, filters, Message
from igap_bot.bot.button import Button, ButtonRow, ButtonKeyboard, ActionTypeEnum, AdditionalTypeEnum

bot = BotClient("YOUR_TOKEN")

@bot.on_message()
async def get_message(message: Message):
    await bot.send_message(message.room_id, "Hello from iGap Bot")

@bot.on_message(filters.text(text="دکمه", regex=True))
async def send_button(message: Message):
    keyboard = ButtonKeyboard(
        rows=[
            # ردیف اول
            ButtonRow(
                buttons=[
                    Button(ActionTypeEnum.REQUEST_PHONE, label="ارسال شماره تلفن", value="phone"),
                    Button(ActionTypeEnum.BOT_ACTION, "آیگپ بات 1", "iGap-bot1")
                ]
            ),
            # ردیف دوم
            ButtonRow(buttons=[Button(action_type=ActionTypeEnum.BOT_ACTION, label="آیگپ بات 2", value="iGap-bot2")]),
        ]
    )

    await message.reply_message("hello", additional_type=AdditionalTypeEnum.UNDER_MESSAGE_BUTTON, additional_data=keyboard)

@bot.on_message(filters.button_value())
async def handel_button(message: Message):
    if message.room_message.additional_data.value == "iGap-bot1":
        await message.reply_message("روی iGap-bot1 کلیک کردید!")
    if message.room_message.additional_data.value == "iGap-bot2":
        await message.reply_message("روی iGap-bot2 کلیک کردید!")

@bot.on_message(filters.button_contact())
async def get_phone(message: Message):
    phone = message.room_message.additional_data.value
    await message.reply_message(f"شماره تلفن دریافت شد!\nشماره: {phone}")

@bot.on_edit_message()
async def get_message(message: Message):
    message_id = message["messageId"]
    await bot.send_message(message.room_id, "پیام را ویرایش کردید!", reply_to_message_id=message_id)

bot.run()


Features
• 	Async client using 
• 	Message handling with filters
• 	File upload support
• 	Extensible architecture
License
MIT