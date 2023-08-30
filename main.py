from asyncio import sleep
import random

from typing import (
    Coroutine,
    Awaitable,
)

from asyncio import (
    gather,
    run
)

from loguru import logger

from src.quantum_mint.quantum_mint import Mint
from config import *

if WALLET_TYPE.lower() == 'argent':
    with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
        private_keys = [line.strip() for line in file]
elif WALLET_TYPE.lower() == 'braavos':
    with open('braavos_wallets.txt', 'r', encoding='utf-8-sig') as file:
        private_keys = [line.strip() for line in file]


async def main() -> None:
    tasks = []
    for private_key in private_keys:
        nft_buyer = Mint(private_key)
        task = nft_buyer.mint()
        tasks.append(task)
        sleep_time = random.randint(MIN_PAUSE, MAX_PAUSE)
        logger.info(f'Sleeping {sleep_time} seconds..')
        await sleep(sleep_time)
    await gather(*tasks)


def start_event_loop(awaitable: Awaitable[Coroutine]) -> None:
    run(awaitable)


if __name__ == '__main__':
    start_event_loop(main())
