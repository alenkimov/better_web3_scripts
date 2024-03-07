import asyncio
import webbrowser
from typing import Iterable

import tqdm
import questionary
from better_web3 import Chain, Wallet
from better_web3.utils import write_lines
from eth_typing import ChecksumAddress
from eth_utils import to_wei, from_wei
from web3.types import Wei
from loguru import logger
import web3

from common.ask import ask_int, ask_float

from .config import CONFIG
from .paths import OUTPUT_DIR
from .input import ADDRESSES, PRIVATE_KEY_TO_ADDRESSES, WALLETS
from .ask import ask_chain, ask_private_key


async def native_token_balances():
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = await ask_chain()
    raw_balances = [raw_balance_data async for raw_balance_data in
                    chain.batch_request.balances(ADDRESSES, raise_exceptions=False)]

    balances_txt = OUTPUT_DIR / "balances.txt"
    balances = []

    for i, balance_data in enumerate(raw_balances, start=1):
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


async def transfer_native_tokens(
        chain: Chain,
        wallets_from: list[Wallet],
        addresses_to: list[ChecksumAddress],
        value: Wei | int,
        wait_for_tx_receipt: bool = False,
):
    for wallet, address in zip(wallets_from, addresses_to):
        tx_hash = await chain.transfer(wallet.account, address, value)
        logger.info(f"\tSent {from_wei(value, 'ether')} {chain.token.symbol} to {address}")
        if wait_for_tx_receipt:
            tx_receipt = await chain.wait_for_tx_receipt(tx_hash)
            logger.info(wallet.tx_receipt(chain, tx_receipt))
        else:
            logger.info(wallet.tx_hash(chain, tx_hash))


async def _disperse_native_tokens(
        chain: Chain,
        wallet: Wallet,
        addresses_to: list[ChecksumAddress],
        values: list[Wei | int],
        wait_for_tx_receipt: bool = True,
):
    total_value_wei = sum(values)
    wallet_balance_wei = await chain.get_balance(wallet.address)
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

    disperse_ether_fn = await chain.disperse.disperse_ether(addresses_to, values)
    tx = await chain.build_tx(disperse_ether_fn, address_from=wallet.address, value=total_value_wei)
    tx_hash = await chain.sign_and_send_tx(wallet.eth_account, tx)

    if wait_for_tx_receipt:
        tx_receipt = await chain.wait_for_tx_receipt(tx_hash)
        logger.info(wallet.tx_receipt(chain, tx_receipt))
    else:
        logger.info(wallet.tx_hash(chain, tx_hash))


async def transfer_from_wallet(wallet: Wallet, addresses: Iterable, chain: Chain, value):
    for address in addresses:
        tx_hash = await chain.transfer(wallet.eth_account, address, value)
        tx_receipt = await chain.wait_for_tx_receipt(tx_hash)
        logger.info(wallet.tx_receipt(chain, tx_receipt))
        await asyncio.sleep(10)


async def transfer_from_wallet_to_address():
    if not PRIVATE_KEY_TO_ADDRESSES:
        logger.warning(f"No wallets to transfer!")
        return

    chain = await ask_chain()

    transfer_types = {
        # "Transfer all balance",
        "Transfer to minimal balance": 1,
        "Transfer value": 2,
        # "Transfer random value",
        # "Transfer value (from file)",
    }

    transfer_type_name = await questionary.select(f"Choose a transfer type:", choices=transfer_types).ask_async()
    transfer_type_number = transfer_types[transfer_type_name]

    if transfer_type_number == 1:
        minimal_value = await ask_float("Enter minimal value:", min=0)
        minimal_value = to_wei(minimal_value, "ether")

        for private_key, addresses in PRIVATE_KEY_TO_ADDRESSES.items():
            wallet = Wallet.from_key(private_key)
            for address in addresses:
                balance = await chain.get_balance(wallet.address)
                logger.info(f"{wallet} {chain} {chain.token.symbol} balance: {from_wei(balance, 'ether')}")
                value_to_transfer = balance - minimal_value
                if value_to_transfer > 0:
                    logger.info(f"{wallet} -> {address} {chain} {chain.token.symbol} to transfer: {from_wei(value_to_transfer, 'ether')}")
                    tx_hash = await chain.transfer(wallet.eth_account, address, value_to_transfer)
                    logger.info(wallet.tx_hash(chain, tx_hash))
                    if CONFIG.TRANSACTION.WAIT_FOR_TX_RECEIPT:
                        try:
                            tx_receipt = await chain.wait_for_tx_receipt(tx_hash)
                            logger.info(wallet.tx_receipt(chain, tx_receipt))
                        except web3.exceptions.TimeExhausted as exc:
                            logger.warning(f"{wallet} {chain} {exc}")

    elif transfer_type_number == 2:
        value = await ask_float(min=0)
        value = to_wei(value, "ether")

        tasks = []
        for private_key, addresses in PRIVATE_KEY_TO_ADDRESSES.items():
            wallet = Wallet.from_key(private_key)
            tasks.append(transfer_from_wallet(wallet, addresses, chain, value))

        await asyncio.gather(*tasks)


async def disperse_native_tokens():
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = await ask_chain()

    private_key = await ask_private_key()
    wallet = Wallet.from_key(private_key)
    logger.info(f"{wallet}")

    value = await ask_float(min=0)
    values = [to_wei(value, "ether")] * len(ADDRESSES)
    logger.info(f"To send: {value} {chain.token.symbol}")

    await _disperse_native_tokens(chain, wallet, ADDRESSES, values)


async def private_keys_to_address():
    if not WALLETS:
        logger.warning(f"There are no private keys!")
        return

    wallets_txt = OUTPUT_DIR / "wallets.txt"
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in WALLETS])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)


async def generate_wallets():
    count = await ask_int("Enter count (int)", min=1)
    wallets_txt = OUTPUT_DIR / "wallets.txt"
    wallets = [Wallet.generate() for _ in tqdm.trange(count)]
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in wallets])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)
