#!/usr/bin/env python
""" You would probably need to increase number of files/sockets allowed to be opened:
 ulimit -n 65535

# run it before running the program,
# google it, if got problems
"""

import trio
from trio_websocket import serve_websocket, ConnectionClosed

websockets_connected = 0
number_of_messages = 0


async def echo_server(request):
    global websockets_connected
    global number_of_messages

    ws = await request.accept()
    websockets_connected += 1
    while True:
        try:
            message = await ws.get_message()
            await ws.send_message(message)
            number_of_messages += 1
        except ConnectionClosed:
            break
    websockets_connected -= 1


async def status_printer():
    global websockets_connected
    global number_of_messages
    while True:
        messages_before_sleep = number_of_messages
        await trio.sleep(1)
        messages_per_second = number_of_messages - messages_before_sleep
        print(f'{websockets_connected=}, {messages_per_second=}')


async def main():
    ssl_context = None
    async with trio.open_nursery() as nursery:
        nursery.start_soon(status_printer)
        nursery.start_soon(serve_websocket, echo_server, '0.0.0.0', 8000, ssl_context)

trio.run(main)
