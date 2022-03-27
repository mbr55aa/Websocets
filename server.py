"""Just a stupid simple websocket server."""
import asyncio

import config
import websockets

people = {}


async def man(websocket: websockets.WebSocketServerProtocol):
    """
    Manual.

    Show manual with all supported commands.
    :param websocket:
    """
    await websocket.send('Чтобы поговорить, напишите "<имя>: <сообщение>". Например: Ира: купи хлеб.')
    await websocket.send('Посмотреть список участников можно командой "?"')


async def welcome(websocket: websockets.WebSocketServerProtocol) -> str:
    """
    Welcome.

    :param websocket:
    :return: name of person
    """
    await websocket.send('Представьтесь!')
    while True:
        name = await websocket.recv()
        name_web = name.strip()
        if name_web not in people:
            break
        await websocket.send('Это имя уже занято, попробуйте другое!')
    await man(websocket)
    people[name] = websocket
    return name


async def receiver(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """
    Connection handler.

    :param websocket:
    :param path: not used yet
    :return: None
    """
    name = await welcome(websocket)
    name_web = name.strip()
    while True:
        try:
            message = (await websocket.recv()).strip()
        except websockets.exceptions.ConnectionClosedError:
            del people[name_web]
            break
        if message == '?':
            await websocket.send(', '.join(people.keys()))
            continue
        else:
            try:
                to, text = message.split(': ', 1)
            except ValueError:
                await man(websocket)
                continue
            if to in people:
                await people[to].send(f'Сообщение от {name}: {text}')
            else:
                await websocket.send(f'Пользователь {to} не найден')


if __name__ == '__main__':
    # Создаём сервер, который будет обрабатывать подключения
    ws_server = websockets.serve(receiver, config.SERVER_HOST, config.SERVER_PORT)

    # Запускаем event-loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ws_server)
    loop.run_forever()
