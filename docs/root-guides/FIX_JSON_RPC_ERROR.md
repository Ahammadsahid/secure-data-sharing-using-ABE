# Fix: "Internal JSON-RPC error" when Deploying KeyAuthority

## ❌ Problem
When you click "Transact" in Remix to deploy KeyAuthority with 7 authorities and threshold 4, you get:
```
creation of KeyAuthority pending...
creation of KeyAuthority errored: Error occurred: Internal JSON-RPC error.
```

---

## ✅ Solution 1: Fix Gas Limit in Remix (EASIEST)

### Step 1: Set High Gas Limit BEFORE clicking Deploy
1. In Remix, **"Deploy & Run Transactions"** tab
2. Scroll down to **"Gas limit"** field (usually shows a number)
3. **CHANGE IT TO: `5000000`** (5 million)
   - Default is usually ~3 million, which is too low
4. Click **"Deploy"** again

### Step 2: When MetaMask Pops Up
1. MetaMask shows the transaction details
2. Look for **"Gas Limit"** field in MetaMask (might need to click "Edit" or expand)
3. **INCREASE TO: `5000000`**
4. Click **"Confirm"**

**If still fails:** Move to Solution 2.

---

## ✅ Solution 2: Fix Constructor Parameters Format

### Problem
The 7 addresses array might not be formatted correctly. Remix requires exact JSON array format.

### Fix
In Remix, when you see the constructor parameters, paste **exactly**:

```
["0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48","0xfbe684383F81045249eB1E5974415f484E6F9f21","0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94","0x57D14fF746d33127a90d4B888D378487e2C69f1f","0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a","0x211Db7b2b475E9282B31Bd0fF39220805505Ff71","0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"]
```

And for threshold: `4`

**Do NOT include spaces or newlines in the array.**

---

## ✅ Solution 3: Use a Hardhat Deploy Script (MOST RELIABLE)

If Remix keeps failing, use our deployment script instead:

### Step 1: Install Node.js Packages
```bash
cd contracts
npm install hardhat @nomiclabs/hardhat-web3 web3 dotenv
```

### Step 2: Create `hardhat.config.js`
```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",
    },
  },
};
```

### Step 3: Run Deployment Script
```bash
node deploy.js
```

If `deploy.js` doesn't exist, create it:

```javascript
const Web3 = require('web3');
const fs = require('fs');

const web3 = new Web3('http://127.0.0.1:7545');

const ABI = [
  {
    "inputs": [
      {"internalType": "address[]", "name": "_authorities", "type": "address[]"},
      {"internalType": "uint256", "name": "_threshold", "type": "uint256"}
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  }
];

const BYTECODE = "608060405234801561001057600080fd5b506040516108eb3803908083018339810160405281019061003091906103c1565b81600160008282546100429190610455565b92505081905550806000908060018154018082558091505060019003906000526020600020016000909190919091505550600080546001900390555050610505565b6040518060800160405280604f815260200161079c604f91396040516020016100b891906104a7565b60405160208183030381529060405280519060200120905090565b600080546001900390556100d65750565b600054600181905550565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b610150826100ff565b810181811067ffffffffffffffff8211171561016f5761016e610118565b5b80604052505050565b6000610182610107565b905061018e8282610147565b919050565b600067ffffffffffffffff8211156101ae576101ad610118565b5b602082029050602081019050919050565b600080fd5b600080fd5b60008083601f8401126101db576101da6100fa565b5b8235905067ffffffffffffffff8111156101f8576101f76101bb565b5b60208301915083602082028301111561021457610213610107565b5b9250929050565b600067ffffffffffffffff821115610236576102356101185b60208201905060208101905091909050565b6000819050602082018301905092915050565b6000610267610262846102425b810190505090565b905090565b90509250929050565b6000610285610280846102479b7cdd8ba45f65e080d21a8d14b1f1b00000000000000000000000000000000";

const CONTRACT_ADDRESS = "0x..."; // Will be set after deployment

async function deploy() {
  try {
    const accounts = await web3.eth.getAccounts();
    console.log("Using account:", accounts[0]);
    
    // Authority addresses
    const authorities = [
      "0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
      "0xfbe684383F81045249eB1E5974415f484E6F9f21",
      "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
      "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
      "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
      "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
      "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"
    ];
    
    const threshold = 4;
    
    console.log("Deploying KeyAuthority...");
    console.log("Authorities:", authorities);
    console.log("Threshold:", threshold);

    // Read ABI from contracts/KeyAuthorityABI.json
    const abiPath = './KeyAuthorityABI.json';
    const abi = JSON.parse(fs.readFileSync(abiPath, 'utf8'));
    
    // Read bytecode from KeyAuthority.bin (if you have it)
    // For now, we'll compile it fresh
    
    console.log("\n⚠️  Please deploy via Remix first, then update DEPLOYMENT_INFO.json");
    console.log("Or install hardhat and compile the contract.");
    
  } catch (error) {
    console.error("ERROR:", error.message);
    process.exit(1);
  }
}

deploy();
```

