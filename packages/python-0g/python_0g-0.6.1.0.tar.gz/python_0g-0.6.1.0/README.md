# python-0g

A Python client for the 0G.ai on-chain inference network. It lets you obtain an OpenAI-compatible client for any 0G provider (by ENS), sign requests locally with your wallet key, and query network/service metadata over the 0G smart contracts.

Highlights:
- OpenAI-compatible sync and async clients (drop-in for openai SDK)
- Provider discovery via on-chain contracts
- Local signing using your EVM private key
- Utility helpers for balance/ledger and quoting costs


## Requirements
- Python >= 3.10, < 4.0
- Node.js (required by the embedded JS bindings via the `javascript` package)
- An EVM private key funded on the 0G network
- RPC endpoint for the 0G testnet or mainnet (HTTP)


## Installation
Install from PyPI:

```bash
pip install python-0g
```


## Quick start
Set your credentials using environment variables:

- A0G_PRIVATE_KEY — your EVM private key (hex string without leading 0x)
- A0G_RPC_URL — RPC endpoint URL for the 0G network (optional; defaults to https://evmrpc-testnet.0g.ai)

Example (macOS/Linux):
```bash
export A0G_PRIVATE_KEY=YOUR_HEX_PRIVATE_KEY
export A0G_RPC_URL=https://evmrpc-testnet.0g.ai
```

Then use the SDK to get an OpenAI-compatible client for a provider and make a chat completion:

```python
from a0g.base import A0G

# Replace with a valid provider ENS name registered on 0G (example placeholder)

a0g_client = A0G()
service = a0g_client.get_all_services()[1]
client = a0g_client.get_openai_client(service.provider)

resp = client.chat.completions.create(
    model=service.model,  # model used by the provider
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello from 0G!"},
    ],
)

print(resp.choices[0].message.content)
```


## Async usage
```python
import asyncio
from a0g.base import A0G

PROVIDER = "vllm-testnet.0gai.eth"  # replace with a valid provider

async def main():
    a0g_client = A0G()
    service = a0g_client.get_all_services()[1]
    
    aclient = a0g_client.get_openai_async_client(service.provider)
    resp = await aclient.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Ping?"},
        ],
    )
    print(resp.choices[0].message.content)

asyncio.run(main())
```

Working directly with the model type:

```python
from a0g.base import A0G
from a0g.types.model import ServiceStructOutput

a0g_client = A0G()
svc = a0g_client.get_all_services()[1]
# If you already have a ServiceStructOutput instance `svc` from on-chain calls
print(svc.get_service_metadata())  # { 'endpoint': '.../v1/proxy', 'model': '...' }
quote = svc.get_quote()            # GET {url}/v1/quote, bigint-safe JSON
print(quote)

# Helpers to approximate byte-based accounting used by some providers:
inputs = ServiceStructOutput.get_input_count("Hello")
outputs = ServiceStructOutput.get_output_count("World")
print(inputs, outputs)
```


## On-chain helpers
A0G exposes basic helpers around the 0G contracts using web3.py:

```python
from a0g.base import A0G
from web3.types import ENS

PROVIDER = "0x...."
sdk = A0G()
print("Balance (ETH):", sdk.get_balance())
print("Ledger inference address:", sdk.get_ledger_inference_address())
print("Ledger owner address:", sdk.get_ledger_owner_address())

acct = sdk.get_account(PROVIDER)
print("Provider account struct:", acct)

svc = sdk.get_service(PROVIDER)
print("Service struct:", svc)
```


## Configuration
- A0G_PRIVATE_KEY: hex-encoded EVM private key used to sign provider requests.
- A0G_RPC_URL: 0G RPC URL. Defaults to https://evmrpc-testnet.0g.ai if not provided.

The constructor also accepts `private_key` and `rpc_url` keyword arguments to override env vars:

```python
from a0g.base import A0G
sdk = A0G(private_key="...", rpc_url="https://evmrpc-testnet.0g.ai")
```


## Development
- Formatting/linting: ruff, isort, mypy are configured in pyproject for dev use.
- JS bindings: bundled under `a0g/jsbindings` and loaded via the `javascript` package; ensure Node.js is installed and accessible.

Run tests:
```bash
pytest -q
```


## Troubleshooting
- Module "javascript" or Node.js errors: Ensure Node.js is installed and available on PATH.
- RPC connection error: Verify `A0G_RPC_URL` is reachable; the SDK checks connectivity on init.
- Provider unavailable: `get_openai_client` raises if `get_service_metadata` returns unsuccessful; try another provider or network.
- HTTP 4xx/5xx: Check your wallet funding and provider’s whitelist or availability windows.


## License
This project is licensed under the terms of the LICENSE file included in the repository.
