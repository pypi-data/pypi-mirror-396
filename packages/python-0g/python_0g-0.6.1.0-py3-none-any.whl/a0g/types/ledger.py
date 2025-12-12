from typing import List, Tuple

from pydantic import BaseModel


class LedgerStructOutput(BaseModel):
    user: str
    availableBalance: int  # bigint → Python int
    totalBalance: int  # bigint → Python int
    inferenceSigner: Tuple[int, int]
    additionalInfo: str
    inferenceProviders: List[str]
    fineTuningProviders: List[str]
