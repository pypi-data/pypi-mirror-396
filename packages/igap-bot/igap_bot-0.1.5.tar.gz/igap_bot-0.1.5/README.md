<p align="center">
  <a href="https://github.com/sinyor-ehsan/igap-bot">
    <img src="https://logoyab.com/wp-content/uploads/2024/08/I-Gap-Logo-1030x1030.png" width="128" alt="igap-bot Logo" />
  </a>
  <br><br>
  <strong><font size="+2">igap-bot</font></strong><br>
  <em>python Library for iGap Bot</em>
  <br><br>
  <a href="https://github.com/sinyor-ehsan/igap-bot">🏠 Homepage</a> •
  <a href="https://github.com/sinyor-ehsan/igap-bot">📘 Documentation</a> •
  <a href="https://pypi.org/project/igap-bot/#history">📦 Releases</a> •
</p>

---

## 🌟 igap-bot

> **Reliable. Scalable. Pythonic.**
> A robust interface to build and manage iGap bots — with full support for **automation interactions**.

---

### 🚀 Async Example
```python
from igap_bot.bot import BotClient, filters, Message

bot = BotClient("YOUR_TOKEN")

@bot.on_message()
async def get_message(message: Message):
    await bot.send_message(message.room_id, "Hello from iGap Bot!")

bot.run()
```

### 🚀 send keyboard
```python
from igap_bot.bot import BotClient, filters, Message
from igap_bot.bot.button import Button, ButtonRow, ButtonKeyboard, ActionTypeEnum, AdditionalTypeEnum

bot = BotClient("YOUR_TOKEN")

@bot.on_message(filters.text(text="دکمه", regex=True))
async def send_button(message: Message):
    keyboard = ButtonKeyboard(
        rows=[
            # ردیف اول
            ButtonRow(
                buttons=[
                    Button(action_type=ActionTypeEnum.REQUEST_PHONE, label="ارسال شماره تلفن", value="phone"),
                    Button(action_type=ActionTypeEnum.BOT_ACTION, label="آیگپ بات 1", value="iGap-bot1")
                ]
            ),
            # ردیف دوم
            ButtonRow(buttons=[Button(action_type=ActionTypeEnum.BOT_ACTION, label="آیگپ بات 2", value="iGap-bot2")]),
        ]
    )

    await message.reply_message("send keyboard!", additional_type=AdditionalTypeEnum.UNDER_MESSAGE_BUTTON, additional_data=keyboard)

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
    
bot.run()
```

### ⚡ Registering a handler for edited messages.
```python
from igap_bot.bot import BotClient, filters, Message

@bot.on_edit_message()
async def get_message(message: Message):
    message_id = message["messageId"]
    await bot.send_message(message.room_id, "پیام را ویرایش کردید!", reply_to_message_id=message_id)

bot.run()
```

---

### 🚀 Why igap-bot?

- 📦 **Instant Setup** — Get started right after `pip install`
- 🧠 **Beginner-Friendly** — Simple, intuitive, and Pythonic by design
- 💅 **Elegant** — Hide the complexity, focus on clean code
- 🔁 **Async Native** — Built with async at its core, sync supported too
- 💪 **Feature-Rich** — Unlock all official client capabilities — plus extra powers

---

### 📦 Installation

```bash
pip install -U igap-bot
```

---

### 📣 Stay Connected

- [iGap Channel](https://iGap.net/iGhap1Bot1)
- [Project Homepage](https://github.com/sinyor-ehsan/igap-bot)

