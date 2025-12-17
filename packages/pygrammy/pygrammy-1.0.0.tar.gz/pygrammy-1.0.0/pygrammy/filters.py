from typing import Callable


class Filter:
    """
    Custom filter yaratish uchun
    
    Example:
        is_admin = Filter(lambda ctx: ctx.from_user.id in ADMIN_IDS)
        
        @bot.filter(is_admin)
        async def admin_handler(ctx):
            await ctx.reply("Admin paneliga xush kelibsiz!")
    """
    
    def __init__(self, predicate: Callable):
        self.predicate = predicate
    
    def __call__(self, ctx):
        return self.predicate(ctx)
    
    def __and__(self, other):
        """AND operator"""
        return Filter(lambda ctx: self(ctx) and other(ctx))
    
    def __or__(self, other):
        """OR operator"""
        return Filter(lambda ctx: self(ctx) or other(ctx))
    
    def __invert__(self):
        """NOT operator"""
        return Filter(lambda ctx: not self(ctx))


# Tayyor filtrlar
class Filters:
    """Tayyor filtrlar to'plami"""
    
    @staticmethod
    def text(ctx):
        return ctx.message and ctx.message.text is not None
    
    @staticmethod
    def photo(ctx):
        return ctx.message and ctx.message.photo is not None
    
    @staticmethod
    def video(ctx):
        return ctx.message and ctx.message.video is not None
    
    @staticmethod
    def private_chat(ctx):
        return ctx.chat and ctx.chat.type == "private"
    
    @staticmethod
    def group_chat(ctx):
        return ctx.chat and ctx.chat.type in ["group", "supergroup"]