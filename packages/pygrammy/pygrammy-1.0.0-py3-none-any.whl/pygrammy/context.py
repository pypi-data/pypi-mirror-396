from typing import Optional, Dict, Any, Union
from .types import Update, Message, CallbackQuery, Chat, User
from .keyboard import InlineKeyboard, Keyboard


class Context:
    """
    Context - har bir update uchun yaratiladi
    GrammyJS ctx ga o'xshash
    """

    def __init__(self, bot, update: Update):
        self.bot = bot
        self.update = update
        
        # State (vaqtinchalik ma'lumotlar)
        self.state: Dict[str, Any] = {}
        
        # Session (middleware orqali qo'shiladi)
        self.session: Optional[Dict] = None

    # ==================== Update qismlari ====================

    @property
    def message(self) -> Optional[Message]:
        """Kelgan xabar"""
        return self.update.message

    @property
    def edited_message(self) -> Optional[Message]:
        """O'zgartirilgan xabar"""
        return self.update.edited_message

    @property
    def callback_query(self) -> Optional[CallbackQuery]:
        """Callback query"""
        return self.update.callback_query

    @property
    def chat(self) -> Optional[Chat]:
        """Chat obyekti"""
        if self.message:
            return self.message.chat
        elif self.callback_query and self.callback_query.message:
            return self.callback_query.message.chat
        return None

    @property
    def from_user(self) -> Optional[User]:
        """Xabar yuborgan foydalanuvchi"""
        if self.message:
            return self.message.from_user
        elif self.callback_query:
            return self.callback_query.from_user
        return None

    @property
    def chat_id(self) -> Optional[int]:
        """Chat ID"""
        if self.chat:
            return self.chat.id
        return None

    # ==================== API metodlar (ctx.api) ====================

    @property
    def api(self):
        """API metodlariga to'g'ridan-to'g'ri kirish"""
        return self.bot

    # ==================== Javob metodlari ====================

    async def reply(
        self,
        text: str,
        reply_markup: Optional[Union[InlineKeyboard, Keyboard]] = None,
        parse_mode: Optional[str] = None,
        **kwargs
    ):
        """
        Xabarga javob berish
        
        Example:
            await ctx.reply("Salom!", parse_mode="HTML")
        """
        params = {
            "chat_id": self.chat_id,
            "text": text,
            **kwargs
        }
        
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        
        if parse_mode:
            params["parse_mode"] = parse_mode
        
        return await self.bot.api_request("sendMessage", params)

    async def send_message(self, text: str, **kwargs):
        """Xabar yuborish (reply bilan bir xil)"""
        return await self.reply(text, **kwargs)

    async def send_photo(
        self,
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional[Union[InlineKeyboard, Keyboard]] = None,
        **kwargs
    ):
        """Rasm yuborish"""
        params = {
            "chat_id": self.chat_id,
            "photo": photo,
            **kwargs
        }
        
        if caption:
            params["caption"] = caption
        
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        
        return await self.bot.api_request("sendPhoto", params)

    async def send_video(self, video: Union[str, bytes], **kwargs):
        """Video yuborish"""
        params = {"chat_id": self.chat_id, "video": video, **kwargs}
        return await self.bot.api_request("sendVideo", params)

    async def send_document(self, document: Union[str, bytes], **kwargs):
        """Fayl yuborish"""
        params = {"chat_id": self.chat_id, "document": document, **kwargs}
        return await self.bot.api_request("sendDocument", params)

    async def answer_callback_query(
        self,
        text: Optional[str] = None,
        show_alert: bool = False,
        **kwargs
    ):
        """
        Callback query ga javob berish
        
        Example:
            await ctx.answer_callback_query("Muvaffaqiyatli!")
        """
        if not self.callback_query:
            raise ValueError("No callback query to answer")
        
        params = {
            "callback_query_id": self.callback_query.id,
            **kwargs
        }
        
        if text:
            params["text"] = text
        
        if show_alert:
            params["show_alert"] = show_alert
        
        return await self.bot.api_request("answerCallbackQuery", params)

    async def edit_message_text(
        self,
        text: str,
        reply_markup: Optional[InlineKeyboard] = None,
        **kwargs
    ):
        """Xabar matnini o'zgartirish"""
        params = {
            "chat_id": self.chat_id,
            "text": text,
            **kwargs
        }
        
        if self.callback_query and self.callback_query.message:
            params["message_id"] = self.callback_query.message.message_id
        elif self.message:
            params["message_id"] = self.message.message_id
        
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        
        return await self.bot.api_request("editMessageText", params)

    async def edit_message_reply_markup(
        self,
        reply_markup: Optional[InlineKeyboard] = None,
        **kwargs
    ):
        """Xabar tugmalarini o'zgartirish"""
        params = {"chat_id": self.chat_id, **kwargs}
        
        if self.callback_query and self.callback_query.message:
            params["message_id"] = self.callback_query.message.message_id
        elif self.message:
            params["message_id"] = self.message.message_id
        
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        
        return await self.bot.api_request("editMessageReplyMarkup", params)

    async def delete_message(self, message_id: Optional[int] = None):
        """Xabarni o'chirish"""
        msg_id = message_id or (self.message.message_id if self.message else None)
        
        if not msg_id:
            raise ValueError("No message to delete")
        
        return await self.bot.api_request("deleteMessage", {
            "chat_id": self.chat_id,
            "message_id": msg_id,
        })

    async def get_file(self, file_id: str):
        """Fayl haqida ma'lumot olish"""
        return await self.bot.api_request("getFile", {"file_id": file_id})

    async def ban_chat_member(self, user_id: int, **kwargs):
        """Foydalanuvchini bloklash"""
        params = {
            "chat_id": self.chat_id,
            "user_id": user_id,
            **kwargs
        }
        return await self.bot.api_request("banChatMember", params)

    async def unban_chat_member(self, user_id: int, **kwargs):
        """Foydalanuvchini blokdan chiqarish"""
        params = {
            "chat_id": self.chat_id,
            "user_id": user_id,
            **kwargs
        }
        return await self.bot.api_request("unbanChatMember", params)