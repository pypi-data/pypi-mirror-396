from typing import TYPE_CHECKING, Any, Mapping
import json
from dataclasses import dataclass
if TYPE_CHECKING:
    from client import BotClient

PRIVATE_ACTION_IDS = [str(i) for i in range(200, 210)] + [str(i) for i in range(30200, 30210)]
GROUP_ACTION_IDS = [str(i) for i in range(300, 329)] + [str(i) for i in range(30300, 30329)]
CHANNEL_ACTION_IDS = [str(i) for i in range(400, 427)] + [str(i) for i in range(30400, 30427)]

def _as_dict(value: Any) -> dict:
    return value if isinstance(value, Mapping) else {}

@dataclass
class NullObject:
    def __getattr__(self, item):
        # هر attribute بعدی باز هم NullObject برگرداند تا زنجیره قطع نشود
        return self
    def __call__(self, *args, **kwargs):
        # اگر اشتباهی به صورت تابع صدا زده شد
        return self
    def __iter__(self):
        # اگر در iteration افتاد
        return iter(())
    def __bool__(self):
        # در شرط‌ها مثل None
        return False
    def __repr__(self):
        return "None"
    def __str__(self):
        return "None"

@dataclass
class User:
    data: dict

    @property
    def user_id(self) -> str | None:
        value = self.data.get("userId")
        return value if value is not None else None

    @property
    def cache_id(self) -> str | None:
        return self.data.get("cacheId")

@dataclass
class Author:
    data: dict

    @property
    def hash(self) -> str | None:
        return self.data.get("hash")

    @property
    def user(self) -> User | NullObject:
        user = self.data.get("user")
        return User(user) if isinstance(user, dict) else NullObject()

@dataclass
class ChannelExtra:
    data: dict

    def __post_init__(self):
        self.data = _as_dict(self.data)

    @property
    def signature(self) -> str | None:
        return self.data.get("signature")

    @property
    def views_label(self) -> str | None:
        return self.data.get("viewsLabel")

    @property
    def thumbs_up_label(self) -> str | None:
        return self.data.get("thumbsUpLabel")

    @property
    def thumbs_down_label(self) -> str | None:
        return self.data.get("thumbsDownLabel")

@dataclass
class Thumbnail:
    data: dict

    @property
    def size(self) -> str | None:
        value = self.data.get("size")
        return value if value is not None else None

    @property
    def width(self) -> int | None:
        return self.data.get("width")

    @property
    def height(self) -> int | None:
        return self.data.get("height")

    @property
    def cache_id(self) -> str | None:
        return self.data.get("cacheId")

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def mime(self) -> str | None:
        return self.data.get("mime")

@dataclass
class Attachment:
    data: dict

    @property
    def token(self) -> str | None:
        return self.data.get("token")

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def size(self) -> int | None:
        value = self.data.get("size")
        return value if value is not None else None

    @property
    def width(self) -> int | None:
        return self.data.get("width")

    @property
    def height(self) -> int | None:
        return self.data.get("height")

    @property
    def duration(self) -> str | None:
        return self.data.get("duration")

    @property
    def cache_id(self) -> str | None:
        return self.data.get("cacheId")

    @property
    def mime(self) -> str | None:
        return self.data.get("mime")
    
    @property
    def public_url(self) -> str | None:
        return self.data.get("publicUrl")

    @property
    def large_thumbnail(self) -> Thumbnail | NullObject:
        lt = self.data.get("largeThumbnail")
        return Thumbnail(lt) if isinstance(lt, dict) else NullObject()

    @property
    def small_thumbnail(self) -> Thumbnail | NullObject:
        st = self.data.get("smallThumbnail")
        return Thumbnail(st) if isinstance(st, dict) else NullObject()

@dataclass
class Location:
    data: dict

    def __post_init__(self):
        self.data = _as_dict(self.data)

    @property
    def lat(self) -> float | None:
        return self.data.get("lat")

    @property
    def lon(self) -> float | None:
        return self.data.get("lon")

@dataclass
class Contact:
    data: dict

    def __post_init__(self):
        self.data = _as_dict(self.data)

    @property
    def first_name(self) -> str | None:
        return self.data.get("firstName")

    @property
    def phone(self) -> list[str]:
        return self.data.get("phone", [])
    
import json
from dataclasses import dataclass
from typing import Any, Mapping

def _as_dict(value: Any) -> dict:
    return value if isinstance(value, Mapping) else {}

