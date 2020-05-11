#!/usr/bin/env python
import trio
from trio_websocket import serve_websocket, ConnectionClosed

connections = 0
messages = 0


async def echo_server(request):
    global connections
    global messages

    ws = await request.accept()
    connections += 1
    while True:
        try:
            message = await ws.get_message()
            await ws.send_message(message)
            messages += 1
        except ConnectionClosed:
            break
    connections -= 1


async def status_printer():
    global connections
    global messages
    while True:
        messages_before_sleep = messages
        await trio.sleep(1)
        messages_per_second = messages - messages_before_sleep
        print(f'{connections=}, {messages_per_second=}')


async def main():
    ssl_context = None
    async with trio.open_nursery() as nursery:
        nursery.start_soon(status_printer)
        nursery.start_soon(serve_websocket, echo_server, '0.0.0.0', 8000, ssl_context)

trio.run(main)