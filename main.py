import questionary
import asyncio

from scripts.config import CONFIG
from scripts.paths import LOG_DIR
from common.logger import setup_logger

from scripts.scripts import (
    generate_wallets,
    private_keys_to_address,
    disperse_native_tokens,
    native_token_balances,
    transfer_from_wallet_to_address,
)

setup_logger(LOG_DIR, CONFIG.LOGGING.LEVEL)

MODULES = {
    "Exit": None,
    "Generate wallets": generate_wallets,
    "Private keys to addresses": private_keys_to_address,
    "Disperse native tokens": disperse_native_tokens,
    "Transfer (Wallet -> Addresses)": transfer_from_wallet_to_address,
    "Native token balances": native_token_balances,
}


async def main():
    while True:
        module_name = await questionary.select("What do you want?", choices=list(MODULES.keys())).ask_async()
        module = MODULES[module_name]

        if module is None:
            quit()

        await module()


if __name__ == '__main__':
    asyncio.run(main())