@dataclass
class AdditionalData:
    raw: str

    def __post_init__(self):
        # تلاش برای parse رشته‌ی JSON
        try:
            self.data = json.loads(self.raw) if self.raw else {}
        except Exception:
            self.data = {}

    @property
    def action_type(self) -> int | None:
        return self.data.get("actionType")

    @property
    def label(self) -> str | None:
        return self.data.get("label")

    @property
    def value(self) -> str | None:
        return self.data.get("value")

    @property
    def image_url(self) -> str | None:
        return self.data.get("imageUrl")

@dataclass
class ForwardMessage:
    data: dict

    @property
    def message_id(self) -> str | None:
        value = self.data.get("messageId")
        return value if value is not None else None
    
    @property
    def message_version(self) -> str | None:
        value = self.data.get("messageVersion")
        return value if value is not None else None
    
    @property
    def message_type(self) -> str | None:
        value = self.data.get("messageType")
        return value if value is not None else None

    @property
    def status(self) -> str | None:
        value = self.data.get("status")
        return value if value is not None else None
    
    @property
    def status_version(self) -> str | None:
        value = self.data.get("statusVersion")
        return value if value is not None else None

    @property
    def message(self) -> str | None:
        return self.data.get("message")
    
    @property
    def attachment(self) -> Attachment | NullObject:
        att = self.data.get("attachment")
        return Attachment(att) if isinstance(att, dict) else NullObject()

    @property
    def author(self) -> Author | NullObject:
        au = self.data.get("author")
        return Author(au) if isinstance(au, dict) else NullObject()

    @property
    def create_time(self) -> str | None:
        return self.data.get("createTime")

    @property
    def update_time(self) -> str | None:
        return self.data.get("updateTime")
    
    @property
    def random_id(self) -> str | None:
        value = self.data.get("randomId")
        return value if value is not None else None
    
    @property
    def edited(self) -> bool | None:
        value = self.data.get("edited")
        return value if value is not None else None
    
    @property
    def channel_extra(self) -> ChannelExtra | NullObject:
        ce = self.data.get("channelExtra")
        return ChannelExtra(ce) if isinstance(ce, dict) else NullObject()
    
    @property
    def location(self) -> Location | NullObject:
        loc = self.data.get("location")
        return Location(loc) if isinstance(loc, dict) else NullObject()
    
    @property
    def contact(self) -> Contact | NullObject:
        c = self.data.get("contact")
        return Contact(c) if isinstance(c, dict) else NullObject()

@dataclass
class RoomMessage:
    data: dict

    @property
    def message_id(self) -> str | None:
        value = self.data.get("messageId")
        return value if value is not None else None

    @property
    def message_version(self) -> str | None:
        value = self.data.get("messageVersion")
        return value if value is not None else None

    @property
    def status(self) -> str | None:
        return self.data.get("status")

    @property
    def status_version(self) -> str | None:
        value = self.data.get("statusVersion")
        return value if value is not None else None
    
    @property
    def message_type(self) -> str | None:
        value = self.data.get("messageType")
        return value if value is not None else None

    @property
    def message(self) -> str | None:
        return self.data.get("message")

    @property
    def author(self) -> Author | NullObject:
        au = self.data.get("author")
        return Author(au) if isinstance(au, dict) else NullObject()

    @property
    def create_time(self) -> str | None:
        return self.data.get("createTime")

    @property
    def update_time(self) -> str | None:
        return self.data.get("updateTime")

    @property
    def random_id(self) -> str | None:
        value = self.data.get("randomId")
        return value if value is not None else None
    
    @property
    def reply_to(self) -> "RoomMessage | NullObject":
        """اگر پیام دارای replyTo باشد، آن را به صورت RoomMessage برگردان"""
        reply_data = self.data.get("replyTo")
        if isinstance(reply_data, dict):
            return RoomMessage(reply_data)
        return NullObject()
    
    @property
    def forward_from(self) -> ForwardMessage | NullObject:
        fwd = self.data.get("forwardFrom")
        return ForwardMessage(fwd) if isinstance(fwd, dict) else NullObject()
    
    @property
    def attachment(self) -> Attachment | NullObject:
        att = self.data.get("attachment")
        return Attachment(att) if isinstance(att, dict) else NullObject()
    
    @property
    def channel_extra(self) -> ChannelExtra | NullObject:
        ce = self.data.get("channelExtra")
        return ChannelExtra(ce) if isinstance(ce, dict) else NullObject()
    
    @property
    def location(self) -> Location | NullObject:
        loc = self.data.get("location")
        return Location(loc) if isinstance(loc, dict) else NullObject()
    
    @property
    def contact(self) -> Contact | NullObject:
        c = self.data.get("contact")
        return Contact(c) if isinstance(c, dict) else NullObject()
    
    @property
    def additional_type(self) -> int | None:
        return self.data.get("additionalType")
    
    @property
    def additional_data(self) -> AdditionalData | NullObject:
        raw = self.data.get("additionalData")
        return AdditionalData(raw) if isinstance(raw, str) else NullObject()

