from __future__ import annotations
import json
from typing import TypedDict, Optional, List, Union, Dict, Any


class ImageDict(TypedDict):
    url: str
    width: Union[int, str]


class MessageDict(TypedDict):
    id: str
    timestamp: str
    user: dict
    text: str
    chat: Optional[Chat]
    images: Union[List[ImageDict], None]
    file: Union[dict, None]


class JsonSerializable:
    def to_json(self) -> str:
        raise NotImplementedError


class Dictionaryable:
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


class JsonDeserializable(object):
    @classmethod
    def de_json(cls, json_string):
        raise NotImplementedError


class User(JsonDeserializable, Dictionaryable, JsonSerializable):  # noqa
    def __init__(
        self,
        login: str = "",
        id: str = "",
        display_name: str = "",
        robot: bool = False,
    ):
        self.user_id = id
        self.display_name = display_name
        self.login = login
        self.robot = robot

    def to_dict(self):
        return {
            "id": self.user_id,
            "display_name": self.display_name,
            "login": self.login,
            "is_robot": self.robot,
        }


class File(JsonDeserializable, Dictionaryable, JsonSerializable):
    def __init__(self, file_id: str, name: str, size: int):
        self.file_id = file_id
        self.name = name
        self.size = size

    def to_dict(self):
        return {
            "id": self.file_id,
            "name": self.name,
            "size": self.size,
        }

    def __repr__(self):
        return f"<File object> {self.file_id}, {self.name}, size: {self.size}"


class Image(JsonDeserializable, Dictionaryable, JsonSerializable):
    def __init__(
        self,
        image_id: str,
        width: int,
        height: int,
        name: str = "",
        size: int = 0,
    ):
        self.image_id = image_id
        self.width = width
        self.height = height
        self.name = name
        self.size = size

    def to_dict(self):
        return {
            "id": self.image_id,
            "width": self.width,
            "height": self.height,
            "name": self.name,
            "size": self.size,
        }

    def __repr__(self):
        return f"<Image object> {self.image_id}, {self.name}, width {self.width}x{self.height}"


class Message:
    def __init__(
        self,
        message_id: str,
        timestamp: str,
        text: str,
        user: User,
        chat: Optional[Chat] = None,
        pictures: Optional[List[Image]] = None,
        attachment: Optional[File] = None,
        **kwargs,
    ):
        if not isinstance(user, User):
            raise ValueError("user должен быть объектом User")
        if chat is not None and not isinstance(chat, Chat):
            raise ValueError("chat должен быть объектом Chat")
        if pictures is not None and not all(
            isinstance(picture, Image) for picture in pictures
        ):
            raise ValueError("pictures должен быть списком объектов Image")
        if attachment is not None and not isinstance(attachment, File):
            raise ValueError("attachment должен быть объектом File")
        self.message_id = message_id
        self.timestamp = timestamp
        self.text = text
        self.user = user
        self.chat = chat
        self.images = pictures if pictures else []
        self.file = attachment
        self.callback_data = kwargs.get("callback_data")

    def to_dict(self) -> MessageDict:
        data: MessageDict = {
            "id": str(self.message_id),
            "timestamp": str(self.timestamp),
            "user": self.user.to_dict(),
            "text": self.text,
            "chat": None,
            "images": None,
            "file": None,
        }
        if self.chat:
            data["chat"] = {k: str(v) for k, v in self.chat.to_dict().items()}
        if self.images:
            data["images"] = [
                ImageDict(
                    url=str(img.url),
                    width=int(img.width),  # type: ignore[attr-defined]
                )  # Явное создание ImageDict
                for img in self.images
            ]
        if self.file:
            data["file"] = {k: str(v) for k, v in self.file.to_dict().items()}
        return data


class Chat(JsonDeserializable, Dictionaryable, JsonSerializable):
    def __init__(
        self,
        name: str = "",
        description: str = "",
        avatar_url: str = "",
        chat_id: str = "",
        **kwargs,
    ):
        self.chat_id = chat_id
        self.name = name
        self.description = description
        self.avatar_url = avatar_url
        self.members: List[User] = []
        self.admins: List[User] = []
        self.subscribers: List[User] = []

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "name": self.name,
            "description": self.description,
            "members": [member.to_dict() for member in self.members],
            "admins": [admin.to_dict() for admin in self.admins],
            "subscribers": [subscriber.to_dict() for subscriber in self.subscribers],
        }

    def set_members(self, members: Optional[List[User]]):
        self.members = members or []
        return self.members

    def set_admins(self, admins: Optional[List[User]]) -> List[User]:
        if admins is not None and not all(isinstance(admin, User) for admin in admins):
            raise ValueError("admins должен быть списком объектов User")
        self.admins = admins or []
        return self.admins

    def set_subscribers(self, subscribers: Optional[List[User]]):
        self.subscribers = subscribers or []
        return self.subscribers


class Button(JsonDeserializable, Dictionaryable, JsonSerializable):
    def __init__(
        self, text: str, callback_data: Optional[dict] = None, phrase: str = ""
    ):
        self.text = text
        self.callback_data = callback_data or {}
        if phrase:
            self.callback_data.update({"phrase": phrase})

    def to_dict(self):
        return {
            "text": self.text,
            "callback_data": self.callback_data,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class Poll(JsonDeserializable, Dictionaryable, JsonSerializable):
    def __init__(
        self,
        title: str,
        answers: list[str],
        max_choices: int = 1,
        is_anonymous: bool = False,
    ) -> None:
        self.title = title
        self.answers = answers
        self.max_choices = max_choices
        self.is_anonymous = is_anonymous

    def to_dict(self):
        return {
            "title": self.title,
            "answers": self.answers,
            "max_choices": self.max_choices,
            "is_anonymous": self.is_anonymous,
        }
