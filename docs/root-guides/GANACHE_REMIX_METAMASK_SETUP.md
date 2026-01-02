# Complete Setup Guide: Ganache + MetaMask + Remix

## 📋 Prerequisites
- **Ganache** installed (download from https://www.trufflesuite.com/ganache)
- **MetaMask** browser extension installed (Chrome/Firefox)
- **Remix IDE** (https://remix.ethereum.org)

---

## 🔧 Step 1: Start Ganache

### Option A: Ganache GUI (Easiest)
1. Open the Ganache application (desktop app)
2. Click **"New Workspace"** → **"Create Workspace"**
3. Note the **RPC Server** URL (default: `http://127.0.0.1:7545`)
4. Keep Ganache running in the background

### Option B: Ganache CLI (If you prefer command line)
```bash
npm install -g ganache-cli
ganache-cli --host 127.0.0.1 --port 7545
```

**Expected output:**
```
Ganache CLI started at http://127.0.0.1:7545
Available Accounts (first one is funded):
(0) 0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48
(1) 0xfbe684383F81045249eB1E5974415f484E6F9f21
...
```

✅ **Ganache is now running!**

---

## 🦊 Step 2: Connect MetaMask to Ganache

### Step 2.1: Open MetaMask
- Click the MetaMask extension icon in your browser toolbar
- If not installed: install from Chrome Web Store or Firefox Add-ons

### Step 2.2: Add Ganache Network to MetaMask
1. Click the **Network dropdown** (top-left, shows "Ethereum Mainnet" or similar)
2. Scroll to the bottom → Click **"Add network"** or **"Add a new network"**
3. Fill in the form:
   ```
   Network name:        Ganache
   New RPC URL:         http://127.0.0.1:7545
   Chain ID:            1337
   Currency symbol:     ETH
   Block explorer URL:  (leave empty)
   ```
4. Click **"Save"**

### Step 2.3: Verify Connection
- MetaMask should now show "Ganache" in the network dropdown
- Click it to switch to the Ganache network
- You should see **"0 ETH"** balance (no accounts imported yet)

### Step 2.4: Import Ganache Accounts to MetaMask
1. From Ganache, copy the **private key** of the first account (Account 0)
   - Click the key icon next to the account in Ganache
2. In MetaMask, click the **account icon** (top-right) → **"Import Account"**
3. Select **"Private Key"** as import method
4. Paste the private key
5. Click **"Import"**
6. Repeat for accounts 1-6 (7 accounts total for the 7 authorities)

**Expected result in MetaMask:**
- You'll see imported accounts like "Account 1", "Account 2", etc.
- Each account shows ~100 ETH (from Ganache)

✅ **MetaMask is now connected to Ganache!**

---

## 🔗 Step 3: Connect Remix to MetaMask

### Step 3.1: Open Remix IDE
- Visit https://remix.ethereum.org in your browser

### Step 3.2: Deploy Smart Contract via Remix
1. In Remix, on the left sidebar, click the **"File Explorer"** icon
2. Click **"Create new file"** → name it `KeyAuthority.sol`
3. Copy the entire code from `contracts/KeyAuthority.sol` (from your project)
4. Paste it into Remix

### Step 3.3: Set Up Compiler
1. Click the **"Solidity Compiler"** icon (left sidebar, looks like a scroll)
2. Ensure the compiler version matches your contract: **0.8.20** or compatible
3. Click **"Compile KeyAuthority.sol"**
4. ✅ If no red errors, compilation successful

### Step 3.4: Deploy to Ganache via MetaMask
1. Click the **"Deploy & Run Transactions"** icon (left sidebar, looks like a play button)
2. In the **"Environment"** dropdown, select **"Injected Provider - MetaMask"**
   - MetaMask will pop up asking for permission
   - Click **"Connect"** to allow Remix to access your wallet
3. Verify the environment now shows:
   ```
   Environment: Injected Provider - MetaMask
   Account:     0x8d4d6c34... (your first Ganache account)
   Balance:     100 ETH
   ```
4. In the **"Contract"** dropdown, select **"KeyAuthority"**
5. For the constructor parameters:
   - **_authorities** (address[]): paste the 7 Ganache account addresses
     ```
     ["0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
      "0xfbe684383F81045249eB1E5974415f484E6F9f21",
      "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
      "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
      "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
      "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
      "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"]
     ```
   - **_threshold** (uint): `4`
6. Click the **"Deploy"** button
7. MetaMask will pop up asking to confirm the transaction
   - Increase Gas Limit to **500000** if needed
   - Click **"Confirm"**

### Step 3.5: Verify Deployment
- After ~2 seconds, you should see the contract deployed in Remix's console
- Copy the **contract address** (shown in the "Deployed Contracts" section)
- Save it to `backend/blockchain/DEPLOYMENT_INFO.json`:
  ```json
  {
    "contractAddress": "0x..."
  }
  ```

✅ **Contract deployed to Ganache via Remix + MetaMask!**

---

## ✅ Verify Everything Works

### Checklist:
- [ ] Ganache is running at `http://127.0.0.1:7545`
- [ ] MetaMask is connected to Ganache network
- [ ] MetaMask has 7 imported accounts with 100 ETH each
- [ ] Remix shows "Injected Provider - MetaMask" in Environment
- [ ] KeyAuthority contract deployed and address saved to `DEPLOYMENT_INFO.json`

### Test the Smart Contract
1. In Remix, under **"Deployed Contracts"**, expand the KeyAuthority contract
2. Call `approveKey()` with any test key ID
3. MetaMask will ask to confirm → Click **"Confirm"**
4. Transaction should succeed (shown in Ganache)

---

## 🎯 Next Steps: Test the Full Backend Flow

Once everything is connected:

```bash
# 1. Start backend
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# 2. Start frontend
cd frontend
npm start

# 3. In the Download page:
#    - Request Approval (generates key_id)
#    - Simulate Approvals (sends approval transactions via backend)
#    - Download Decrypted File
```

---

## ❌ Troubleshooting

### Problem: "The chainId provided does not match the chainId of the network"
**Solution:** In MetaMask network settings, ensure Chain ID is set to `1337`

### Problem: MetaMask doesn't show Ganache network option
**Solution:** 
- Click "Add a network" manually (not "Add a popular network")
- Ensure RPC URL is exactly `http://127.0.0.1:7545`

### Problem: Remix says "No accounts available"
**Solution:** 
1. Check MetaMask is on "Ganache" network
2. Ensure at least one account is imported and has ETH balance
3. In Remix, click "Connect to MetaMask" button again

### Problem: Contract deployment fails with "gas limit exceeded"
**Solution:** Increase gas limit in MetaMask to `500000` before confirming transaction

### Problem: Can't import Ganache accounts to MetaMask
**Solution:** 
1. In Ganache, click the account row to reveal the private key
2. Look for the "Show private key" button
3. Copy the full private key (64 hex characters)
4. In MetaMask, paste it exactly as shown

---

## 📝 Summary

| Component | Status | URL/Details |
|-----------|--------|------------|
| Ganache | Running | http://127.0.0.1:7545 |
| MetaMask | Connected | Network: Ganache (Chain ID 1337) |
| Remix | Connected | Injected Provider - MetaMask |
| KeyAuthority Contract | Deployed | Address saved in DEPLOYMENT_INFO.json |

You're now ready to test the full end-to-end secure data sharing flow! 🚀

