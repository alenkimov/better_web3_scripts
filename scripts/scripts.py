import asyncio
import random
import webbrowser
from typing import Iterable

import tqdm
import questionary
from better_web3 import Chain
from common.utils import write_lines
from eth_typing import ChecksumAddress
from eth_utils import to_wei, from_wei, to_checksum_address
from eth_account.signers.local import LocalAccount
from eth_account import Account
from web3.types import Wei
from loguru import logger
import web3

from common.ask import ask_int, ask_float

from .comet import CometBridge
from .config import CONFIG
from .paths import OUTPUT_DIR
from .input import ADDRESSES, PRIVATE_KEY_TO_ADDRESSES, WALLETS
from .ask import ask_chain
from .chains import get_chains
from .tx import tx_hash_info, tx_receipt_info


async def native_token_balances():
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = await ask_chain()

    balances_txt = OUTPUT_DIR / "balances.txt"
    with open(balances_txt, "w") as file:
        async for address, balance in chain.balances(ADDRESSES):
            print(address, balance)
            file.write("\n".join(f"{address}:{balance}"))

    if CONFIG.AUTO_OPEN:
        webbrowser.open(balances_txt)


async def transfer_native_tokens(
        chain: Chain,
        wallets_from: list[LocalAccount],
        addresses_to: list[ChecksumAddress],
        value: Wei | int,
        wait_for_tx_receipt: bool = False,
):
    for wallet, address in zip(wallets_from, addresses_to):
        tx_hash = await chain.transfer(wallet.account, address, value)
        logger.info(f"\tSent {from_wei(value, 'ether')} {chain.native_currency.symbol} to {address}")
        if wait_for_tx_receipt:
            tx_receipt = await chain.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(wallet.tx_receipt(chain, tx_receipt))
        else:
            logger.info(wallet.tx_hash(chain, tx_hash))


async def transfer_from_wallet(wallet: LocalAccount, addresses: Iterable, chain: Chain, value):
    for address in addresses:
        tx_hash = await chain.transfer(wallet, to_checksum_address(address), value)
        tx_receipt = await chain.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(tx_receipt_info(chain, wallet.address, tx_receipt, value))
        await asyncio.sleep(61)


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
            wallet = Account.from_key(private_key)
            for address in addresses:
                balance = await chain.eth.get_balance(wallet.address)
                logger.info(f"{wallet} {chain} {chain.native_currency.symbol} balance: {from_wei(balance, 'ether')}")
                value_to_transfer = balance - minimal_value
                if value_to_transfer > 0:
                    logger.info(f"{wallet} -> {address} {chain} {chain.native_currency.symbol} to transfer: {from_wei(value_to_transfer, 'ether')}")
                    tx_hash = await chain.transfer(wallet, to_checksum_address(address), value_to_transfer)
                    logger.info(tx_hash_info(chain, wallet.address, tx_hash))

    elif transfer_type_number == 2:
        value = await ask_float(min=0)
        value = to_wei(value, "ether")

        tasks = []
        for private_key, addresses in PRIVATE_KEY_TO_ADDRESSES.items():
            wallet = Account.from_key(private_key)
            tasks.append(transfer_from_wallet(wallet, addresses, chain, value))

        await asyncio.gather(*tasks)


async def private_keys_to_address():
    if not WALLETS:
        logger.warning(f"There are no wallets (private keys)!")
        return

    wallets_txt = OUTPUT_DIR / "wallets.txt"
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in WALLETS])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)


async def generate_wallets():
    count = await ask_int("Enter count (int)", min=1)
    wallets_txt = OUTPUT_DIR / "wallets.txt"
    wallets = [Account.create() for _ in tqdm.trange(count)]
    write_lines(wallets_txt, [f"{wallet.private_key}:{wallet.address}" for wallet in wallets])
    logger.success(f"Wallets data saved here: {wallets_txt}")

    if CONFIG.AUTO_OPEN:
        webbrowser.open(wallets_txt)


async def comet_bridge():
    if not WALLETS:
        logger.warning(f"There are no wallets (private keys)!")
        return

    # Optimism,     Mintchain
    original_chain, target_chain = get_chains((10, 185))

    print(f"Original chain: {original_chain}")
    print(f"Target chain: {target_chain}")

    original_chain_balances: dict[ChecksumAddress: Wei] = {}
    target_chain_balances: dict[ChecksumAddress: Wei] = {}

    print(f"original_chain_balances:")
    async for address, balance in original_chain.balances([wallet.address for wallet in WALLETS]):
        print(address, balance)
        original_chain_balances[address] = balance

    print(f"target_chain_balances:")
    async for address, balance in target_chain.balances([wallet.address for wallet in WALLETS]):
        print(address, balance)
        target_chain_balances[address] = balance

    only_empty_wallets = await questionary.confirm(f"Bridge only empty wallets?").ask_async()

    minimal_value = await ask_float("Enter minimal value:", min=0)
    minimal_value = to_wei(minimal_value, "ether")

    maximum_value = await ask_float("Enter maximum value:", min=0)
    maximum_value = to_wei(maximum_value, "ether")

    comet = CometBridge(original_chain)

    for wallet in WALLETS:
        original_chain_balance = original_chain_balances[wallet.address]

        if original_chain_balance == 0:
            logger.info(f"[{wallet.address}] Wallet skipped (empty original chain balance).")
            continue

        target_chain_balance = target_chain_balances[wallet.address]
        if only_empty_wallets and target_chain_balance > 0:
            logger.info(f"[{wallet.address}] Wallet skipped (non-empty target chain balance)."
                        f"\n\tBalance (Wei): {target_chain_balance}")
            continue

        value = random.randint(minimal_value, maximum_value)
        tx_hash = await comet.bridge_eth(wallet, value, await target_chain.eth.chain_id)
        print(tx_hash_info(comet.chain, wallet.address, tx_hash, value))
