import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# =============== НАСТРОЙКИ БОТА ===============
TOKEN = os.getenv("BOT_TOKEN") or "ВАШ_ТОКЕН_БОТА"
bot = Bot(token=8542988551:AAHkBPHMLpcMB5zX-stuMN42M_fuJ6JDZbY, parse_mode=ParseMode.HTML)
dp = Dispatcher()

DATA_FILE = "data.json"

# =============== ЗАГРУЗКА / СОХРАНЕНИЕ ДАННЫХ ===============
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user(user_id, user_name=None):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "name": user_name or "Unknown",
            "level": 1,
            "xp": 0,
            "resets": 0
        }
        save_data(data)
    return data[str(user_id)]

def update_user(user_id, **kwargs):
    data = load_data()
    user = data.get(str(user_id))
    if not user:
        return None
    for key, value in kwargs.items():
        user[key] = value
    data[str(user_id)] = user
    save_data(data)
    return user

# =============== XP ФОРМУЛА ===============
def xp_for_next_level(level):
    return 20 + level * 10

# =============== АВТО-ДОБАВЛЕНИЕ XP ОТКЛЮЧЕНО ===============
# Автоматическая выдача XP за сообщения отключена полностью.</b> получил новый уровень! → <b>{user['level']}</b>")

# =============== /level ===============
@dp.message(Command("level"))
async def level_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    need = xp_for_next_level(user["level"])
    await message.reply(
        f"👤 <b>Ваш уровень:</b> {user['level']}\n"
        f"⭐ <b>XP:</b> {user['xp']} / {need}\n"
        f"🔄 <b>Ресетов:</b> {user['resets']}"
    )

# =============== /reset ===============
@dp.message(Command("reset"))
async def reset_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["level"] = 1
    user["xp"] = 0
    user["resets"] += 1
    update_user(message.from_user.id, **user)
    await message.reply(f"♻️ <b>Уровень сброшен!</b>\nТеперь уровень: 1\nВсего ресетов: {user['resets']}")

# =============== ПРОВЕРКА АДМИНА ===============
async def is_admin(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

# =============== /adduser ===============
@dp.message(Command("adduser"))
async def adduser_cmd(message: types.Message):
    if not await is_admin(message):
        return await message.reply("❗ Только администратор может повышать уровни.")

    args = message.text.split()

    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
        if len(args) < 2 or not args[1].isdigit():
            return await message.reply("Использование: /adduser 20 (в ответ на сообщение)")
        amount = int(args[1])

    else:
        if len(args) < 3:
            return await message.reply("Использование: /adduser ID 20")
        if not args[2].isdigit():
            return await message.reply("XP должно быть числом!")
        target = int(args[1])
        amount = int(args[2])

    user = get_user(target)
    user["xp"] += amount

    leveled_up = False
    while user["xp"] >= xp_for_next_level(user["level"]) and user["level"] < 120:
        user["xp"] -= xp_for_next_level(user["level"])
        user["level"] += 1
        leveled_up = True

    update_user(target, **user)

    if leveled_up:
        await message.reply(f"🎉 {user['name']} повысил уровень до <b>{user['level']}</b>")
    else:
        await message.reply(f"✨ {user['name']} получил +{amount} XP")

# =============== /removeuser ===============
@dp.message(Command("removeuser"))
async def removeuser_cmd(message: types.Message):
    if not await is_admin(message):
        return await message.reply("❗ Только администратор может понижать уровни.")

    args = message.text.split()

    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
        if len(args) < 2 or not args[1].isdigit():
            return await message.reply("Использование: /removeuser 20 (в ответ)")
        amount = int(args[1])

    else:
        if len(args) < 3:
            return await message.reply("Использование: /removeuser ID 20")
        if not args[2].isdigit():
            return await message.reply("XP должно быть числом!")
        target = int(args[1])
        amount = int(args[2])

    user = get_user(target)
    user["xp"] -= amount

    leveled_down = False
    while user["xp"] < 0 and user["level"] > 1:
        user["level"] -= 1
        user["xp"] += xp_for_next_level(user["level"])
        leveled_down = True

    if user["level"] == 1 and user["xp"] < 0:
        user["xp"] = 0

    update_user(target, **user)

    if leveled_down:
        await message.reply(f"⬇️ {user['name']} понижен до уровня <b>{user['level']}</b>")
    else:
        await message.reply(f"➖ {user['name']} потерял {amount} XP")

# =============== /top ===============
@dp.message(Command("top"))
async def top_cmd(message: types.Message):
    data = load_data()
    sorted_users = sorted(data.values(), key=lambda u: (u['level'], u['xp']), reverse=True)

    text = "🏆 <b>Топ игроков:</b>\n\n"
    for i, u in enumerate(sorted_users[:10], start=1):
        text += f"{i}. {u['name']} — уровень <b>{u['level']}</b> (XP: {u['xp']})\n"

    await message.reply(text)

# =============== АВТО XP ОТКЛЮЧЕНО ===============
# Бот больше не выдаёт XP за сообщения.

# =============== СТАРТ ===============
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
