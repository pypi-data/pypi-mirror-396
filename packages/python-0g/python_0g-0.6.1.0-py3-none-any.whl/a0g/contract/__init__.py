import os
from typing import Literal


TESTNET_CHAIN_ID = 16602
MAINNET_CHAIN_ID = 16661
HARDHAT_CHAIN_ID = 31337


CONTRACT_ADDRESSES = {
    "testnet": {
        "ledger": "0xE70830508dAc0A97e6c087c75f402f9Be669E406",
        "inference": "0xa79F4c8311FF93C06b8CfB403690cc987c93F91E",
        "fineTuning": "0xaC66eBd174435c04F1449BBa08157a707B6fa7b1",
    },
    "mainnet": {
        "ledger": "0x2dE54c845Cd948B72D2e32e39586fe89607074E3",
        "inference": "0x47340d900bdFec2BD393c626E12ea0656F938d84",
        "fineTuning": "0x0000000000000000000000000000000000000000",
    },
    "hardhat": {
        "ledger": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
        "inference": "0x0165878A594ca255338adfa4d48449f69242Eb8F",
        "fineTuning": "0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0",
    }
}


def get_ca(
    name: Literal["inference", "ledger"],
    network: Literal["testnet", "mainnet", "hardhat"] = "mainnet"
):
    if name not in ["inference", "ledger"]:
        raise RuntimeError(f"No contract address found with name: {name}")

    if network not in CONTRACT_ADDRESSES:
        raise RuntimeError(f"No contract address found for network: {network}")

    env_key = f"A0G_{name.upper()}_CA"
    return os.environ.get(env_key, CONTRACT_ADDRESSES[network][name])
