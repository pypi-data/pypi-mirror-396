import json
from dataclasses import dataclass
from typing import List


class AdditionalTypeEnum:
    NONE = 0
    UNDER_KEYBOARD_BUTTON = 1
    UNDER_MESSAGE_BUTTON = 2
    BUTTON_CLICK_ACTION = 3
    STICKER = 4
    GIF = 5
    STREAM_TYPE = 6
    KEYBOARD_TYPE = 7
    FORM_BUILDER = 8
    WEBVIEW_SHOW = 9

class ActionTypeEnum:
    JOIN_LINK = 1
    BOT_ACTION = 2
    USERNAME_LINK = 3
    WEB_LINK = 4
    WEBVIEW_LINK = 5
    STREAM_PLAY = 6
    PAY_BY_WALLET = 7
    PAY_DIRECT = 8
    REQUEST_PHONE = 9
    REQUEST_LOCATION = 10
    SHOW_ALERT = 11
    PAGE = 12
    FINANCIAL_MENU = 13
    BILL_MENU = 14
    TRAFFIC_BILL_MENU = 15
    MOBILE_BILL_MENU = 16
    PHONE_BILL_MENU = 17
    TOPUP_MENU = 18
    WALLET_MENU = 19
    NEARBY_MENU = 20
    CALL = 21
    STICKER_SHOP = 22
    IVAN = 23
    IVANQR = 24
    IVANDLIST = 25
    IVANDSCORE = 26
    CARD_TO_CARD = 27

@dataclass
class Button:
    action_type: int
    label: str
    value: str
    image_url: str = ""

    def to_dict(self) -> dict:
        return {
            "actionType": self.action_type,
            "label": self.label,
            "value": self.value,
            "imageUrl": self.image_url,
        }


@dataclass
class ButtonRow:
    buttons: List[Button]

    def to_list(self) -> List[dict]:
        return [btn.to_dict() for btn in self.buttons]


@dataclass
class ButtonKeyboard:
    rows: List[ButtonRow]

    def to_json(self) -> str:
        """خروجی JSON آماده برای additionalData"""
        return json.dumps([row.to_list() for row in self.rows], ensure_ascii=False)
    
    def __str__(self) -> str:
        return json.dumps([row.to_list() for row in self.rows], ensure_ascii=False)

