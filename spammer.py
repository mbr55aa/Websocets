"""Simple spambot."""

import asyncio
import logging
import random
import string
import sys

import websockets

DEFAULT_URI = 'ws://localhost:8765'
DEFAULT_REPEAT = 3000  # 100

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def rand_string():
    """Random string generator."""
    return ''.join(random.choices(string.ascii_letters, k=4))


async def invade(websocket: websockets.WebSocketServerProtocol) -> str:
    """Greet the server and return spambot name."""
    name = rand_string()
    await websocket.send(name)
    [await websocket.recv() for _ in range(3)]
    logger.info(f'My name is {name}')
    return name


async def spammer(uri: str, repeat: int):
    """Connect to the server and send spam messages."""
    try:
        async with websockets.connect(uri) as websocket:
            name = await invade(websocket)
            while True:
                await asyncio.sleep(repeat / 1000)
                await websocket.send('?')
                people = (await websocket.recv()).strip().split(', ')
                people_str = ', '.join(people)
                logger.info(f'People: {people_str}')
                for person in people:
                    if person == name:
                        continue
                    message = f'{person}: {rand_string()}'
                    logger.info(message)
                    await websocket.send(message)
    except OSError:
        logger.critical('Cannot connect!')


if __name__ == '__main__':
    if len(sys.argv) > 3:
        print('Usage: python spammer [ws://server.address:port] [repeat period in milliseconds]')
        exit()
    repeat = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_REPEAT
    uri = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URI
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(spammer(uri, repeat))
    except KeyboardInterrupt:
        print('\nExit')
        exit()
