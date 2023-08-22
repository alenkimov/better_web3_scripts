from collections import defaultdict

from better_web3.utils import addresses_from_file, load_lines
from better_web3 import Wallet

from .logger import logger
from .paths import PROXIES_TXT, ADDRESSES_TXT, PRIVATE_KEYS_TXT, PRIVATE_KEY_TO_ADDRESS_TXT
from .proxy import Proxy


PROXIES = Proxy.from_file(PROXIES_TXT)
logger.info(f"Proxies: {len(PROXIES)}")

ADDRESSES = addresses_from_file(ADDRESSES_TXT)
logger.info(f"Addresses: {len(ADDRESSES)}")

WALLETS = Wallet.from_file(PRIVATE_KEYS_TXT)
logger.info(f"Private keys: {len(WALLETS)}")

PRIVATE_KEY_TO_ADDRESSES = defaultdict(list)
for private_key, address in [line.split(":") for line in load_lines(PRIVATE_KEY_TO_ADDRESS_TXT)]:
    PRIVATE_KEY_TO_ADDRESSES[private_key].append(address)
logger.info(f"Private keys ({len(PRIVATE_KEY_TO_ADDRESSES.keys())}) to addresses (?)")
