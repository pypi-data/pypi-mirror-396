import re
from typing import Optional, Union, List
from .message import Message

def maybe_instance(f):
    return f() if isinstance(f, type) else f

class FilterMeta(type):
    def __and__(cls, other):
        return AndFilter(maybe_instance(cls), maybe_instance(other))

    def __rand__(cls, other):
        return AndFilter(maybe_instance(other), maybe_instance(cls))

    def __or__(cls, other):
        return OrFilter(maybe_instance(cls), maybe_instance(other))

    def __ror__(cls, other):
        return OrFilter(maybe_instance(other), maybe_instance(cls))

    def __invert__(cls):
        return NotFilter(maybe_instance(cls))


class Filter(metaclass=FilterMeta):
    async def check(self, update):
        raise NotImplementedError

    async def __call__(self, message: Message) -> bool:
        return await self.check(message)

    def __and__(self, other):
        return AndFilter(maybe_instance(self), maybe_instance(other))

    def __rand__(self, other):
        return AndFilter(maybe_instance(other), maybe_instance(self))

    def __or__(self, other):
        return OrFilter(maybe_instance(self), maybe_instance(other))

    def __ror__(self, other):
        return OrFilter(maybe_instance(other), maybe_instance(self))

    def __invert__(self):
        instance = self() if isinstance(self, type) else self
        return NotFilter(instance)


class AndFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    async def check(self, update: Message) -> bool:
        for f in self.filters:
            if isinstance(f, type):  # اگر کلاس دادیم
                f = f()
            if not await f.check(update):
                return False
        return True


class OrFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    async def check(self, update):
        for f in self.filters:
            if isinstance(f, type):
                f = f()
            if await f.check(update):
                return True
        return False


class NotFilter(Filter):
    def __init__(self, f: Filter):
        self.f = f if not isinstance(f, type) else f()

    async def check(self, update):
        return not await self.f.check(update)



class text(Filter):
    """
    Filter برای بررسی محتوای متنی پیام.

    این فیلتر می‌تواند پیام‌ها را بر اساس:
    - وجود هر متن (اگر هیچ مقداری داده نشود).
    - یک رشته‌ی دقیق.
    - یک الگوی regex.

    Args:
        text (str, optional): رشته‌ی دقیق یا الگوی regex برای match.
        regex (bool): اگر True باشد، `text` به عنوان regex استفاده می‌شود.

    Returns:
        bool: اگر متن پیام با معیار داده شده match کند، True برمی‌گرداند.
    """

    def __init__(self, text: Optional[str] = None, regex: bool = False):
        self.text = text
        self.regex = regex
        self._compiled = re.compile(text) if regex and text else None

    async def check(self, message: Message) -> bool:
        msg_text = message.room_message.message
        if not msg_text:
            return False

        if not self.text:
            return True

        if self.regex and self._compiled:
            return bool(self._compiled.match(msg_text))

        return msg_text == self.text

class commands(Filter):
    """
    Advanced filter for detecting bot commands (e.g. /start, !help, test).

    Features:
        - Supports multiple command prefixes (default: / and !).
        - Case-insensitive option.
        - Matches both exact commands and commands with arguments.
        - Supports single or multiple commands.

    Args:
        commands (Union[str, List[str]]): Command or list of commands (without prefix).
        prefixes (List[str], optional): Allowed prefixes (default: ["/", "!"]).
        case_sensitive (bool, optional): Whether command matching is case-sensitive. Default False.
        allow_no_prefix (bool, optional): If True, matches commands even without prefix. Default False.

    Example:
        >>> @bot.on_message(commands("start"))
        ... async def handle_start(msg: Message):
        ...     await msg.reply("Welcome to the bot!")

        >>> @bot.on_message(commands(["help", "about"], prefixes=["/", ".", "!"]))
        ... async def handle_help(msg: Message):
        ...     await msg.reply("Help/About detected!")

        >>> @bot.on_message(commands("test", allow_no_prefix=True))
        ... async def handle_test(msg: Message):
        ...     await msg.reply("Matched with or without prefix")
    """

    def __init__(
        self,
        commands: Union[str, List[str]],
        prefixes: List[str] = ["/", "!"],
        case_sensitive: bool = False,
        allow_no_prefix: bool = False,
    ):
        self.commands = [commands] if isinstance(commands, str) else commands
        self.prefixes = prefixes
        self.case_sensitive = case_sensitive
        self.allow_no_prefix = allow_no_prefix

        if not case_sensitive:
            self.commands = [cmd.lower() for cmd in self.commands]

    async def check(self, message: Message) -> bool:
        # گرفتن متن پیام از ساختار اصلی
        msg_text = message.room_message.message
        if not msg_text:
            return False

        # آماده‌سازی متن برای مقایسه
        check_text = msg_text if self.case_sensitive else msg_text.lower()

        # جدا کردن دستور از آرگومان‌ها
        parts = check_text.split(maxsplit=1)
        command_part = parts[0]

        # بررسی با prefixها
        for cmd in self.commands:
            for prefix in self.prefixes:
                if command_part == f"{prefix}{cmd}" or command_part.startswith(f"{prefix}{cmd}"):
                    return True

            # اجازه‌ی match بدون prefix
            if self.allow_no_prefix and (command_part == cmd or command_part.startswith(cmd)):
                return True

        return False

