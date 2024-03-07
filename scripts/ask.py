from better_web3 import Chain
import questionary


from .config import CHAINS

CHAINS_TO_CHOOSE = {chain.name: chain for chain in CHAINS.values()}


async def ask_chain() -> Chain:
    chain_name = await questionary.select(f"Choose a chain:", choices=CHAINS_TO_CHOOSE).ask_async()
    return CHAINS_TO_CHOOSE[chain_name]


async def ask_private_key() -> str:
    return await questionary.password(f"Enter a private key:").ask_async()
