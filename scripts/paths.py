from pathlib import Path

from better_web3.utils import copy_file

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent

# Log
LOG_DIR = BASE_DIR / "log"

# Config
CONFIG_DIR = BASE_DIR / "config"
DEFAULT_CONFIG_DIR = CONFIG_DIR / ".default"

# ABI
ABI_DIR = SCRIPT_DIR / "abi"

# Input
INPUT_DIR = BASE_DIR / "input"
PROXIES_TXT = INPUT_DIR / "proxies.txt"
ADDRESSES_TXT = INPUT_DIR / "addresses.txt"
PRIVATE_KEYS_TXT = INPUT_DIR / "private_keys.txt"
PRIVATE_KEY_TO_ADDRESS_TXT = INPUT_DIR / "private_key_to_address.txt"

# Output
OUTPUT_DIR = BASE_DIR / "output"

# Database
DATABASES_DIR = INPUT_DIR / ".db"
DATABASE_FILEPATH = DATABASES_DIR / "tabi.db"
ALEMBIC_INI = BASE_DIR / "alembic.ini"

# Creating dirs and files
_dirs = (LOG_DIR, INPUT_DIR, OUTPUT_DIR)

for dirpath in _dirs:
    dirpath.mkdir(exist_ok=True)

_txt_files = (PROXIES_TXT, ADDRESSES_TXT, PRIVATE_KEYS_TXT, PRIVATE_KEY_TO_ADDRESS_TXT)

for filepath in _txt_files:
    filepath.touch(exist_ok=True)

# Creating copies
DEFAULT_CONFIG_TOML = DEFAULT_CONFIG_DIR / "config.toml"
CONFIG_TOML = CONFIG_DIR / "config.toml"
copy_file(DEFAULT_CONFIG_TOML, CONFIG_TOML)

DEFAULT_CHAINS_TOML = DEFAULT_CONFIG_DIR / "chains.toml"
CHAINS_TOML = CONFIG_DIR / "chains.toml"
copy_file(DEFAULT_CHAINS_TOML, CHAINS_TOML)
