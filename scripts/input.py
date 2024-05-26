from collections import defaultdict

from eth_account import Account
from eth_utils import to_checksum_address

from common.utils import load_lines

from .paths import ADDRESSES_TXT, PRIVATE_KEYS_TXT, PRIVATE_KEY_TO_ADDRESS_TXT


ADDRESSES = [to_checksum_address(line) for line in load_lines(ADDRESSES_TXT)]
print(f"Addresses: {len(ADDRESSES)}")

WALLETS = [Account.from_key(line) for line in load_lines(PRIVATE_KEYS_TXT)]
print(f"Wallets (private keys): {len(WALLETS)}")

PRIVATE_KEY_TO_ADDRESSES = defaultdict(list)
for private_key, address in [line.split(":") for line in load_lines(PRIVATE_KEY_TO_ADDRESS_TXT)]:
    PRIVATE_KEY_TO_ADDRESSES[private_key].append(address)
print(f"Private keys ({len(PRIVATE_KEY_TO_ADDRESSES.keys())}) to addresses (?)")
