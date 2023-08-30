from asyncio import sleep
import random

from loguru import logger

from src.quantum_mint.utils.transaction import get_mint_call
from src.quantum_mint.utils.account import Wallet
from src.utils.decorators import retry

from config import (
    ESTIMATED_FEE_MULTIPLIER,
    MAX_FEE_FOR_TRANSACTION,
)


class Mint(Wallet):
    def __init__(self, private_key: str) -> None:
        super().__init__(private_key)

    @retry()
    async def mint(self) -> None:
        balance = await self.get_balance()
        if balance == 0:
            logger.error(f'Your balance is 0 | {hex(self.account.address)}')
            return

        mint_call = await get_mint_call(self.account.address)
        calls = [mint_call]

        while True:
            self.account.ESTIMATED_FEE_MULTIPLIER = ESTIMATED_FEE_MULTIPLIER
            invoke_tx = await self.account.sign_invoke_transaction(calls=calls, auto_estimate=True)
            estimate_fee = await self.account._estimate_fee(invoke_tx)
            if estimate_fee.overall_fee / 10 ** 18 > MAX_FEE_FOR_TRANSACTION:
                logger.info('Current fee is too high...')
                sleep_time = random.randint(45, 75)
                logger.info(f'Sleeping {sleep_time} seconds')
                await sleep(sleep_time)
                continue
            tx = await self.account.client.send_transaction(invoke_tx)
            logger.debug(f'Transaction sent. Waiting... | TX: https://voyager.online/tx/{hex(tx.transaction_hash)}')
            await sleep(15)
            await self.account.client.wait_for_tx(tx.transaction_hash)
            logger.success(
                f'Successfully minted NFT for address {hex(self.account.address)} | TX: https://voyager.online/tx/{hex(tx.transaction_hash)}'
            )
            break
