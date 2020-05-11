#!/usr/bin/env python
description = """Stress utility for testing web-sockets servers.
You would probably need to increase number of open files/sockets allowed, please run
 
    ulimit -n 65535

Google 'ulimit -n' if got problems
"""

import trio
from trio_websocket import open_websocket_url
import argparse
import logging

# define command-line arguments
parser = argparse.ArgumentParser(description="Stress utility for testing web-sockets servers.")
parser.add_argument('-c', '--connections', type=int, help='number of connections', default=1000)
parser.add_argument('-m', '--messages', type=int, help='number of messages to pass via every connection',
                    default=100)
parser.add_argument('target', type=str, help='target web-server address, like "ws://127.0.0.1:8000"')
args = parser.parse_args()

url = args.target
number_of_connections = args.connections
number_of_messages = args.messages

# error counters
failed_connections_counter = 0
lost_connections_counter = 0

# success counters
msg_sent = 0
msg_received = 0


async def send_message_get_response(ws):
    global msg_sent
    global msg_received

    await ws.send_message('hello world')
    msg_sent += 1
    response = await ws.get_message()
    msg_received += 1


async def send_m_messages(m):
    global failed_connections_counter
    try:
        async with open_websocket_url(url) as ws:
            for _ in range(m):
                await send_message_get_response(ws)

    except OSError as ose:
        failed_connections_counter += 1
        logging.error(f'Connection attempt failed {ose}')


async def main():
    async with trio.open_nursery() as nursery:
        for _ in range(number_of_connections):
            nursery.start_soon(send_m_messages, number_of_messages)

print(description)
trio.run(main)


print(f'connections             = {number_of_connections}')
print(f'messages per connection = {number_of_messages}')
print(f'fail to connect         = {failed_connections_counter}')
print(f'lost connections        = {lost_connections_counter}')
print(f'messages sent           = {msg_sent}')
print(f'messages received       = {msg_received}')
