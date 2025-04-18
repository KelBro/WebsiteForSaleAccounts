import asyncio
import threading
import os
from website.run import run_website
from bot.telegram_bot import run_bot
from website.data import db_session


def init_db():
    # Используйте относительный путь от корня проекта
    db_path = os.path.join(os.path.dirname(__file__), "website/db/accounts.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)

    # Тестовая сессия для проверки
    try:
        session = db_session.create_session()
        session.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise


async def main():
    init_db()  # Явная инициализация перед запуском

    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_website, daemon=True)
    flask_thread.start()

    # Запускаем бота в основном потоке
    await run_bot()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Application failed: {e}")