from typing import List, Tuple

from pydantic import BaseModel


class RefundStructOutput(BaseModel):
    txHash: str
    amount: int


class AccountStructOutput(BaseModel):
    user: str
    provider: str
    nonce: int  # bigint → Python int
    balance: int  # bigint → Python int
    pendingRefund: int  # bigint → Python int
    signer: Tuple[int, int]  # [bigint, bigint]
    refunds: List[RefundStructOutput]
    additionalInfo: str
    providerPubKey: Tuple[int, int]  # [bigint, bigint]
    teeSignerAddress: str
    validRefundsLength: int
