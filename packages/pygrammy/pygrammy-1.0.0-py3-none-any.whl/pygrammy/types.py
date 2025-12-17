from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class User:
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class Chat:
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class MessageEntity:
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        if "user" in data:
            data["user"] = User.from_dict(data["user"])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class PhotoSize:
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class Message:
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    photo: Optional[List[PhotoSize]] = None
    video: Optional[Dict] = None
    voice: Optional[Dict] = None
    document: Optional[Dict] = None
    reply_to_message: Optional['Message'] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        data = data.copy()
        
        if "from" in data:
            data["from_user"] = User.from_dict(data.pop("from"))
        
        if "chat" in data:
            data["chat"] = Chat.from_dict(data["chat"])
        
        if "entities" in data:
            data["entities"] = [MessageEntity.from_dict(e) for e in data["entities"]]
        
        if "photo" in data:
            data["photo"] = [PhotoSize.from_dict(p) for p in data["photo"]]
        
        if "reply_to_message" in data:
            data["reply_to_message"] = Message.from_dict(data["reply_to_message"])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class CallbackQuery:
    id: str
    from_user: User
    data: Optional[str] = None
    message: Optional[Message] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        data = data.copy()
        
        if "from" in data:
            data["from_user"] = User.from_dict(data.pop("from"))
        
        if "message" in data:
            data["message"] = Message.from_dict(data["message"])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class Update:
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    
    @classmethod
    def from_dict(cls, data: Dict):
        data = data.copy()
        
        if "message" in data:
            data["message"] = Message.from_dict(data["message"])
        
        if "edited_message" in data:
            data["edited_message"] = Message.from_dict(data["edited_message"])
        
        if "callback_query" in data:
            data["callback_query"] = CallbackQuery.from_dict(data["callback_query"])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})