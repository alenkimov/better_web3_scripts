from pathlib import Path

from better_web3.utils import copy_file

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent

CONFIG_DIR = BASE_DIR / "config"
DEFAULT_CONFIG_DIR = CONFIG_DIR / "default"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR = BASE_DIR / "input"
LOG_DIR = BASE_DIR / "log"

DIRS = [OUTPUT_DIR, INPUT_DIR, LOG_DIR]

for dirpath in DIRS:
    dirpath.mkdir(exist_ok=True)

DEFAULT_CONFIG_TOML = DEFAULT_CONFIG_DIR / "config.toml"
CONFIG_TOML = CONFIG_DIR / "config.toml"
copy_file(DEFAULT_CONFIG_TOML, CONFIG_TOML)

DEFAULT_CHAINS_TOML = DEFAULT_CONFIG_DIR / "chains.toml"
CHAINS_TOML = CONFIG_DIR / "chains.toml"
copy_file(DEFAULT_CHAINS_TOML, CHAINS_TOML)
