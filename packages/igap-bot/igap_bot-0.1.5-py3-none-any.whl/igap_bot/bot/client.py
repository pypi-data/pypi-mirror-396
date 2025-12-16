from .message import Message
from typing import Any, Callable, Tuple
from aiohttp import web
from .filters import Filter
from igap_bot.proto import (
    ChatSendMessage_pb2, ChatEditMessage_pb2, ChatUpdateStatus_pb2, GroupKickMember_pb2, GroupSendMessage_pb2,
    ChatGetRoom_pb2, GroupPinMessage_pb2, GroupEditMessage_pb2, FileUploadOption_pb2, FileUploadInit_pb2,
    FileUpload_pb2, FileUploadStatus_pb2, GroupChangeMemberRights_pb2, GroupUpdateStatus_pb2, GroupDeleteMessage_pb2,
    ChatDeleteMessage_pb2, GroupEdit_pb2, ChannelSendMessage_pb2, ChannelEditMessage_pb2, ChannelDeleteMessage_pb2)
from google.protobuf import json_format
import random, json, aiohttp, os, asyncio, uuid, mimetypes
from collections import deque
from PIL import Image

last_message_ids = deque(maxlen=20)

PRIVATE_ACTION_IDS = [str(i) for i in range(200, 210)] + [str(i) for i in range(30200, 30210)]
GROUP_ACTION_IDS = [str(i) for i in range(300, 329)] + [str(i) for i in range(30300, 30329)]
CHANNEL_ACTION_IDS = [str(i) for i in range(400, 427)] + [str(i) for i in range(30400, 30427)]

class BotClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/octet-stream"
        }
        self.data: dict = {}
        self.roomMessage = {}
        self.handlers = {}              # هندلرها
        self.message_wrapper = None     # پیام فعلی
        self.propagationStopped = False

    async def handle_post(self, request):
        # گرفتن داده‌ی خام
        raw_data = await request.read()
        print(f"{request.method} {request.path} {request.query}")
        
        action_id_map = {
            "30201": ChatSendMessage_pb2.ChatSendMessageResponse,
            "30202": ChatUpdateStatus_pb2.ChatUpdateStatusResponse,
            "30307": GroupKickMember_pb2.GroupKickMemberResponse,
            "30310": GroupSendMessage_pb2.GroupSendMessageResponse,
            "30311": GroupUpdateStatus_pb2.GroupUpdateStatusResponse,
            "30327": GroupChangeMemberRights_pb2.GroupChangeMemberRightsResponse,
            "30410": ChannelSendMessage_pb2.ChannelSendMessageResponse,
            "30203": ChatEditMessage_pb2.ChatEditMessageResponse,
            "30325": GroupEditMessage_pb2.GroupEditMessageResponse,
            "30425": ChannelEditMessage_pb2.ChannelEditMessageResponse
        }

        self.action_id = request.query.get("actionId")
        if self.action_id in action_id_map:
            self.data = self.decode_message(raw_data, action_id_map[self.action_id])
            # if self.action_id == "30203":print(f"response: {self.data}")

        # ذخیره برای استفاده در هندلرها
        self.roomMessage = self.data.get("roomMessage", {})
        self.data["actionId"] = self.action_id # اضافه کردن action_id به update 
        self.message_wrapper = Message(self, self.data)
        message_id = self.roomMessage.get("messageId")

        if not message_id in last_message_ids:
            last_message_ids.append(message_id)
            await self._dispatch_handlers()
            
        return web.Response(text="OK")

    def on_message(self, *filters) -> Callable:
        """
        Decorator برای ثبت هندلر پیام با فیلترهای اختیاری.
        تابعی که با این decorator تزئین می‌شود باید یک آرگومان از نوع Message دریافت کند.
        """
        def decorator(func: Callable):
            filter_key = str(uuid.uuid4())
            if filter_key not in self.handlers:
                self.handlers[filter_key] = []
            # ذخیره‌ی هندلر همراه با فیلترها و نوع
            self.handlers[filter_key].append({
                "filters": filters,
                "callback": func,
                "type": "message"
            })
            return func
        return decorator
    
    def on_member_rights_change(self) -> Callable:
        """
        Decorator برای ثبت هندلر تغییر دسترسی اعضا.
        تابعی که با این decorator تزئین می‌شود باید یک آرگومان از نوع Update یا MemberRights دریافت کند.
        """
        def decorator(func: Callable):
            filter_key = str(uuid.uuid4())
            if filter_key not in self.handlers:
                self.handlers[filter_key] = []
            # ذخیره‌ی هندلر همراه با نوع
            self.handlers[filter_key].append({
                "filters": (),   # اینجا معمولاً فیلتر خاصی نداریم
                "callback": func,
                "type": "member_rights"
            })
            return func
        return decorator
    
    def on_message_status_update(self, *filters) -> Callable:
        """
        Decorator برای ثبت هندلر تغییر وضعیت پیام‌ها.
        تابعی که با این decorator تزئین می‌شود باید یک آرگومان
        از نوع UpdateStatus_pb2.UpdateStatusResponse دریافت کند.
        """
        def decorator(func: Callable):
            filter_key = str(uuid.uuid4())
            if filter_key not in self.handlers:
                self.handlers[filter_key] = []
            self.handlers[filter_key].append({
                "filters": filters,
                "callback": func,
                "type": "update_status"
            })
            return func
        return decorator
    
    def on_edit_message(self, *filters) -> Callable:
        """
        Decorator برای ثبت هندلر ویرایش پیام‌ها.
        تابعی که با این decorator تزئین می‌شود باید یک آرگومان
        از نوع ChatEditMessage_pb2.ChatEditMessageResponse دریافت کند.
        """
        def decorator(func: Callable):
            filter_key = str(uuid.uuid4())
            if filter_key not in self.handlers:
                self.handlers[filter_key] = []
            self.handlers[filter_key].append({
                "filters": filters,
                "callback": func,
                "type": "edit_message"
            })
            return func
        return decorator

    async def _dispatch_handlers(self):
        for handler_list in self.handlers.values():
            for handler in handler_list:
                filters = handler.get("filters", [])
                callback = handler["callback"]
                handler_type = handler.get("type")
                # بررسی نوع هندلر
                if handler_type == "message":
                    if self.roomMessage and await self._match_filters(self.message_wrapper, filters):
                        await callback(self.message_wrapper)
                        if self.propagationStopped: return
                elif handler_type == "member_rights":
                    if self.data.get("permission"):
                        await callback(self.message_wrapper)
                        if self.propagationStopped:
                            return
                elif handler_type == "update_status" and self.data.get("updaterAuthorHash") and await self._match_filters(self.message_wrapper, filters):
                    await callback(self.message_wrapper)
                    if self.propagationStopped: return
                elif handler_type == "edit_message" and self.action_id in ["30203", "30325", "30425"] and await self._match_filters(self.message_wrapper, filters):
                    await callback(self.message_wrapper)
                    if self.propagationStopped: return

    async def _match_filters(self, message, filters: Tuple[Filter, ...]) -> bool:
        for f in filters:
            result = await f.check(message)
            if not result:  # اگر یکی از فیلترها False بده، هندلر اجرا نمی‌شه
                return False
        return True

    def run(self, path_webhook="/webhook", host="localhost", port=8000):
        """
        راه‌اندازی سرور aiohttp برای دریافت درخواست‌های وبهوک.

        پارامترها:
            path_webhook (str): مسیر URL برای دریافت درخواست‌های وبهوک. مقدار پیش‌فرض "/webhook" است.
                                می‌توانی آن را تغییر بدهی تا endpoint دلخواه داشته باشی.
            host (str): آدرس هاست برای اجرا.
                        - مقدار "localhost" برای تست محلی استفاده می‌شود (فقط روی همان سیستم در دسترس است).
                        - مقدار "0.0.0.0" برای اجرا روی هاست یا VPS استفاده می‌شود (روی همه‌ی اینترفیس‌ها در دسترس است).
            port (int): شماره پورت برای اجرا روی هاست. معمولاً 80 یا 443 برای وبهوک واقعی، یا 8000/8080 برای تست.

        مثال:
            run(path_webhook="/webhook", host="0.0.0.0", port=8080)
        """
        app = web.Application()
        app.router.add_post(path_webhook, self.handle_post)
        web.run_app(app, host=host, port=port)

    def stop_propagation(self):
        self.propagationStopped = True
    
    def generate_random_id(self, length=19):
        return int(''.join(str(random.randint(0, 9)) for _ in range(length)))

    def decode_message(self, binary_data: bytes, proto_cls):
        """دیکد کردن پاسخ پروتو و تبدیل به dict"""
        response = proto_cls()
        response.ParseFromString(binary_data)

        # تبدیل به dict
        decode_json = json_format.MessageToJson(response)
        return json.loads(decode_json)

    def build_proto_data(self, proto_cls, **fields) -> bytes:
        """
        ساختن پروتو و تبدیل به باینری
        proto_cls: کلاس پروتو (مثلاً ChatSendMessage_pb2.ChatSendMessage)
        fields: فیلدهای لازم برای پر کردن پروتو
        """
        message = proto_cls()
        for key, value in fields.items():
            setattr(message, key, value)
        return message.SerializeToString()
    
    async def send_message(self, room_id, text, additional_type=None, additional_data=None, reply_to_message_id = None, target_type=None):
        fields = {
            "message": text,
            "room_id": int(room_id),
            "random_id": self.generate_random_id(),
            "message_type": 0
        }
        if reply_to_message_id is not None:
            fields["reply_to"] = int(reply_to_message_id)
        if additional_type is not None:
            fields["additional_type"] = int(additional_type)
            fields["additional_data"] = str(additional_data)

        if (self.action_id and self.action_id in PRIVATE_ACTION_IDS) or (target_type and target_type == "private"):
            data = self.build_proto_data(ChatSendMessage_pb2.ChatSendMessage, **fields)
            return await self.execute_action(201, data, ChatSendMessage_pb2.ChatSendMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "group"):
            data = self.build_proto_data(GroupSendMessage_pb2.GroupSendMessage, **fields)
            return await self.execute_action(310, data, GroupSendMessage_pb2.GroupSendMessageResponse)
        elif (self.action_id and self.action_id in CHANNEL_ACTION_IDS) or (target_type and target_type == "channel"):
            data = self.build_proto_data(ChannelSendMessage_pb2.ChannelSendMessage, **fields)
            return await self.execute_action(410, data, ChannelSendMessage_pb2.ChannelSendMessageResponse)
        else:
            raise ValueError(f'Invalid target_type "{target_type}". Must be one of ("private", "group", "channel").')
    
    async def edit_message(self, room_id: int, message_id: int, new_text: str, target_type=None):
        fields = {
            "room_id": int(room_id),
            "message_id": int(message_id),
            "message": new_text
        }
        if (self.action_id and self.action_id in PRIVATE_ACTION_IDS) or (target_type and target_type == "private"):
            data = self.build_proto_data(ChatEditMessage_pb2.ChatEditMessage, **fields)
            return await self.execute_action(203, data, ChatEditMessage_pb2.ChatEditMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "group"):
            data = self.build_proto_data(GroupEditMessage_pb2.GroupEditMessage, **fields)
            return await self.execute_action(325, data, GroupEditMessage_pb2.GroupEditMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "channel"):
            data = self.build_proto_data(ChannelEditMessage_pb2.ChannelEditMessage, **fields)
            return await self.execute_action(425, data, ChannelEditMessage_pb2.ChannelEditMessageResponse)
        else:
            raise ValueError(f'Invalid target_type "{target_type}". Must be one of ("private", "group", "channel").')
    
    async def delete_message(self, room_id: int, message_id: int, delete_type="Global", target_type=None):
        fields = {
            "room_id": int(room_id),
            "message_id": int(message_id),
        }
        fields["both"] = True if delete_type == "Global" else False
        if (self.action_id and self.action_id in PRIVATE_ACTION_IDS) or (target_type and target_type == "private"):
            data = self.build_proto_data(ChatDeleteMessage_pb2.ChatDeleteMessage, **fields)
            return await self.execute_action(204, data, ChatDeleteMessage_pb2.ChatDeleteMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "group"):
            data = self.build_proto_data(GroupDeleteMessage_pb2.GroupDeleteMessage, **fields)
            return await self.execute_action(320, data, GroupDeleteMessage_pb2.GroupDeleteMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "channel"):
            data = self.build_proto_data(ChannelDeleteMessage_pb2.ChannelDeleteMessage, **fields)
            return await self.execute_action(411, data, ChannelDeleteMessage_pb2.ChannelDeleteMessageResponse)
        else:
            raise ValueError(f'Invalid target_type "{target_type}". Must be one of ("private", "group", "channel").')

    async def ban_member(self, room_id: int, member_id: int, target_type=None):
        fields = {
            "room_id": int(room_id),
            "member_id": int(member_id)
        }
        if (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type and target_type == "group"):
            data = self.build_proto_data(GroupKickMember_pb2.GroupKickMember, **fields)
            return await self.execute_action(320, data, GroupKickMember_pb2.GroupKickMemberResponse)
        else:
            raise ValueError(f'Invalid target_type "{target_type}". Must be one of ("group", "channel").')

    def generate_thumbnail(self, file_path: str, size: tuple[int, int]) -> str:
        """
        ساخت thumbnail از تصویر اصلی با اندازه‌ی مشخص.
        """
        with Image.open(file_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.thumbnail(size)

            base, ext = os.path.splitext(file_path)
            thumb_path = f"{base}_thumb.jpg"

            img.save(thumb_path, format="JPEG")

        return thumb_path

    async def send_photo(self, room_id, file_path, caption=None, reply_to_message_id=None, target_type=None):

        token = await self.upload_file_to_ighap(file_path)
        mime = mimetypes.guess_type(file_path)[0] or "image/jpeg"

        with Image.open(file_path) as img:
            width, height = img.size

        large_thumb_path = self.generate_thumbnail(file_path, (350, 824))
        large_token = await self.upload_file_to_ighap(large_thumb_path)
        large_size = os.path.getsize(large_thumb_path)

        small_thumb_path = self.generate_thumbnail(file_path, (100, 235))
        small_token = await self.upload_file_to_ighap(small_thumb_path)
        small_size = os.path.getsize(small_thumb_path)

        attachment = {
            "token": token,
            "size": os.path.getsize(file_path),
            "name": os.path.basename(file_path),
            "mime": mime,
            "width": width,
            "height": height,
            "cacheId": token,
            "largeThumbnail": {
                "size": large_size,
                "width": 350,
                "height": 824,
                "cacheId": f"{token}LT",
                "name": os.path.basename(large_thumb_path),
                "mime": "image/jpeg"
            },
            "smallThumbnail": {
                "size": small_size,
                "width": 100,
                "height": 235,
                "cacheId": f"{token}ST",
                "name": os.path.basename(small_thumb_path),
                "mime": "image/jpeg"
            }
        }

        fields = {
            "room_id": int(room_id),
            "random_id": self.generate_random_id(),
            "attachment": json.dumps(attachment),
            "message_type": 2 if caption else 1
        }

        if reply_to_message_id is not None:
            fields["reply_to"] = int(reply_to_message_id)
        if caption is not None:
            fields["message"] = caption

        if (self.action_id and self.action_id in PRIVATE_ACTION_IDS) or (target_type == "private"):
            data = self.build_proto_data(ChatSendMessage_pb2.ChatSendMessage, **fields)
            return await self.execute_action(201, data, ChatSendMessage_pb2.ChatSendMessageResponse)
        elif (self.action_id and self.action_id in GROUP_ACTION_IDS) or (target_type == "group"):
            data = self.build_proto_data(GroupSendMessage_pb2.GroupSendMessage, **fields)
            return await self.execute_action(310, data, GroupSendMessage_pb2.GroupSendMessageResponse)
        else:
            raise ValueError(f'Invalid target_type \"{target_type}\". Must be one of (\"private\", \"group\", \"channel\").')
    
    async def send_message_private(self, room_id, text, additional_type=None, additional_data=None, reply_to_message_id = None):
        return await self.send_message(room_id=room_id, text=text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id, target_type="private")

    async def edit_message_private(self, room_id: int, message_id: int, new_text: str):
        return await self.edit_message(room_id=room_id, message_id=message_id, new_text=new_text, target_type="private")

    async def delete_message_private(self, room_id: int, message_id: int, delete_type = "Global"):
        return await self.delete_message(room_id=room_id, message_id=message_id, delete_type=delete_type, target_type="private")

    async def get_room_private(self, room_id: int):
        """
        ⚠️ وضعیت: این متد در نسخه‌ی فعلی iGap Bot API غیرفعال است.
        سرور در پاسخ به درخواست، خطای PAGE_NOT_FOUND برمی‌گرداند.
        """
        fields = {
            "peer_id": int(room_id)
        }
        data = self.build_proto_data(ChatGetRoom_pb2.ChatGetRoom, **fields)
        return await self.execute_action(200, data, ChatGetRoom_pb2.ChatGetRoomResponse)

    async def send_photo_private(self, room_id, file_path, caption=None, reply_to_message_id=None):
        return await self.send_photo(room_id, file_path, caption, reply_to_message_id, "private")

    async def send_message_group(self, room_id, text, additional_type=None, additional_data=None, reply_to_message_id = None):
        return await self.send_message(room_id=room_id, text=text, additional_type=additional_type, additional_data=additional_data, reply_to_message_id=reply_to_message_id, target_type="group")

    async def edit_message_group(self, room_id: int, message_id: int, new_text: str):
        return await self.edit_message(room_id=room_id, message_id=message_id, new_text=new_text, target_type="group")

    async def delete_message_group(self, room_id: int, message_id: int, delete_type = "Global"):
        return await self.delete_message(room_id=room_id, message_id=message_id, delete_type=delete_type, target_type="group")

    async def pin_message_group(self, room_id: int, message_id: int):
        """
        ⚠️ وضعیت: این متد در نسخه‌ی فعلی iGap Bot API غیرفعال است.
        سرور در پاسخ به درخواست، خطای PAGE_NOT_FOUND برمی‌گرداند.
        """
        fields = {
            "room_id": int(room_id),
            "message_id": int(message_id)
        }

        data = self.build_proto_data(GroupPinMessage_pb2.GroupPinMessage, **fields)
        action_id = 326
        return await self.execute_action(action_id, data, GroupPinMessage_pb2.GroupPinMessageResponse)

    async def send_photo_group(self, room_id, file_path, caption = None, reply_to_message_id = None):
        return await self.send_photo(room_id, file_path, caption, reply_to_message_id, "group")
    
    async def ban_member_group(self, room_id, member_id):
        """
        ⚠️ توجه: این متد در نسخه‌ی فعلی iGap Bot API غیرفعال است.
        سرور در پاسخ به درخواست، خطای PAGE_NOT_FOUND برمی‌گرداند.
        """
        return await self.ban_member(room_id, member_id, "group")
    
    async def edit_group_info(self, room_id, group_name=None, description=None):
        """
        ⚠️ وضعیت: این متد در نسخه‌ی فعلی iGap Bot API غیرفعال است.
        سرور در پاسخ به درخواست، خطای PAGE_NOT_FOUND برمی‌گرداند.
        """
        fields = {"room_id": int(room_id)}
        if group_name is not None: fields["name"] = group_name
        if description is not None: fields["description"] = description
        data = self.build_proto_data(GroupEdit_pb2.GroupEdit, **fields)
        return await self.execute_action(30305, data, GroupEdit_pb2.GroupEditResponse)
    
    async def send_message_channel(self, room_id, text, additional_type=None, additional_data=None, reply_to_message_id = None):
        return await self.send_message(room_id, text, additional_type, additional_data, reply_to_message_id, "channel")
    
    async def edit_message_channel(self, room_id: int, message_id: int, new_text: str):
        return await self.edit_message(room_id=room_id, message_id=message_id, new_text=new_text, target_type="channel")
    
    async def delete_message_channel(self, room_id: int, message_id: int, delete_type = "Global"):
        return await self.delete_message(room_id=room_id, message_id=message_id, delete_type=delete_type, target_type="channel")

    async def upload_file_to_ighap(self, path):
        size = os.path.getsize(path)
        fields = {"size": size}
        data = self.build_proto_data(FileUploadOption_pb2.FileUploadOption, **fields)
        response = await self.execute_action(700, data, FileUploadOption_pb2.FileUploadOptionResponse)
        print("FileUploadOption_pb2: ", response)

        # مرحله دوم: FileUploadInit (با first/last bytes)
        with open(path, "rb") as f:
            first_bytes = f.read(1024)  # یا مقدار درست از FileUploadOptionResponse
            f.seek(size - 1024)
            last_bytes = f.read(1024)

        init_fields = {
            "size": size,
            "file_name": os.path.basename(path),
            "first_bytes": first_bytes,
            "last_bytes": last_bytes
        }
        init_data = self.build_proto_data(FileUploadInit_pb2.FileUploadInit, **init_fields)
        resp_init = await self.execute_action(701, init_data, FileUploadInit_pb2.FileUploadInitResponse)

        token = resp_init.get("token")
        offset = resp_init.get("offset", 0)
        limit = resp_init.get("limit", 4096)  # اگر خالی بود، یک مقدار پیش‌فرض بذار
        progress = resp_init.get("progress", 0)

        # مرحله سوم: FileUpload (chunk upload)
        with open(path, "rb") as f:
            while progress < 100:
                f.seek(offset)
                chunk = f.read(limit)

                upload_fields = {
                    "token": token,
                    "offset": offset,
                    "bytes": chunk
                }
                upload_data = self.build_proto_data(FileUpload_pb2.FileUpload, **upload_fields)
                resp_upload = await self.execute_action(702, upload_data, FileUpload_pb2.FileUploadResponse)
                print(f"resp_upload: {resp_upload}")

                progress = resp_upload.get("progress") or progress
                offset = resp_upload.get("nextOffset") or (offset + limit)
                limit = resp_upload.get("nextLimit") or limit

        # مرحله چهارم: FileUploadStatus (با retry)
        status_fields = {"token": token}
        status_data = self.build_proto_data(FileUploadStatus_pb2.FileUploadStatus, **status_fields)

        for attempt in range(5):
            resp_status = await self.execute_action(703, status_data, FileUploadStatus_pb2.FileUploadStatusResponse)
            print(f"resp_status: {resp_status}")
            if resp_status.get("status") == "PROCESSED":
                return token
            await asyncio.sleep(1)

        raise Exception("Upload failed or still processing after retries")

    async def execute_action(
        self,
        action_id: int,
        payload: bytes,
        decode_type: Callable[[bytes], Any] = None
    ):
        url = f"https://api.igap.net/botland/v1/api?actionId={action_id}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=self.headers) as resp:
                resp_bytes = await resp.read()

                if decode_type:
                    try: return self.decode_message(resp_bytes, decode_type)
                    except Exception as e:
                        error_info = {
                            "Error decode": str(e),
                            "bytes": resp_bytes if resp_bytes else None
                        }
                        return error_info
                else:
                    return resp_bytes

