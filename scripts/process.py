import asyncio
from asyncio import Semaphore
from typing import Iterable

from eth_account.signers.local import LocalAccount
from tqdm.asyncio import tqdm

from loguru import logger


async def sleep(wallet: LocalAccount, delay: float):
    logger.info(f"[{wallet.address}] Sleeping {delay} sec...")
    await asyncio.sleep(delay)


async def process_wallet(semaphore: Semaphore, fn, wallet: LocalAccount):
    async with semaphore:
        try:
            await fn(wallet)
        except Exception as e:
            logger.error(f"[{wallet.address}] Wallet was skipped: {e}")
            return


async def process_wallets(wallets: Iterable[LocalAccount], fn, max_tasks: int = 100):
    if not wallets:
        logger.warning(f"There are no wallets!")
        return

    semaphore = Semaphore(max_tasks)
    tasks = [process_wallet(semaphore, fn, wallet) for wallet in wallets]
    await tqdm.gather(*tasks)
