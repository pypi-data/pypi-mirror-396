from typing import Dict, Any, Callable, Optional
import json
from pathlib import Path


class MemorySessionStorage:
    """Xotirada session saqlash"""
    
    def __init__(self):
        self.sessions: Dict[int, Dict] = {}
    
    async def get(self, chat_id: int) -> Optional[Dict]:
        return self.sessions.get(chat_id)
    
    async def set(self, chat_id: int, data: Dict):
        self.sessions[chat_id] = data
    
    async def delete(self, chat_id: int):
        self.sessions.pop(chat_id, None)


class FileSessionStorage:
    """Faylda session saqlash"""
    
    def __init__(self, directory: str = "sessions"):
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=True)
    
    def _get_file_path(self, chat_id: int) -> Path:
        return self.directory / f"{chat_id}.json"
    
    async def get(self, chat_id: int) -> Optional[Dict]:
        file_path = self._get_file_path(chat_id)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    async def set(self, chat_id: int, data: Dict):
        file_path = self._get_file_path(chat_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def delete(self, chat_id: int):
        file_path = self._get_file_path(chat_id)
        if file_path.exists():
            file_path.unlink()


def session(
    initial: Optional[Callable[[], Dict]] = None,
    storage: Optional[Any] = None,
    get_session_key: Optional[Callable] = None,
):
    """
    Session middleware
    
    Example:
        bot.use(session(initial=lambda: {"count": 0}))
        
        @bot.on("message:text")
        async def handler(ctx):
            ctx.session["count"] += 1
            await ctx.reply(f"Count: {ctx.session['count']}")
    """
    if storage is None:
        storage = MemorySessionStorage()
    
    if initial is None:
        initial = lambda: {}
    
    if get_session_key is None:
        get_session_key = lambda ctx: ctx.chat_id
    
    async def middleware(ctx, next):
        session_key = get_session_key(ctx)
        
        if session_key is None:
            await next()
            return
        
        # Session'ni yuklash
        session_data = await storage.get(session_key)
        if session_data is None:
            session_data = initial()
        
        ctx.session = session_data
        
        # Handler'ni bajarish
        await next()
        
        # Session'ni saqlash
        await storage.set(session_key, ctx.session)
    
    return middleware