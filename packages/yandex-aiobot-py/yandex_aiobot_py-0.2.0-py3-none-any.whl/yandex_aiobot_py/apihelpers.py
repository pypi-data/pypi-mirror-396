import os
from typing import Optional, Dict, Any, List
import aiohttp
import aiofiles
import asyncio
from typing import Optional, Dict, Any
import json
from yandex_aiobot_py.bot_types import Poll, Chat  # Import Poll, Button

BASE_URL = "https://botapi.messenger.yandex.net/bot/v1"


def clear_kwargs_values(new_data: Dict[str, Any]) -> Dict[str, Any]:
    """удаляет из словаря элементы с пустыми значениями."""
    return {k: v for k, v in new_data.items() if v}


async def _check_result(resp: aiohttp.ClientResponse) -> None:
    if not isinstance(resp, aiohttp.ClientResponse):
        raise ValueError("resp должен быть объектом aiohttp.ClientResponse")
    if resp.status != 200:
        try:
            error = await resp.json()
        except aiohttp.ContentTypeError:
            error = await resp.text()
        raise Exception(f"API Error {resp.status}: {error}")


async def _make_request(
    client: Any,
    method_url: str,
    method: str,
    data: Optional[Dict[str, Any]] = None,
    session: Optional[aiohttp.ClientSession] = None,
) -> Dict[str, Any]:
    if not isinstance(method_url, str):
        raise ValueError("method_url должен быть строкой")
    if not isinstance(method, str):
        raise ValueError("method должен быть строкой")
    if data is not None and not isinstance(data, dict):
        raise ValueError("data должен быть словарем")
    if session is not None and not isinstance(session, aiohttp.ClientSession):
        raise ValueError("session должен быть объектом aiohttp.ClientSession")
    headers = {
        "Authorization": f"OAuth {client.api_key}",
        "Content-Type": "application/json",
    }

    url = f"{BASE_URL}{method_url}"

    own_session = False
    aiotimeout = aiohttp.ClientTimeout(total=30)  # Таймаут 30 секунд
    if session is None:
        session = aiohttp.ClientSession(timeout=aiotimeout)
        own_session = True

    try:
        if method.upper() == "GET":
            async with session.get(
                url, headers=headers, params=data, ssl=client.ssl_verify
            ) as resp:
                await _check_result(resp)
                return await resp.json()

        elif method.upper() == "POST":
            async with session.post(
                url, headers=headers, json=data, ssl=client.ssl_verify
            ) as resp:
                await _check_result(resp)
                return await resp.json()

        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except asyncio.TimeoutError:
        raise Exception("Запрос превысил время ожидания (таймаут)")
    except asyncio.CancelledError:
        # Здесь можно логировать или пробросить дальше
        raise
    except aiohttp.ClientError as e:
        raise Exception(f"Network error: {str(e)}") from e

    finally:
        if own_session:
            await session.close()


async def _download_file(
    client,
    method_url: str,
    file_id: str,
    file_path: str,
    session: Optional[aiohttp.ClientSession] = None,
):
    url = f"{BASE_URL}{method_url}"
    headers = {"Authorization": f"OAuth {client.api_key}"}

    own_session = False
    if session is None:
        session = aiohttp.ClientSession()
        own_session = True

    try:
        async with session.get(
            url, headers=headers, params={"file_id": file_id}, ssl=client.ssl_verify
        ) as resp:
            await _check_result(resp)

            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024):
                    await f.write(chunk)

            return file_path
    finally:
        if own_session:
            await session.close()


async def _make_file_request(
    client,
    method_url: str,
    data: Dict[str, Any],
    session: Optional[aiohttp.ClientSession] = None,
):
    url = f"{BASE_URL}{method_url}"
    headers = {"Authorization": f"OAuth {client.api_key}"}

    form = aiohttp.FormData()

    for key, value in data.items():
        if isinstance(value, str) and os.path.isfile(value):
            # Асинхронно читаем файл в память и добавляем как байты
            # async with aiofiles.open(value, "rb") as f:
            #     content = await f.read()
            # form.add_field(
            #     key,
            #     content,
            #     filename=os.path.basename(value),
            #     content_type="application/octet-stream",
            # )
            form.add_field(
                key, open(value, "rb"), filename=os.path.basename(value)
            )  # Stream, без чтения в память
        else:
            form.add_field(key, str(value))

    own_session = False
    if session is None:
        session = aiohttp.ClientSession()
        own_session = True

    try:
        async with session.post(
            url, headers=headers, data=form, ssl=client.ssl_verify
        ) as resp:
            await _check_result(resp)
            return await resp.json()
    finally:
        if own_session:
            await session.close()


