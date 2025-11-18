import asyncio
from .main_bot import bot, dp
import main.commands  # подключаем команды


async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
