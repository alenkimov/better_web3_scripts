import questionary

from scripts.scripts import (
    generate_wallets,
    private_keys_to_address,
    disperse_native_tokens,
    native_token_balances,
)


MODULES = {
    "Generate wallets": generate_wallets,
    "Private keys to addresses": private_keys_to_address,
    "Disperse native tokens": disperse_native_tokens,
    "Native token balances": native_token_balances,
}


def main():
    while True:
        module_name = questionary.select("What do you want?", choices=list(MODULES.keys())).ask()
        MODULES[module_name]()
        print(f"Ctrl + C to exit")  # TODO сделать функцию выхода


if __name__ == '__main__':
    main()
