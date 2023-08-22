import asyncio
from asyncio import Semaphore
from typing import Iterable

from better_web3 import Wallet
from tqdm.asyncio import tqdm

from .logger import logger
from .proxy import Proxy


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