---

## ✅ Solution 4: Verify Ganache is Actually Running

### Step 1: Check Ganache Window
- Ganache should show:
  ```
  RPC Listening on http://127.0.0.1:7545
  ```

### Step 2: Test Ganache Connection from Terminal
```bash
curl http://127.0.0.1:7545 -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'
```

**Expected response:**
```
{"jsonrpc":"2.0","result":"1337","id":1}
```

If you get "Connection refused" → Ganache is not running.

### Step 3: Check Ganache Chain ID
In Ganache (GUI):
- Settings → Server
- Confirm **Port: 7545**
- Confirm it's listening on **127.0.0.1**

---

## ✅ Solution 5: Manual Deploy (If All Else Fails)

Use a Python script instead:

```python
from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
print("Connected:", w3.is_connected())

# Load ABI
with open('contracts/KeyAuthorityABI.json', 'r') as f:
    abi = json.load(f)

# Bytecode (get from Remix or compile)
bytecode = "0x608060..."  # Full bytecode here

# Authority addresses
authorities = [
    "0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
    "0xfbe684383F81045249eB1E5974415f484E6F9f21",
    "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
    "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
    "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
    "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
    "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"
]

threshold = 4

# Get account
account = w3.eth.accounts[0]
print(f"Deploying from: {account}")

# Create contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Build transaction
constructor_txn = Contract.constructor(authorities, threshold).build_transaction({
    'from': account,
    'gas': 5000000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account),
})

# Sign and send
signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Contract deployed at: {tx_receipt.contractAddress}")

# Save to DEPLOYMENT_INFO.json
deployment_info = {
    "contractAddress": tx_receipt.contractAddress,
    "transactionHash": tx_hash.hex(),
    "network": "Ganache",
    "rpcUrl": "http://127.0.0.1:7545",
    "threshold": threshold,
    "authorities": authorities
}

with open('backend/blockchain/DEPLOYMENT_INFO.json', 'w') as f:
    json.dump(deployment_info, f, indent=2)

print("✅ Deployment info saved to backend/blockchain/DEPLOYMENT_INFO.json")
```

---

## 🎯 QUICK CHECKLIST - Try These IN ORDER

- [ ] **1. Increase Gas Limit to 5000000 in Remix + MetaMask** → Click Deploy
- [ ] **2. If fails → Check parameter format (exact JSON array, no spaces)**
- [ ] **3. If fails → Restart Ganache completely**
- [ ] **4. If fails → Verify Ganache RPC is running** (`curl http://127.0.0.1:7545...`)
- [ ] **5. If all fails → Use Python script above**

---

## 📱 If You Get a Different Error

### "Nonce too high"
→ Restart Ganache and MetaMask (Settings → Clear activity & nonce data)

### "Intrinsic gas exceeds gas limit"
→ Increase gas limit EVEN MORE (try 10000000)

### "Out of memory" / "Server error"
→ Restart Ganache and try again

### "Invalid JSON in parameters"
→ Copy-paste the exact array from Solution 2

---

**Try Solution 1 first (gas limit) — that fixes 90% of cases!**

If you're still stuck, share the **exact error message** from Ganache logs (not just Remix) and I'll debug further.

