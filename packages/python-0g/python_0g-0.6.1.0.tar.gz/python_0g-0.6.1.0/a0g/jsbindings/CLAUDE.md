# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **0G Compute Starter Kit** - a REST API starter kit for interacting with the 0G Compute Network. The project provides both TypeScript/JavaScript bindings and Python wrappers for blockchain-based AI service discovery and interaction.

### Key Components
- **JavaScript/TypeScript Core** (`src/index.ts`): Main API functions for service metadata and headers
- **Python Wrapper** (`../base.py`): High-level A0G class providing OpenAI-compatible clients
- **Smart Contract Integration** (`../contract/__init__.py`): Contract addresses and ABI management
- **Bundle Output** (`dist/bundle.js`): Compiled JavaScript bundle used by Python via PyExecJS

## Development Commands

### Setup
```bash
# Install dependencies
pnpm install
```

### Development
```bash
# Run in development mode with ts-node
pnpm dev

# Watch mode with automatic restart
pnpm watch

# Run a demo (if available)
pnpm demo
```

### Building
```bash
# Compile TypeScript to JavaScript
pnpm build

# Create bundled JavaScript file for Python consumption
pnpm build:bundle
```

### Starting
```bash
# Start the compiled application
pnpm start
```

## Architecture

### Multi-Language Interop
- **TypeScript Core**: Provides two main functions:
  - `getOpenAIHeadersDemo()`: Retrieves authentication headers and service metadata for AI providers
  - `getAllServices()`: Lists all available compute services on the 0G network
- **Python Bridge**: Uses PyExecJS (`require()`) to load and execute the JavaScript bundle
- **Smart Contracts**: Interacts with `inference` and `ledger` contracts on 0G blockchain

### Network Configuration
- **Mainnet**: Default production network (`https://evmrpc.0g.ai`)
- **Testnet**: Development network (`https://evmrpc-testnet.0g.ai`)
- **Hardhat**: Local development (contract addresses in `../contract/__init__.py:23-27`)

### Environment Variables
- `A0G_PRIVATE_KEY`: Wallet private key for blockchain transactions
- `A0G_RPC_URL`: Custom RPC endpoint (optional, defaults based on network)
- `A0G_INFERENCE_CA`: Override inference contract address
- `A0G_LEDGER_CA`: Override ledger contract address

## Key Files and Structure

### TypeScript Source (`src/`)
- `index.ts`: Main API functions - only source file in the project

### Python Integration (`../`)
- `base.py`: A0G class providing high-level Python interface
- `contract/__init__.py`: Contract addresses and ABI loading utilities
- `contract/*_abi.json`: Smart contract ABIs (not shown in exploration)

### Output (`dist/`)
- `bundle.js`: Bundled JavaScript consumed by Python wrapper

## API Usage Patterns

### From TypeScript
```typescript
import { getOpenAIHeadersDemo, getAllServices } from './index';

const headers = await getOpenAIHeadersDemo(privateKey, query, providerAddress, rpcUrl);
const services = await getAllServices(privateKey, rpcUrl);
```

### From Python
```python
from a0g import A0G

client = A0G(private_key="...", network="testnet")
openai_client = client.get_openai_client(provider_address)
all_services = client.get_all_services()
```

## Dependencies

### Core Dependencies
- `@0glabs/0g-serving-broker`: 0G network broker for service discovery
- `ethers`: Ethereum/blockchain interaction library
- `crypto-js`: Cryptographic functions

### Development Tools
- `typescript`: TypeScript compiler
- `ts-node`: Direct TypeScript execution
- `esbuild`: Fast JavaScript bundler

## Development Notes

- **No Testing Framework**: Project currently lacks automated tests
- **No TypeScript Config**: Uses default TypeScript settings
- **Bundle Required**: Python integration depends on the bundled JavaScript output
- **Blockchain Required**: All functionality requires valid wallet and RPC connection
- **Service Discovery**: Core functionality revolves around discovering and authenticating with AI compute providers on the 0G network

## Error Handling

- Functions return JSON-encoded responses with `success` boolean flag
- TypeScript functions catch errors and return `{success: false}` objects
- Python wrapper raises exceptions for failed operations
- Provider acknowledgment may show "already acknowledged" error (expected behavior)