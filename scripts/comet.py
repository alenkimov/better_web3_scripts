import json

from better_web3 import Chain
from web3.types import Wei
from eth_utils import to_checksum_address, to_hex
from eth_account.account import LocalAccount


class CometBridge:
    ADDRESS = to_checksum_address("0xB50Ac92D6d8748AC42721c25A3e2C84637385A6b")

    def __init__(self, chain: Chain):
        self.chain = chain

    async def bridge_eth(
            self,
            wallet: LocalAccount,
            value: Wei | int,
            target_chain_id: int,
    ):
        metadata = {
            "targetChain": str(target_chain_id),
            "targetAddress": wallet.address,
        }
        metadata = f'data:,{json.dumps(metadata, separators=(',', ':'))}'
        tx_params = await self.chain._build_tx_base_params(
            gas=self.chain.default_gas_price,
            value=value,
            address_to=self.ADDRESS,
            address_from=wallet.address,
        )
        tx_params["data"] = to_hex(text=metadata)
        gas = await self.chain.eth.estimate_gas(tx_params)
        tx_params = await self.chain._build_tx_base_params(gas, tx_params=tx_params)
        tx_params = await self.chain._build_tx_fee_params(tx_params=tx_params)
        return await self.chain.sign_and_send_tx(wallet, tx_params)
