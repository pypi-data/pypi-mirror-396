from decimal import Decimal
from typing import Any, TypedDict, Union

import httpx
from pydantic import BaseModel

from a0g.types.headers import ServingRequestHeaders


class ServiceStructOutput(BaseModel):
    provider: str
    serviceType: str
    url: str
    inputPrice: Union[int, Decimal]  # bigint -> int (or Decimal if needed)
    outputPrice: Union[int, Decimal]
    updatedAt: int
    model: str
    verifiability: str
    additionalInfo: str

    def get_request_headers(self, content: str, vllm_proxy: bool = True):
        pass

    def get_service_metadata(self):
        return {
            "endpoint": f"{self.url}/v1/proxy",
            "model": self.model,
        }

    def get_quote(self) -> dict[str, Any]:
        try:
            endpoint = f"{self.url}/v1/quote"
            resp = httpx.get(endpoint)
            resp.raise_for_status()

            def bigint_hook(obj):
                for k, v in obj.items():
                    if isinstance(v, str) and v.isdigit():
                        try:
                            obj[k] = int(v)
                        except ValueError:
                            obj[k] = v
                return obj

            ret = resp.json(object_hook=bigint_hook)
            return ret
        except Exception as e:
            raise RuntimeError(f"Failed to get quote: {e}") from e

    @classmethod
    def get_input_count(cls, content: str) -> int:
        if not content:
            return 0
        encoded = content.encode("utf-8")
        return len(encoded)

    @classmethod
    def get_output_count(cls, content: str) -> int:
        if not content:
            return 0
        encoded = content.encode("utf-8")
        return len(encoded)


class ServiceMetadata(TypedDict, total=False):
    endpoint: str
    model: str
    headers: ServingRequestHeaders
    success: bool
