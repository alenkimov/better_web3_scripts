from web3 import Web3

from better_web3 import Chain, TxSpeed


def get_and_print_fees(chain: Chain, tx_speed: TxSpeed):
    max_fee_per_gas, max_priority_fee_per_gas = chain.estimate_eip1559_fees(tx_speed=tx_speed)
    max_fee_per_gas = Web3.from_wei(max_fee_per_gas, "gwei")
    max_priority_fee_per_gas = Web3.from_wei(max_priority_fee_per_gas, "gwei")
    print(f"{tx_speed.name} maxFeePerGas: {max_fee_per_gas} gwei")
    print(f"{tx_speed.name} MaxPriorityFeePerGas: {max_priority_fee_per_gas} gwei")


if __name__ == '__main__':
    goerli = Chain("https://eth-goerli.public.blastapi.io")

    get_and_print_fees(goerli, TxSpeed.SLOWEST)
    """output:
    SLOWEST maxFeePerGas: 0.003626646 gwei
    SLOWEST MaxPriorityFeePerGas: 0.003626613 gwei
    """

    get_and_print_fees(goerli, TxSpeed.NORMAL)
    """output:
    NORMAL maxFeePerGas: 1.000000033 gwei
    NORMAL MaxPriorityFeePerGas: 1 gwei
    """

    get_and_print_fees(goerli, TxSpeed.FASTEST)
    """output:
    FASTEST maxFeePerGas: 34.999999998 gwei
    FASTEST MaxPriorityFeePerGas: 34.999999965 gwei
    """
