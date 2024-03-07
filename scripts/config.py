from better_web3.utils import load_toml
from better_web3.chain import load_chains
from pydantic import BaseModel

from common.config import LoggingConfig, TransactionConfig

from .paths import CONFIG_TOML, CHAINS_TOML


class Config(BaseModel):
    LOGGING: LoggingConfig
    TRANSACTION: TransactionConfig
    AUTO_OPEN: bool


CONFIG = Config(**load_toml(CONFIG_TOML))
CHAINS, MINIMAL_BALANCES = load_chains(load_toml(CHAINS_TOML))
