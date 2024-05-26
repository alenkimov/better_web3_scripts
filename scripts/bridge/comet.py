import json

from better_web3 import Contract
from eth_typing import ChecksumAddress
from web3.types import Wei, HexStr
from eth_utils import to_checksum_address
from eth_account.account import LocalAccount
from web3.contract.async_contract import AsyncContractFunction

from common.utils import load_json

from ..paths import ABI_DIR
from ..constants import ETH_ADDRESS


class CometBridge(Contract):
    ABI = load_json(ABI_DIR / "comet_bridge.json")
    DEFAULT_ADDRESS = to_checksum_address("0xB50Ac92D6d8748AC42721c25A3e2C84637385A6b")

    def _bridge(
            self,
            amount: int,
            token: ChecksumAddress,
            provider: ChecksumAddress,
            metadata: bytes,
    ) -> AsyncContractFunction:
        return self.contract.functions.bridge(amount, token, provider, metadata)

    async def bridge(
            self,
            wallet: LocalAccount,
            value: Wei | int,
            target_chain_id: int,
            token_address: ChecksumAddress = ETH_ADDRESS,
            **kwargs,
    ) -> HexStr:
        metadata = {
            "targetChain": target_chain_id,
            "targetAddress": wallet.address,
        }
        bridge_fn = self._bridge(
            value,
            token_address,
            self.DEFAULT_ADDRESS,
            bytes(f'data:,{json.dumps(metadata, separators=(',', ':'))}', "utf-8"),
        )
        # TODO why it doesn't work?
        return await self.chain.execute_fn(wallet, bridge_fn, value=value, **kwargs)
