# yandex-aiobot-py

**Современная асинхронная библиотека для создания ботов в Яндекс Мессенджере**

Простая. Надёжная. Без спама при старте. Работает в личке и группах.

[![PyPI version](https://img.shields.io/pypi/v/yandex-aiobot-py.svg)](https://pypi.org/project/yandex-aiobot-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/yandex-aiobot-py.svg)](https://pypi.org/project/yandex-aiobot-py/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Возможности

- Полностью асинхронная (asyncio + aiohttp)
- Автоматическое определение: личный чат или группа
- Inline-кнопки, опросы, фото, файлы
- `skip_old_messages=True` — **не отвечает на старые сообщения при старте**
- Простой декоратор `@bot.on_message`
- Поддержка callback-кнопок
- Минималистичный и понятный API

## Установка

```bash
pip install yandex-aiobot-py
```

## Пример использвания

```python
import asyncio
import logging
from yandex_aiobot_py.client import Client, Button, Message
import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    bot = Client(api_key=config.API_KEY, ssl_verify=False)

    @bot.on_message("/test")
    async def test_session_steps(message: Message):
        await bot.send_message(
            login=message.user.login,
            text="Пожалуйста, введите коротко тему обращения:",
        )
        await bot.register_next_step_handler(message.user.login, step_2)

    async def step_2(message: Message):
        # Шаг 2: Вопрос о подробной информации
        await bot.send_message(
            login=message.user.login,
            text="Пожалуйста, введите подробную информацию о вашей проблеме:",
            inline_keyboard=[
                await bot.create_universal_button(
                    text="Отмена",
                    phrase="/test_session_steps",
                    callback_data={"action": "cancel"},
                ),
            ],
        )
        await bot.register_next_step_handler(message.user.login, step_3)

    async def step_3(message: Message):
        # Шаг 3: Подтверждение обращения
        await bot.send_message(
            login=message.user.login,
            text="Вы уверены, что хотите отправить обращение?",
            inline_keyboard=[
                await bot.create_universal_button(
                    text="Да",
                    callback_data={"action": "confirm"},
                ),
                await bot.create_universal_button(
                    text="Нет",
                    callback_data={"action": "cancel"},
                ),
            ],
        )
        await bot.register_next_step_handler(message.user.login, step_4)

    async def step_4(message: Message):
        # Шаг 4: Завершение сессии
        if message.callback_data.get("action") == "confirm":
            await bot.send_message(
                login=message.user.login,
                text="Ваше обращение принято. Мы свяжемся с вами в ближайшее время.",
            )
        else:
            await bot.send_message(
                login=message.user.login,
                text="Обращение отменено.",
            )

    @bot.on_message("/start", chat_type="group")
    async def start_handler_g(message: Message):
        await bot.send_message(
            text="Вы обратились ко мне из группы!",
            chat_id=message.chat.chat_id,
        )

    @bot.on_message("/start", chat_type="private")
    async def start_handler_p(message: Message):
        await bot.send_message(
            text="Это личный чат.",
            login=message.user.login,
        )

    @bot.on_message("/image", chat_type="private")
    async def image_handler_p(message: Message):
        await bot.send_image(
            "/data/Script/Python/MyLibrary/yandex_aiobot_py/files/5435871924950525925.jpg",
            login=message.user.login,
        )

    @bot.on_message("/start")
    async def start_handler(message: Message):
        if message.chat and message.chat.chat_id:
            await bot.send_message(
                text="!!Вы обратились ко мне из группы!!!!",
                chat_id=message.chat.chat_id,
            )
        else:
            await bot.send_message(
                text="Это личный чат. 1",
                login=message.user.login,
            )

    @bot.on_message(r"/menu")
    async def show_menu(message: Message):
        btn = [
            Button(
                text="Выход",
                phrase="/exit_poll",
                callback_data={"actions": "exit_poll"},
            )
        ]

        await bot.send_message(
            text="Отправьте ссылку на чат",
            login=message.user.login,
            inline_keyboard=btn,
        )

    @bot.on_message(r".*")
    async def echo_handler(message: Message):
        chat_id = getattr(message.chat, "chat_id", None)
        logger.debug("Message chat_id: %s", chat_id)
        logger.debug("Message user login: %s", message.user.login)

        try:
            if chat_id:
                # Отправляем в чат, если chat_id есть
                await bot.send_message(
                    text=f"Вы написали: {message.text}", chat_id=chat_id
                )
            elif message.user and message.user.login:
                # Если chat_id нет, отправляем по логину пользователя
                await bot.send_message(
                    text=f"Вы написали: {message.text}", login=message.user.login
                )
            else:
                logger.warning(
                    "Не удалось определить chat_id или login для сообщения: %s", message
                )
        except Exception as e1:
            logger.exception("Ошибка при обработке сообщения: %s", e1)

    try:
        await bot.start_session()
        await bot.run()  # Запускаем метод run с асинхронным polling и watchdog
    except asyncio.CancelledError:
        logger.info("Bot stopped by cancellation")
    except Exception as e2:
        logger.exception("Произошла ошибка при запуске бота: %s", e2)
    finally:
        await bot.close_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
```