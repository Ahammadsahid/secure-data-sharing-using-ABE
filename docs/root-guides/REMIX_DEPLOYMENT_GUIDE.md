# KeyAuthority contract deployment (Remix + Ganache)

This project expects a KeyAuthority contract deployed on a local Ganache chain.
The backend reads the contract address (and authority list) from `backend/blockchain/DEPLOYMENT_INFO.json`.

## Prerequisites

1. Start Ganache:

```bash
ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545
```

2. Ensure MetaMask is connected to the Ganache network (RPC `http://127.0.0.1:7545`, chain id `1337`).

## Deploy via Remix

1. Open https://remix.ethereum.org
2. Open `contracts/KeyAuthority.sol` (copy/paste into Remix if needed)
3. Compile with Solidity 0.8.x
4. Deploy & Run Transactions:
	 - Environment: Injected Provider (MetaMask)
	 - Gas limit: increase if deployment fails (e.g. 8,000,000)
	 - Constructor args:
		 - `authorities`: use the `authorities` array from `backend/blockchain/DEPLOYMENT_INFO.json`
		 - `threshold`: `4`
5. Deploy, then copy the deployed contract address.

## Update the backend config

Edit `backend/blockchain/DEPLOYMENT_INFO.json` and set:
- `contractAddress` to the address you deployed

Restart the backend after updating the address.

## Common issues

- Not enough gas: increase Remix gas limit.
- Wrong chain: verify MetaMask is pointed at Ganache.
- Backend says `contract_misconfigured`: contract address/ABI mismatch; redeploy and update `DEPLOYMENT_INFO.json`.

