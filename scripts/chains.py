from typing import Iterable

from better_web3 import Chain
from better_web3 import get_chain

from common.utils import load_toml

from .paths import CHAINS_TOML
from .config import CONFIG

LOCAL_CHAINS_CONFIG = load_toml(CHAINS_TOML)


def get_chains(chain_ids: Iterable[int]) -> list[Chain]:
    chains = []
    for chain_id in chain_ids:
        chain_config = LOCAL_CHAINS_CONFIG.get(str(chain_id), {})
        chains.append(get_chain(chain_id, **chain_config))
    return chains


CHAINS = get_chains(CONFIG.CHAIN_IDS)
