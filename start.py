import questionary
import asyncio

from scripts.scripts import (
    generate_wallets,
    private_keys_to_address,
    disperse_native_tokens,
    native_token_balances,
    check_proxies,
    transfer_from_wallet_to_address,
)


MODULES = {
    "Generate wallets": generate_wallets,
    "Check proxies": check_proxies,
    "Private keys to addresses": private_keys_to_address,
    "Disperse native tokens": disperse_native_tokens,
    "Transfer (Wallet -> Addresses)": transfer_from_wallet_to_address,
    "Native token balances": native_token_balances,
}


async def main():
    while True:
        module_name = await questionary.select("What do you want?", choices=list(MODULES.keys())).ask_async()
        await MODULES[module_name]()
        print(f"Ctrl + C to exit")  # TODO сделать функцию выхода


if __name__ == '__main__':
    asyncio.run(main())
