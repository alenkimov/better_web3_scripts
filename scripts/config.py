from better_web3.utils import load_toml
from pydantic import BaseModel

from ._logger import LoggingLevel
from .paths import CONFIG_TOML


class Config(BaseModel):
    LOGGING_LEVEL: LoggingLevel
    WAIT_FOR_TX_RECEIPT: bool
    REQUEST_BALANCES: bool
    HIDE_SECRETS: bool
    AUTO_OPEN: bool


CONFIG = Config(**load_toml(CONFIG_TOML))
