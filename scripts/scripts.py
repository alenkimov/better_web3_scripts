import asyncio
import os
import webbrowser
from typing import Iterable

import aiohttp
import questionary
import tqdm
from tqdm.asyncio import tqdm as async_tqdm
from better_web3 import Chain
from better_web3.utils import write_lines, addresses_from_file
from better_web3 import Wallet
from eth_typing import ChecksumAddress
from eth_utils import to_wei, from_wei
from web3.types import Wei


from .config import CONFIG
from .logger import logger
from .paths import INPUT_DIR, OUTPUT_DIR
from .proxy import Proxy, ProxyInfo
from ._scripts import process_proxies, curry_async, ask_chain, ask_private_key

PROXIES_TXT = INPUT_DIR / "proxies.txt"
ADDRESSES_TXT = INPUT_DIR / "addresses.txt"
PRIVATE_KEYS_TXT = INPUT_DIR / "private_keys.txt"

INPUT_FILES = [PROXIES_TXT, ADDRESSES_TXT, PRIVATE_KEYS_TXT]

for filepath in INPUT_FILES:
    filepath.touch(exist_ok=True)

PROXIES = Proxy.from_file(PROXIES_TXT)
logger.info(f"Proxies: {len(PROXIES)}")

ADDRESSES = addresses_from_file(ADDRESSES_TXT)
logger.info(f"Addresses: {len(ADDRESSES)}")

WALLETS = Wallet.from_file(PRIVATE_KEYS_TXT)
logger.info(f"Private keys: {len(WALLETS)}")


def native_token_balances():
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = ask_chain()
    balances_generator = chain.batch_request.balances(ADDRESSES, raise_exceptions=False)

    balances_txt = OUTPUT_DIR / "balances.txt"
    balances = []

    for i, balance_data in enumerate(balances_generator, start=1):
        address = balance_data["address"]
        if "balance" in balance_data:
            balance = from_wei(balance_data["balance"], "ether")
            logger.info(f"[{i:03}] [{address}] {chain} {chain.token.symbol} {round(balance, 4)}")
            balances.append(f"{address}:{balance}")
        else:
            exception = balance_data["exception"]
            logger.error(f"[{i:03}] [{address}] {chain} {exception}")
            balances.append(f"{address}:ERROR")

    write_lines(balances_txt, balances)

    if CONFIG.AUTO_OPEN:
        webbrowser.open(balances_txt)


def transfer_native_tokens(
        chain: Chain,
        wallets_from: list[Wallet],
        addresses_to: list[ChecksumAddress],
        value: Wei | int,
        wait_for_tx_receipt: bool = False,
):
    for wallet, address in zip(wallets_from, addresses_to):
        tx_hash = chain.transfer(wallet.account, address, value, gas_price=to_wei(1.5, "gwei"))
        tx_hash_link = chain.get_link_by_tx_hash(tx_hash)
        logger.info(f"{wallet} {tx_hash_link}")
        logger.info(f"\tSent {from_wei(value, 'ether')} {chain.token.symbol} to {address}")
        if wait_for_tx_receipt:
            tx_receipt = chain.wait_for_tx_receipt(tx_hash)
            tx_fee_wei = tx_receipt.gasUsed * tx_receipt.effectiveGasPrice
            tx_fee = from_wei(tx_fee_wei, "ether")
            logger.info(f"\tFee: {tx_fee} {chain.token.symbol}")


def _disperse_native_tokens(
        chain: Chain,
        wallet: Wallet,
        addresses_to: list[ChecksumAddress],
        values: list[Wei | int],
        wait_for_tx_receipt: bool = True,
):
    total_value_wei = sum(values)
    wallet_balance_wei = chain.get_balance(wallet.address)
    if total_value_wei > wallet_balance_wei:
        logger.error(f"{total_value_wei} > {wallet_balance_wei}")
        return
    else:
        logger.info(f"{wallet} {from_wei(wallet_balance_wei, 'ether')}")

    logger.info(f"Transferring {chain.token.symbol} {from_wei(total_value_wei, 'ether')} from {wallet.address} to:")
    for recipient, value in zip(addresses_to, values):
        logger.info(f" ==[{chain.token.symbol} {from_wei(value, 'ether')}]==>> {recipient}")
    """output
    Transferring gETH 0.02 from 0x780afe4a82Ed3B46eA6bA94a1BB8F7b977298722 to:
     ==[gETH 0.01]==>> 0xd87Fa8ac81834c6625519589C38Cb54899F1FBA5
     ==[gETH 0.01]==>> 0xc278c6B61C33A97e39cE5603Caa8A0235839B2b0
    """

    disperse_ether_fn = chain.disperse.disperse_ether(addresses_to, values)
    tx = chain.build_tx(disperse_ether_fn, address_from=wallet.address, value=total_value_wei)
    tx_hash = chain.sign_and_send_tx(wallet.account, tx)
    logger.info(f"tx: {chain.get_link_by_tx_hash(tx_hash)}")
    """output
    tx: https://goerli.etherscan.io/tx/0xdb7a3a03c49752aabb96207508269493eb35762249ad1b4e90a97685cb899571
    """

    if wait_for_tx_receipt:
        chain.wait_for_tx_receipt(tx_hash)


def disperse_native_tokens():
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = ask_chain()

    private_key = ask_private_key()
    wallet = Wallet.from_key(private_key)
    logger.info(f"{wallet}")

    value = questionary.text(f"Enter value (float):").ask()
    try:
        value = float(value)
    except ValueError:
        logger.error(f"Wrong float value")
        return
    values = [to_wei(value, "ether")] * len(ADDRESSES)
    logger.info(f"To send: {value} {chain.token.symbol}")

    _disperse_native_tokens(chain, wallet, ADDRESSES, values)


def private_keys_to_address():
    if not WALLETS:
        logger.warning(f"There are no private keys!")
        return

    wallets_txt = OUTPUT_DIR / "wallets.txt"
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in WALLETS])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)


def generate_wallets():
    value = questionary.text(f"Enter count (int):").ask()
    try:
        count = int(value)
    except ValueError:
        logger.error(f"Wrong int value")
        return

    wallets_txt = OUTPUT_DIR / "wallets.txt"
    wallets = [Wallet.generate() for _ in tqdm.trange(count)]
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in wallets])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)


async def request_and_set_proxy_info(session: aiohttp.ClientSession, proxy: Proxy):
    async with session.get(f"https://ipapi.co/json/", proxy=proxy.as_url) as response:
        data = await response.json()
        proxy.info = ProxyInfo(**data)
        logger.success(f"{proxy} {proxy.info.country_name}")


async def request_proxies_info_aiohttp(proxies: Iterable[Proxy]):
    async with aiohttp.ClientSession() as session:
        await process_proxies(proxies, await curry_async(request_and_set_proxy_info)(session))


def check_proxies():
    asyncio.run(request_proxies_info_aiohttp(PROXIES))
