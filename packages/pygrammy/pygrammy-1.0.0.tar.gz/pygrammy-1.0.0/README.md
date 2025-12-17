# 🐍 PyGrammY

**PyGrammY** — bu Python uchun **to‘liq asinxron**, **grammy.js’dan ilhomlangan**, zamonaviy **Telegram Bot Framework**.  
U `async/await`, `httpx`, middleware, session, filters va modular arxitekturani qo‘llab-quvvatlaydi.

---

## 🚀 Xususiyatlar

- ⚡ To‘liq **asinxron** (`async/await`)
- 🌐 `httpx` asosida Telegram Bot API
- 🧠 **Context (ctx)** — barcha ma’lumotlar bitta joyda
- 🔌 **Middleware chain** (GrammyJS uslubida)
- 💾 **Session** (memory & file storage)
- 🧩 **Composer** — modular bot arxitekturasi
- 🎯 Kuchli **filters**
- ⌨️ Inline & Reply **Keyboards**
- 🪝 **Polling** va **Webhook** qo‘llab-quvvatlanadi
- 🛡 Global **error handling**

---

## 📦 O‘rnatish

### PyPI orqali (kelajakda)
```bash
pip install pygrammy
````

### Lokal o‘rnatish

```bash
pip install httpx aiohttp
```

```text
project/
├── pygrammy/
│   ├── bot.py
│   ├── context.py
│   ├── keyboard.py
│   ├── session.py
│   ├── filters.py
│   ├── composer.py
│   ├── types.py
│   └── __init__.py
└── main.py
```

---

## 🧑‍💻 Minimal misol

```python
import asyncio
from pygrammy import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.command("start")
async def start(ctx):
    await ctx.reply("👋 Salom, PyGrammY ishlayapti!")

async def main():
    async with bot:
        await bot.start()

asyncio.run(main())
```

---

## 🧩 Middleware

```python
@bot.use
async def logger(ctx, next):
    print(ctx.update.update_id)
    await next()
```

---

## 💾 Session

```python
from pygrammy import session

bot.use(session(initial=lambda: {"count": 0}))

@bot.on("message:text")
async def counter(ctx):
    ctx.session["count"] += 1
    await ctx.reply(f"Count: {ctx.session['count']}")
```

---

## ⌨️ Inline Keyboard

```python
from pygrammy import InlineKeyboard

kb = InlineKeyboard()
kb.text("👍 Like", "like").row().url("Google", "https://google.com")

await ctx.reply("Tanlang:", reply_markup=kb)
```

---

## 🎯 Filters

```python
@bot.on("message:photo")
async def photo_handler(ctx):
    await ctx.reply("📸 Rasm qabul qilindi")
```

Custom filter:

```python
@bot.filter(lambda ctx: ctx.chat.type == "private")
async def private_only(ctx):
    await ctx.reply("Private chat")
```

---

## 🪝 Callback Query

```python
@bot.callback_query("like")
async def like(ctx):
    await ctx.answer_callback_query("👍")
```

---

## 🌐 Webhook

```python
await bot.start(webhook={
    "domain": "https://example.com",
    "path": "/webhook",
    "port": 8443
})
```

---

## 🆚 GrammyJS bilan taqqoslash

| Xususiyat | GrammyJS   | PyGrammY    |
| --------- | ---------- | ----------- |
| Til       | JS / TS    | Python      |
| Async     | Promise    | async/await |
| HTTP      | fetch      | httpx       |
| Typing    | TypeScript | type hints  |

---