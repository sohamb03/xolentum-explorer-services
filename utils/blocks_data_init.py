#!/usr/bin/python3

import json
from pathlib import Path

import requests
from tqdm import tqdm

with open(Path(__file__).parent / '../config.json') as f:
    data = json.load(f)

    host = data['daemon_host']
    port = data['daemon_port']
    ssl = data['ssl']

blocks_data = list()

current_height = requests.get(f'{"https" if ssl else "http"}://{host}:{port}/get_info')\
    .json()['height']

progress_bar = tqdm(range(1, current_height), unit=' blocks', desc='Progress', unit_scale=False)

till_height = current_height - current_height % 1000

for block_height in range(1, till_height + 1, 1000):
    # noinspection SpellCheckingInspection
    raw_data = requests.post(
        f'{"https" if ssl else "http"}://{host}:{port}/json_rpc',
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': '0',
            'method': 'get_block_headers_range',
            'params': {
                    'start_height': block_height,
                    'end_height': block_height + 1000,
                    }
            }),
        headers={
            'Content-type': 'application/json'
        }
    )\
        .json()['result']['headers']

    for header in raw_data:
        # noinspection SpellCheckingInspection
        blocks_data.append(
            {
                'height': header['height'],
                'block_size': header['block_size'],
                'already_generated_coins': header['already_generated_coins'],
                'difficulty': header['difficulty'],
                'num_txes': header['num_txes'],
                'reward': header['reward'],
                'timestamp': header['timestamp']
            }
        )

        progress_bar.update(1)

if current_height - till_height > 1:
    raw_data = requests.post(
        f'{"https" if ssl else "http"}://{host}:{port}/json_rpc',
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': '0',
            'method': 'get_block_headers_range',
            'params': {
                'start_height': till_height + 1,
                'end_height': current_height - 1,
            }
        }),
        headers={
            'Content-type': 'application/json'
        }
    ) \
        .json()['result']['headers']

    for header in raw_data:
        # noinspection SpellCheckingInspection
        blocks_data.append(
            {
                'height': header['height'],
                'block_size': header['block_size'],
                'already_generated_coins': header['already_generated_coins'],
                'difficulty': header['difficulty'],
                'num_txes': header['num_txes'],
                'reward': header['reward'],
                'timestamp': header['timestamp']
            }
        )

        progress_bar.update(1)

progress_bar.close()

blocks_data = json.dumps(blocks_data, indent=4)

with open(Path(__file__).parent / '../data/blocks-data.json', 'w') as f:
    f.write(blocks_data)
