import asyncio
from asyncio import Semaphore
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime
from typing import Iterable

import questionary
from aiohttp.client_exceptions import ContentTypeError
from better_web3 import Chain, JSONRPCException, Wallet, Proxy
from eth_typing import HexStr
from eth_utils import from_wei, to_wei
from tqdm.asyncio import tqdm
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError
from web3.types import Wei

from .chains import CHAINS as _CHAINS
from .logger import logger


CHAINS = {chain.name: chain for chain in _CHAINS.values()}


def ask_chain() -> Chain:
    chain_name = questionary.select(f"Choose a chain:", choices=CHAINS).ask()
    return CHAINS[chain_name]


def ask_private_key() -> str:
    return questionary.password(f"Enter a private key:").ask()


def curry_async(async_func):
    async def curried(*args, **kwargs):
        def bound_async_func(*args2, **kwargs2):
            return async_func(*(args + args2), **{**kwargs, **kwargs2})
        return bound_async_func
    return curried


async def sleep(wallet: Wallet, delay: float):
    logger.info(f"{wallet} Sleeping {delay} sec.")
    await asyncio.sleep(delay)


async def process_wallet(semaphore: Semaphore, fn, wallet: Wallet):
    async with semaphore:
        try:
            await fn(wallet)
        except Exception as e:
            logger.error(f"{wallet} Wallet was skipped: {e}")
            return


async def process_proxy(semaphore: Semaphore, fn, proxy: Proxy):
    async with semaphore:
        try:
            await fn(proxy)
        except Exception as e:
            logger.error(f"{proxy} Proxy was skipped: {e}")
            return


async def process_wallets(wallets: Iterable[Wallet], fn, max_tasks: int = 100):
    if not wallets:
        logger.warning(f"There are no wallets!")
        return

    semaphore = Semaphore(max_tasks)
    tasks = [process_wallet(semaphore, fn, wallet) for wallet in wallets]
    await tqdm.gather(*tasks)


async def process_proxies(proxies: Iterable[Proxy], fn, max_tasks: int = 100):
    if not proxies:
        logger.warning(f"There are no proxies!")
        return

    semaphore = Semaphore(max_tasks)
    tasks = [process_proxy(semaphore, fn, proxy) for proxy in proxies]
    await tqdm.gather(*tasks)
