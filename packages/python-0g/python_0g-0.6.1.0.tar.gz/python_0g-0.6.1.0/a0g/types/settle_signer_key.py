from typing import Tuple, TypedDict


class SettleSignerKey(TypedDict):
    settleSignerPublicKey: Tuple[int, int]
    settleSignerEncryptedPrivateKey: str