class room_id(Filter):
    def __init__(self, room_id: Union[List[str], str]):
        self.room_ids = [room_id] if isinstance(room_id, str) else room_id
    
    async def check(self, message: Message) -> bool:
        return message.room_id in self.room_ids

class user_id(Filter):
    def __init__(self, user_id: Union[List[str], str]):
        self.user_ids = [user_id] if isinstance(user_id, str) else user_id
    
    async def check(self, message: Message) -> bool:
        return message.room_message.author.user.user_id in self.user_ids

class private(Filter):
    def __init__(self, add_action_ids: List[str] =None):
        self.private_action_ids = (add_action_ids or []) + [str(i) for i in range(200, 210)] + [str(i) for i in range(30200, 30210)]

    async def check(self, message: Message) -> bool:
        return message.action_id in self.private_action_ids

class group(Filter):
    def __init__(self, add_action_ids: List[str] =None):
        self.group_action_ids = (add_action_ids or []) + [str(i) for i in range(300, 329)] + [str(i) for i in range(30300, 30329)]

    async def check(self, message: Message) -> bool:
        return message.action_id in self.group_action_ids

class channel(Filter):
    def __init__(self, add_action_ids: List[str] =None):
        self.channel_action_ids = (add_action_ids or []) + [str(i) for i in range(400, 427)] + [str(i) for i in range(30400, 30427)]

    async def check(self, message: Message) -> bool:
        return message.action_id in self.channel_action_ids

class action_id():
    def __init__(self, action_ids: List[str]):
        self.action_ids = action_ids
    async def check(self, message: Message) -> bool:
        return message.action_id in self.action_ids

class replied():
    async def check(self, message: Message) -> bool:
        return bool(message.room_message.reply_to)
    
class has_file():
    async def check(self, message: Message) -> bool:
        return bool(message.room_message.attachment) or bool(message.room_message.forward_from.attachment)

class file:
    async def check(self, message: Message) -> bool:
        allowed_mimes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip",
            "application/vnd.rar",
            "audio/wav",
            "audio/x-wav",
            "application/vnd.android.package-archive",
        ]

        file_mime = message.room_message.attachment.mime or message.room_message.forward_from.attachment.mime

        return file_mime in allowed_mimes if file_mime else False
    
class photo():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type

        return message_type in ["IMAGE" ,"IMAGE_TEXT"] if message_type else False

class video():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type

        return message_type in ["VIDEO" ,"VIDEO_TEXT"] if message_type else False

class music():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type
        return message_type in ["AUDIO" ,"AUDIO_TEXT"] if message_type else False

class voice():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type
        return message_type in ["VOICE" ,"VOICE_TEXT"] if message_type else False
    
class gif():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type
        return message_type in ["GIF" ,"GIF_TEXT"] if message_type else False

class forward():
    async def check(self, message: Message) -> bool:
        return bool(message.room_message.forward_from)
    
class location():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type
        return message_type in ["LOCATION" ,"LOCATION_TEXT"] if message_type else False

class contact():
    async def check(self, message: Message) -> bool:
        message_type = message.room_message.message_type or message.room_message.forward_from.message_type
        return message_type in ["CONTACT" ,"CONTACT_TEXT"] if message_type else False

class button_value():
    def __init__(self, button_ids: Optional[str | List[str]] = None):
        self.button_ids = [button_ids] if isinstance(button_ids, str) else button_ids
    async def check(self, message: Message) -> bool:
        value_id = message.room_message.additional_data.value
        if value_id and self.button_ids is None: return True
        return value_id in self.button_ids if value_id else False
    
class button_label():
    def __init__(self, button_labels: Optional[str | List[str]] = None):
        self.button_labels = [button_labels] if isinstance(button_labels, str) else button_labels
    async def check(self, message: Message) -> bool:
        label_text = message.room_message.additional_data.label
        return label_text in self.button_labels if label_text else False

class button_contact():
    async def check(self, message: Message) -> bool:
        phone = str(message.room_message.additional_data.value)
        return phone.isdigit() and len(phone) == 12 if phone else False

class button_action_type():
    def __init__(self, button_actions: List[int]):
        self.button_actions = [button_actions] if isinstance(button_actions, str) else button_actions
    async def check(self, message: Message) -> bool:
        action_type = message.room_message.additional_data.action_type
        return action_type in self.button_actions if action_type else False