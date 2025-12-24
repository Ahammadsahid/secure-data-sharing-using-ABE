# Secure Data Sharing - Complete Setup Guide
# Remix + Ganache + MetaMask Integration in VS Code

## **Step 1: Install VS Code Extensions**

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Install these extensions:
   - **Hardhat for Solidity** (Buidler Labs)
   - **Solidity** (Juan Blanco)
   - **REST Client** (Huachao Mao)

## **Step 2: Start Services in VS Code Terminal**

### **Terminal 1 - Ganache**
```bash
ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545
```

### **Terminal 2 - Backend (Python)**
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### **Terminal 3 - Frontend (React)**
```bash
cd frontend
npm install
npm start
```

### **Terminal 4 - Remix Server (Optional)**
```bash
# If you want local Remix
npm install -g @remix-project/remixd
remixd -s . --port 65521
```

## **Step 3: Access Remix in Browser**

1. Go to https://remix.ethereum.org
2. Click "Connect to localhost" (bottom left)
3. Select the `contracts` folder
4. Open `KeyAuthority.sol`

## **Step 4: Deploy Contract in Remix**

1. Compile the contract (Ctrl+S)
2. Go to "Deploy & Run Transactions"
3. Set GAS LIMIT: `10000000`
4. Enter constructor parameters:
   - Authorities: `["0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48","0xfbe684383F81045249eB1E5974415f484E6F9f21","0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94","0x57D14fF746d33127a90d4B888D378487e2C69f1f","0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a","0x211Db7b2b475E9282B31Bd0fF39220805505Ff71","0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"]`
   - Threshold: `4`
5. Click "Deploy"
6. Copy the contract address and update `DEPLOYMENT_INFO.json`

## **Step 5: MetaMask Setup**

1. Install MetaMask browser extension
2. Add Ganache network:
   - Network Name: Ganache
   - RPC URL: http://127.0.0.1:7545
   - Chain ID: 1337
   - Currency: ETH
3. Import first account:
   - Private Key: (from Ganache terminal)

## **Step 6: Test End-to-End**

1. Open http://localhost:3000 (Frontend)
2. Register with attributes: `role:admin,department:IT,clearance:top-secret`
3. Upload a file with ABE policy
4. Get key approvals from 4 authorities
5. Download and decrypt file

## **Troubleshooting**

| Issue | Solution |
|-------|----------|
| Gas error in Remix | Increase GAS LIMIT to 10000000 |
| MetaMask not connecting | Check Ganache RPC in settings |
| Backend can't connect to blockchain | Update contract address in code |
| Port already in use | Kill process or use different port |
