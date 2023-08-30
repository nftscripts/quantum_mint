import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET
from loguru import logger

from starknet_py.net.signer.stark_curve_signer import (
    StarkCurveSigner,
    KeyPair,
)

from config import (
    WALLET_TYPE,
    RPC_URL,
)


class Wallet:
    def __init__(self, private_key: str) -> None:
        private_key = re.sub(r'[^0-9a-fA-F]+', '', private_key)
        private_key = int(private_key, 16)
        if WALLET_TYPE.lower() == 'argent':
            proxy_class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
            implementation_class_hash = 0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
        elif WALLET_TYPE.lower() == 'braavos':
            proxy_class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            implementation_class_hash = 0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570
        else:
            logger.error(f'Unknown wallet type {WALLET_TYPE} | Use only: argent/braavos.')
            return
        if WALLET_TYPE.lower() == 'argent':
            selector = get_selector_from_name("initialize")
        else:
            selector = get_selector_from_name("initializer")
        key_pair = KeyPair.from_private_key(private_key)
        if WALLET_TYPE == 'argent':
            calldata = [key_pair.public_key, 0]
        else:
            calldata = [key_pair.public_key]
        address = compute_address(
            class_hash=proxy_class_hash,
            constructor_calldata=[implementation_class_hash, selector, len(calldata), *calldata],
            salt=key_pair.public_key
        )
        self.account = Account(
            address=address,
            client=FullNodeClient(
                node_url=RPC_URL) if RPC_URL != 'https://alpha-mainnet.starknet.io' else GatewayClient(net=MAINNET),
            signer=StarkCurveSigner(
                account_address=address,
                key_pair=key_pair,
                chain_id=StarknetChainId.MAINNET
            )
        )
        logger.info(f'Wallet | [{hex(self.account.address)}]')

    async def get_balance(self) -> int:
        balance = await self.account.get_balance(0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7)
        return balance