async def get_updates(
    client: Any,
    last_update_id: int = 0,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[Dict[str, Any]]:
    if not isinstance(last_update_id, int):
        raise ValueError("last_update_id должен быть целым числом")
    if session is not None and not isinstance(session, aiohttp.ClientSession):
        raise ValueError("session должен быть объектом aiohttp.ClientSession")

    try:
        data = await _make_request(
            client,
            f"/messages/getUpdates?offset={last_update_id}&limit=5",
            "GET",
            session=session,
        )
        return data["updates"]
    except KeyError:
        return []


async def send_message(
    client: Any,
    text: str,
    session: Optional[aiohttp.ClientSession] = None,
    **kwargs: Any,
) -> int:
    if not isinstance(text, str):
        raise ValueError("text должен быть строкой")
    if session is not None and not isinstance(session, aiohttp.ClientSession):
        raise ValueError("session должен быть объектом aiohttp.ClientSession")
    data = {"text": text}
    data.update(clear_kwargs_values(kwargs))

    response = await _make_request(
        client, "/messages/sendText/", "POST", data, session=session
    )
    return response["message_id"]


async def create_poll(
    client: Any,
    poll: Poll,
    session: Optional[aiohttp.ClientSession] = None,
    **kwargs: Any,
) -> int:
    if not isinstance(poll, Poll):
        raise ValueError("poll должен быть объектом Poll")
    if session is not None and not isinstance(session, aiohttp.ClientSession):
        raise ValueError("session должен быть объектом aiohttp.ClientSession")
    data = {**poll.to_dict(), **clear_kwargs_values(kwargs)}
    response = await _make_request(
        client, "/messages/createPoll/", "POST", data, session=session
    )
    return response["message_id"]


async def get_poll_results(
    client: Any,
    message_id: int,
    session: Optional[aiohttp.ClientSession] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    if not isinstance(message_id, int):
        raise ValueError("message_id должен быть целым числом")
    if session is not None and not isinstance(session, aiohttp.ClientSession):
        raise ValueError("session должен быть объектом aiohttp.ClientSession")
    data = {"message_id": int(message_id), **clear_kwargs_values(kwargs)}
    response = await _make_request(
        client, "/polls/getResults/", "GET", data, session=session
    )
    return response


async def get_poll_voters(
    client: Any,
    message_id: int,
    answer_id: int,
    session: Optional[aiohttp.ClientSession] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    if not isinstance(message_id, int):
        raise ValueError("message_id должен быть целым числом")
    data = {
        "message_id": message_id,
        "answer_id": answer_id,
        **clear_kwargs_values(kwargs),
    }
    return await _make_request(
        client, "/polls/getVoters/", "GET", data, session=session
    )


async def chat_create(
    client, chat: Chat, session: Optional[aiohttp.ClientSession] = None, **kwargs
):
    data = {**chat.to_dict(), **clear_kwargs_values(kwargs)}
    response = await _make_request(
        client, "/chats/create/", "POST", data, session=session
    )
    return response["chat_id"]


async def change_chat_users(
    client, data: Dict[str, Any], session: Optional[aiohttp.ClientSession] = None
):
    return await _make_request(
        client, "/chats/updateMembers/", "POST", data, session=session
    )


async def get_file(
    client,
    file_id: str,
    file_path: str,
    session: Optional[aiohttp.ClientSession] = None,
) -> str:
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    await _download_file(
        client, "/messages/getFile/", file_id, file_path, session=session
    )
    return file_path


async def get_file_info(file_info: dict) -> tuple:
    """Метод для получения id и name из словаря файла."""
    file_id = file_info.get("id")
    file_name = file_info.get("name")
    return file_id, file_name


async def save_file(file_name: str, file_data: bytes, directory: str = ".") -> str:
    """Метод для сохранения файла в указанной папке."""
    # Создаем путь для сохранения файла
    save_path = os.path.join(directory, file_name)
    # Сохраняем файл
    with open(save_path, "wb") as f:
        f.write(file_data)
    return save_path  # Возвращаем путь к сохраненному файлу


async def delete_message(
    client, message_id: int, session: Optional[aiohttp.ClientSession] = None, **kwargs
):
    data = {"message_id": message_id, **clear_kwargs_values(kwargs)}
    response = await _make_request(
        client, "/messages/delete/", "POST", data, session=session
    )
    return response["message_id"]


async def get_user_link(
    client, login: str, session: Optional[aiohttp.ClientSession] = None
):
    data = {"login": login}
    response = await _make_request(
        client, "/users/getUserLink/", "GET", data, session=session
    )
    return response


async def send_file(client, session: Optional[aiohttp.ClientSession] = None, **kwargs):
    data = clear_kwargs_values(kwargs)
    if "document" not in data:
        raise ValueError("Missing 'document' parameter")

    if not os.path.isfile(data["document"]):
        raise FileNotFoundError(f"File not found: {data['document']}")

    return await _make_file_request(
        client, "/messages/sendFile/", data, session=session
    )


async def send_image(client, session: Optional[aiohttp.ClientSession] = None, **kwargs):
    data = clear_kwargs_values(kwargs)
    if "image" not in data:
        raise ValueError("Missing 'image' parameter")

    if not os.path.isfile(data["image"]):
        raise FileNotFoundError(f"Image not found: {data['image']}")

    return await _make_file_request(
        client, "/messages/sendImage/", data, session=session
    )


async def get_image_info(image_info: str) -> tuple[str, str]:
    # Разделяем строку по запятой
    parts = image_info.split(", ")
    # Извлекаем id из первой части
    image_id = parts[0].split(" ")[2]  # Получаем id из первой части
    # Извлекаем имя файла из второй части
    image_name = parts[1]  # Получаем имя файла из второй части

    return image_id, image_name
