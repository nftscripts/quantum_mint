from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.cairo import felt


async def get_mint_call(address: felt) -> Call:
    mint_call = Call(to_addr=0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76,
                     selector=get_selector_from_name("mintPublic"),
                     calldata=[
                         address
                     ])
    return mint_call
