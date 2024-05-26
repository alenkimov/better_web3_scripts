import inspect
from typing import Callable

import questionary
import asyncio

from scripts.config import CONFIG
from scripts.paths import LOG_DIR
from common.logger import setup_logger
from common.author import print_author_info, open_channel
from common.project import print_project_info

from scripts.scripts import (
    generate_wallets,
    private_keys_to_address,
    native_token_balances,
    transfer_from_wallet_to_address,
    comet_bridge,
)

setup_logger(LOG_DIR, CONFIG.LOGGING.LEVEL)


MODULES = {
    "❤️ Channel": open_channel,
    "Generate wallets": generate_wallets,
    "Private keys to addresses": private_keys_to_address,
    "Transfer (Wallet -> Addresses)": transfer_from_wallet_to_address,
    "Native token balances": native_token_balances,
    # "Comet bridge (ETH OP -> Mintchain)": comet_bridge,
    "Quit": quit,
}


def select_module(modules: dict[str: Callable]) -> Callable:
    module_name = questionary.select("Select module:", choices=modules).ask()
    return modules[module_name]


def main():
    print_project_info()
    print_author_info()
    while True:
        fn = select_module(MODULES)
        if inspect.iscoroutinefunction(fn):
            asyncio.run(fn())
        else:
            fn()


if __name__ == '__main__':
    main()
