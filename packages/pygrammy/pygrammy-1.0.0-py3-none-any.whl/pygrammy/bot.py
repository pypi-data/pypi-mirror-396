import asyncio
import logging
from typing import Callable, Optional, Union, List, Dict, Any
import httpx
from .context import Context
from .types import Update, Message

logger = logging.getLogger(__name__)


class Bot:
    """
    PyGrammY Bot - Telegram Bot API uchun async framework
    """

    def __init__(
        self,
        token: str,
        api_url: str = "https://api.telegram.org",
        timeout: float = 30.0,
    ):
        self.token = token
        self.api_url = f"{api_url}/bot{token}"
        self.timeout = timeout
        
        self._middlewares: List[Callable] = []
        self._handlers: List[Dict[str, Any]] = []
        self._error_handler: Optional[Callable] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._running = False
        
        # Offset for getUpdates
        self._offset = 0

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)

    async def api_request(
        self, method: str, params: Optional[Dict] = None, files: Optional[Dict] = None
    ) -> Dict:
        """
        Telegram API ga so'rov yuborish
        """
        await self._ensure_client()
        
        url = f"{self.api_url}/{method}"
        
        try:
            if files:
                response = await self._client.post(url, data=params, files=files)
            else:
                response = await self._client.post(url, json=params)
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                raise Exception(f"API Error: {result.get('description')}")
            
            return result.get("result")
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            raise
        except Exception as e:
            logger.error(f"API Request Error: {e}")
            raise

    # ==================== Update Handlers ====================

    def use(self, middleware: Callable):
        """
        Global middleware qo'shish
        
        Example:
            @bot.use
            async def logger_middleware(ctx, next):
                print(f"Update: {ctx.update.update_id}")
                await next()
        """
        self._middlewares.append(middleware)
        return middleware

    def on(self, filter_query: Union[str, Callable], handler: Optional[Callable] = None):
        """
        Filter asosida handler qo'shish
        
        Examples:
            bot.on("message", handler)
            bot.on("message:text", handler)
            bot.on("callback_query", handler)
        """
        def decorator(func: Callable):
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

    def command(self, commands: Union[str, List[str]], handler: Optional[Callable] = None):
        """
        Buyruq handleri
        
        Examples:
            @bot.command("start")
            async def start(ctx):
                await ctx.reply("Salom!")
            
            @bot.command(["help", "yordam"])
            async def help_handler(ctx):
                await ctx.reply("Yordam...")
        """
        if isinstance(commands, str):
            commands = [commands]
        
        def decorator(func: Callable):
            self._handlers.append({
                "type": "command",
                "commands": commands,
                "handler": func,
            })
            return func
        
        if handler:
            decorator(handler)
            return handler
        return decorator

    def callback_query(self, data: Union[str, Callable], handler: Optional[Callable] = None):
        """
        Callback query handler
        
        Example:
            @bot.callback_query("like")
            async def like_handler(ctx):
                await ctx.answer_callback_query("Yoqdi! 👍")
        """
        def decorator(func: Callable):
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

    def filter(self, filter_func: Callable, handler: Callable):
        """
        Custom filter
        
        Example:
            @bot.filter(lambda ctx: ctx.chat.type == "private")
            async def private_handler(ctx):
                await ctx.reply("Shaxsiy chat")
        """
        self._handlers.append({
            "type": "filter",
            "filter_func": filter_func,
            "handler": handler,
        })
        return handler

    def catch(self, error_handler: Callable):
        """
        Global error handler
        
        Example:
            @bot.catch
            async def error_handler(error, ctx):
                print(f"Error: {error}")
        """
        self._error_handler = error_handler
        return error_handler

    # ==================== Update Processing ====================

    async def _process_update(self, update_data: Dict):
        """Update ni qayta ishlash"""
        try:
            update = Update.from_dict(update_data)
            ctx = Context(bot=self, update=update)
            
            # Middleware chain
            middleware_chain = self._middlewares.copy()
            handler_found = False

            async def run_middlewares(index: int = 0):
                nonlocal handler_found
                
                if index < len(middleware_chain):
                    # Middleware ishlatish
                    middleware = middleware_chain[index]
                    
                    async def next_middleware():
                        await run_middlewares(index + 1)
                    
                    await middleware(ctx, next_middleware)
                else:
                    # Handler topish va ishlatish
                    for handler_info in self._handlers:
                        if await self._match_handler(ctx, handler_info):
                            handler_found = True
                            await handler_info["handler"](ctx)
                            break
            
            await run_middlewares()
            
        except Exception as e:
            if self._error_handler:
                await self._error_handler(e, ctx if 'ctx' in locals() else None)
            else:
                logger.error(f"Unhandled error: {e}", exc_info=True)

    async def _match_handler(self, ctx: Context, handler_info: Dict) -> bool:
        """Handler mosligini tekshirish"""
        handler_type = handler_info["type"]
        
        if handler_type == "command":
            if ctx.message and ctx.message.text:
                text = ctx.message.text
                if text.startswith("/"):
                    command = text.split()[0][1:].split("@")[0]
                    return command in handler_info["commands"]
        
        elif handler_type == "on":
            filter_query = handler_info["filter"]
            return self._match_filter(ctx, filter_query)
        
        elif handler_type == "callback_query":
            if ctx.callback_query:
                data = handler_info["data"]
                if callable(data):
                    return await data(ctx)
                return ctx.callback_query.data == data
        
        elif handler_type == "filter":
            filter_func = handler_info["filter_func"]
            if callable(filter_func):
                result = filter_func(ctx)
                if asyncio.iscoroutine(result):
                    return await result
                return result
        
        return False

    def _match_filter(self, ctx: Context, filter_query: str) -> bool:
        """Filter query ni tekshirish"""
        parts = filter_query.split(":")
        
        # message
        if parts[0] == "message":
            if not ctx.message:
                return False
            if len(parts) == 1:
                return True
            
            # message:text
            if parts[1] == "text":
                return ctx.message.text is not None
            
            # message:photo
            elif parts[1] == "photo":
                return ctx.message.photo is not None
            
            # message:video
            elif parts[1] == "video":
                return ctx.message.video is not None
            
            # message:voice
            elif parts[1] == "voice":
                return ctx.message.voice is not None
            
            # message:document
            elif parts[1] == "document":
                return ctx.message.document is not None
            
            # message:entities:url
            elif parts[1] == "entities" and len(parts) > 2:
                if not ctx.message.entities:
                    return False
                entity_type = parts[2]
                return any(e.type == entity_type for e in ctx.message.entities)
        
        # callback_query
        elif parts[0] == "callback_query":
            return ctx.callback_query is not None
        
        # edited_message
        elif parts[0] == "edited_message":
            return ctx.edited_message is not None
        
        return False

    # ==================== Polling & Webhook ====================

    async def start(self, webhook: Optional[Dict] = None, drop_pending_updates: bool = False):
        """
        Botni ishga tushirish
        
        Examples:
            # Polling
            await bot.start()
            
            # Webhook
            await bot.start(webhook={
                "domain": "https://example.com",
                "port": 8443,
                "path": "/webhook"
            })
        """
        self._running = True
        await self._ensure_client()
        
        if drop_pending_updates:
            await self.api_request("deleteWebhook", {"drop_pending_updates": True})
        
        if webhook:
            await self._start_webhook(webhook)
        else:
            await self._start_polling()

    async def _start_polling(self):
        """Long polling"""
        logger.info("🚀 Bot started (polling mode)")
        
        try:
            while self._running:
                try:
                    updates = await self.api_request("getUpdates", {
                        "offset": self._offset,
                        "timeout": 30,
                        "allowed_updates": ["message", "callback_query", "edited_message"],
                    })
                    
                    for update in updates:
                        self._offset = update["update_id"] + 1
                        asyncio.create_task(self._process_update(update))
                    
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                    await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped")
        finally:
            if self._client:
                await self._client.aclose()

    async def _start_webhook(self, webhook_config: Dict):
        """Webhook mode (qo'shimcha konfiguratsiya kerak)"""
        from aiohttp import web
        
        domain = webhook_config["domain"]
        port = webhook_config.get("port", 8443)
        path = webhook_config.get("path", "/webhook")
        
        # Webhook o'rnatish
        await self.api_request("setWebhook", {
            "url": f"{domain}{path}",
        })
        
        logger.info(f"🚀 Bot started (webhook mode) at {domain}{path}")
        
        async def webhook_handler(request):
            update = await request.json()
            await self._process_update(update)
            return web.Response(text="OK")
        
        app = web.Application()
        app.router.add_post(path, webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        
        # Keep running
        while self._running:
            await asyncio.sleep(1)

    def stop(self):
        """Botni to'xtatish"""
        self._running = False