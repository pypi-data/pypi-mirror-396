from typing import List, Callable


class Composer:
    """
    Modular bot qismlari uchun
    
    Example:
        # handlers/start.py
        composer = Composer()
        
        @composer.command("start")
        async def start(ctx):
            await ctx.reply("Salom!")
        
        # main.py
        from handlers.start import composer as start_composer
        bot.use(start_composer)
    """
    
    def __init__(self):
        self._handlers: List[Callable] = []
        self._middlewares: List[Callable] = []
    
    def use(self, middleware: Callable):
        """Middleware qo'shish"""
        self._middlewares.append(middleware)
        return middleware
    
    def command(self, commands, handler=None):
        """Buyruq qo'shish"""
        def decorator(func):
            self._handlers.append({
                "type": "command",
                "commands": commands if isinstance(commands, list) else [commands],
                "handler": func,
            })
            return func
        
        if handler:
            decorator(handler)
            return handler
        return decorator
    
    def on(self, filter_query, handler=None):
        """Filter qo'shish"""
        def decorator(func):
            self._handlers.append({
                "type": "on",
                "filter": filter_query,
                "handler": func,
            })
            return func
        
        if handler:
            decorator(handler)
            return handler
        return decorator
    
    def callback_query(self, data, handler=None):
        """Callback qo'shish"""
        def decorator(func):
            self._handlers.append({
                "type": "callback_query",
                "data": data,
                "handler": func,
            })
            return func
        
        if handler:
            decorator(handler)
            return handler
        return decorator
    
    async def __call__(self, ctx, next):
        """Middleware sifatida ishlaydi"""
        # Bu composer'ning middleware'larini ishlatish
        for middleware in self._middlewares:
            await middleware(ctx, lambda: None)
        
        # Handler'larni botga qo'shish
        for handler_info in self._handlers:
            if handler_info not in ctx.bot._handlers:
                ctx.bot._handlers.append(handler_info)
        
        await next()