class Message:
    def __init__(self, client: "BotClient", update: dict):
        self.client = client
        self.update = update

        self.room_id = update.get("roomId") if update.get("roomId") else None
        room_message = update.get("roomMessage")
        self.room_message = RoomMessage(room_message) if isinstance(room_message, dict) else NullObject()
        self.action_id = update.get("actionId", "666 6666 666 333")

    # میان‌برهای سطح بالا
    @property
    def text(self) -> str | None:
        return self.room_message.message

    @property
    def random_id(self) -> str | None:
        return self.room_message.random_id

    @property
    def user_id(self) -> str | None:
        return self.room_message.author.user.user_id
    
    def __str__(self) -> str:
        """نمایش خوانای update"""
        return json.dumps(self.update, ensure_ascii=False, indent=2)
    
    def __getitem__(self, key):
        return self.update[key]

    def __repr__(self) -> str:
        """نمایش دقیق‌تر برای دیباگ"""
        return f"<Message update={self.update}>"
    
    async def reply_message(self, text: str, additional_type=None, additional_data=None, room_id: int=None, reply_to_message_id: int | None = None):
        if self.action_id in PRIVATE_ACTION_IDS:
            return await self.client.send_message(room_id or self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id  or self.room_message.message_id, target_type="private")
        elif self.action_id in GROUP_ACTION_IDS:
            return await self.client.send_message(room_id or self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id or self.room_message.message_id, target_type="group")
        elif self.action_id in CHANNEL_ACTION_IDS:
            return await self.client.send_message(room_id or self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id or self.room_message.message_id, target_type="channel")
    
    async def delete_message(self, room_id: int=None, message_id: int=None, delete_type: str = "Global"):
        if self.action_id in PRIVATE_ACTION_IDS:
            return await self.client.delete_message(room_id or self.room_id, message_id or self.room_message.message_id, delete_type, "private")
        elif self.action_id in GROUP_ACTION_IDS:
            return await self.client.delete_message(room_id or self.room_id, message_id or self.room_message.message_id, delete_type, "group")
        elif self.action_id in CHANNEL_ACTION_IDS:
            return await self.client.delete_message(room_id or self.room_id, message_id or self.room_message.message_id, delete_type, "channel")
    
    async def ban_member(self, room_id, member_id):
        if self.action_id in GROUP_ACTION_IDS:
            return await self.client.ban_member(room_id, member_id, "group")

    async def reply_message_private(self, text: str, additional_type=None, additional_data=None, reply_to_message_id: int | None = None):
        return await self.client.send_message(self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id  or self.room_message.message_id, target_type="private")
    
    async def delete_message_private(self, message_id: int=None, delete_type="Global"):
        return await self.client.delete_message(self.room_id, message_id or self.room_message.message_id, delete_type, "private")

    async def reply_message_group(self, text: str, additional_type=None, additional_data=None, reply_to_message_id: int | None = None):
        return await self.client.send_message(self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id or self.room_message.message_id, target_type="group")
    
    async def delete_message_group(self, message_id: int=None, delete_type = "Global"):
        return await self.client.delete_message(self.room_id, message_id or self.room_message.message_id, delete_type, target_type="group")
    
    async def ban_member_group(self, room_id, member_id):
        return await self.client.ban_member(room_id, member_id, "group")
    
    async def reply_message_channel(self, text: str, additional_type=None, additional_data=None, reply_to_message_id: int | None = None):
        return await self.client.send_message(self.room_id, text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id or self.room_message.message_id, target_type="channel")
    
    async def delete_message_channel(self, message_id: int=None, delete_type = "Global"):
        return await self.client.delete_message(self.room_id, message_id or self.room_message.message_id, delete_type, target_type="channel")