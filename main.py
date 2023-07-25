import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from config_data.config import Config, load_config
from keywords.main_menu_kb import set_main_menu
from handlers import start_handlers, other_handlers

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
redis: Redis = Redis(host='localhost')
storage: RedisStorage = RedisStorage(redis=redis)

# Инициализация бота и диспетчера
bot: Bot = Bot(config.tg_bot.token)
dp: Dispatcher = Dispatcher(storage=storage)
dp.include_router(start_handlers.router)
dp.include_router(other_handlers.router)

# Задаем меню бота, пропускаем накопившиеся апдейты и запускаем polling
async def main():
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=60)

if __name__ == '__main__':
    asyncio.run(main())