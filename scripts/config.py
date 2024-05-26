from common.utils import load_toml
from pydantic import BaseModel

from common.config import LoggingConfig, TransactionConfig

from .paths import CONFIG_TOML


class ChainsConfig(BaseModel):
    CHAIN_IDS: tuple[int]


class Config(BaseModel):
    LOGGING: LoggingConfig
    TRANSACTION: TransactionConfig
    AUTO_OPEN: bool
    CHAIN_IDS: list[int] = [1, 5, 56, 97, 137, 204]


CONFIG = Config(**load_toml(CONFIG_TOML))
