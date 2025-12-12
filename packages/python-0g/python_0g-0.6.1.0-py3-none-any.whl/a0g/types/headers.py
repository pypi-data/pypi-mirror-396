from typing import Literal, TypedDict

ServingRequestHeaders = TypedDict(
    "ServingRequestHeaders",
    {
        "X-Phala-Signature-Type": Literal["StandaloneApi"],
        "Address": str,
        "Fee": str,
        "Input-Fee": str,
        "Request-Hash": str,
        "Nonce": str,
        "Signature": str,
        "VLLM-Proxy": str,
    },
)
