# Quick reference

## Start services

```bash
# Terminal 1: Start Ganache Blockchain
ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545

# Terminal 2: Start Python Backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 3: Start React Frontend  
cd frontend && npm install && npm start

# Terminal 4: (Optional) Deploy Contract via Remix
# Go to: https://remix.ethereum.org
```

---

## Key components

### Blockchain (Ganache + smart contract)
- **Port**: 7545
- **Network ID**: 1337
- **Accounts**: 7 authorities with 100 ETH each
- **Contract**: KeyAuthority (4-of-7 approval)

### Backend (FastAPI)
- **Port**: 8000
- **Docs**: http://localhost:8000/docs
- **Main Features**:
  - ABE Key Management (4-of-7 split)
  - Blockchain Authentication
  - File Encryption/Decryption
  - Access Control API

### Frontend (React)
- **Port**: 3000
- **Pages**:
  - `/login` - authentication
  - `/upload` - upload with a policy
  - `/access` - approval + decrypt flow
  - `/download` - download/decrypt UI

Note: self-registration is disabled; accounts are created by an admin.

---

## Workflow summary

```
1. UPLOAD FILE
   └─→ Encrypt with ABE policy
   └─→ Split key into 4-of-7 shares
   └─→ Distribute to 7 authorities

2. REQUEST APPROVAL
   └─→ Create blockchain key ID
   └─→ Authorities receive approval request
   └─→ Monitor approval percentage

3. COLLECT APPROVALS (4 needed)
   └─→ Authority 1 approves ✅
   └─→ Authority 2 approves ✅
   └─→ Authority 3 approves ✅
   └─→ Authority 4 approves ✅ [THRESHOLD MET]

4. DECRYPT FILE
   └─→ Reconstruct key from 4 shares
   └─→ Decrypt file content
   └─→ Download plaintext
```

---

## API quick reference

### **Check Blockchain Connection**
```bash
curl -X POST http://localhost:8000/api/access/blockchain/status
```

### **Get All 7 Authorities**
```bash
curl http://localhost:8000/api/access/authorities
```

### **Request Key Approval**
```bash
curl -X POST http://localhost:8000/api/access/request-key-approval \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file123",
    "user_id": "alice",
    "user_attributes": {
      "role": "admin",
      "department": "IT",
      "clearance": "top-secret"
    }
  }'
```

### **Check Approval Status (4/7?)**
```bash
curl http://localhost:8000/api/access/approval-status/0x...keyid...
```

### **Decrypt File (Need 4 Approvals)**
```bash
curl -X POST http://localhost:8000/api/access/decrypt \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file123",
    "key_id": "0x...",
    "approving_authorities": [
      "0x8d4d6c34...",
      "0xfbe68438...",
      "0xd2a2e096...",
      "0x57d14ff7..."
    ]
  }'
```

---

## **7 Authorities on Ganache**

```
1. 0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48
2. 0xfbe684383F81045249eB1E5974415f484E6F9f21
3. 0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94
4. 0x57D14fF746d33127a90d4B888D378487e2C69f1f
5. 0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a
6. 0x211Db7b2b475E9282B31Bd0fF39220805505Ff71
7. 0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16

⚡ Need 4 out of these 7 to approve for decryption
```

---

## **File Locations**

```
📁 project/
├── 📄 COMPLETE_IMPLEMENTATION_GUIDE.md (Read this!)
├── 📄 VS_CODE_SETUP_GUIDE.md
├── 📄 REMIX_DEPLOYMENT_GUIDE.md
├── 📁 backend/
│   ├── 📄 requirements.txt (Install: pip install -r requirements.txt)
│   ├── 📄 main.py (FastAPI app)
│   ├── 📁 blockchain/
│   │   ├── 📄 blockchain_auth.py (NEW! Blockchain integration)
│   │   ├── 📄 DEPLOYMENT_INFO.json (Contract address)
│   ├── 📁 abe/
│   │   ├── 📄 abe_key_manager.py (NEW! 4-of-7 key splitting)
│   ├── 📁 api/
│   │   ├── 📄 access_routes.py (NEW! Decentralized access API)
├── 📁 frontend/
│   ├── 📄 package.json (npm install)
│   ├── 📁 src/
│   │   ├── 📄 App.js (Updated with /access route)
│   │   ├── 📁 pages/
│   │   │   ├── 📄 DecentralizedAccess.js (NEW! Main UI)
│   │   │   ├── 📄 DecentralizedAccess.css (NEW! Styling)
├── 📁 contracts/
│   ├── 📄 KeyAuthority.sol (Smart contract - 4-of-7)
│   ├── 📄 deploy.js (Hardhat deployment)
```

---

## **Troubleshooting Checklist**

- [ ] Ganache running on 127.0.0.1:7545
- [ ] Backend responding at http://localhost:8000
- [ ] Frontend loading at http://localhost:3000
- [ ] MetaMask connected to Ganache network
- [ ] Contract deployed and address saved
- [ ] DEPLOYMENT_INFO.json updated with contract address
- [ ] Backend requirements.txt installed
- [ ] Frontend node_modules installed
- [ ] Python virtual environment activated

---

## **Environment Variables** (Optional)

Create `.env` in backend folder:
```
GANACHE_RPC_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x... (your deployed address)
THRESHOLD=4
TOTAL_SHARES=7
DATABASE_URL=sqlite:///./test.db
```

---

## **Common Errors & Fixes**

| Error | Fix |
|-------|-----|
| `Port 7545 already in use` | `ganache-cli --port 7546` |
| `ModuleNotFoundError: charm` | `pip install charm-crypto` |
| `Cannot find module 'DecentralizedAccess'` | Check import path in App.js |
| `Contract not found` | Update DEPLOYMENT_INFO.json |
| `Insufficient gas` | Set GAS_LIMIT to 10000000 in Remix |
| `MetaMask not connected` | Add Ganache network: 127.0.0.1:7545 |

---

## **Test Data**

### **User Registration**
```
Username: alice
Password: test123
Role: admin
Department: IT
Clearance: top-secret
```

### **File Policy**
```
role:admin AND department:IT
```

---

## **System Statistics**

- **Total Authorities**: 7
- **Threshold Required**: 4 (57% majority)
- **Max Shares Lost**: 3 (without losing ability to decrypt)
- **Key Split Algorithm**: Shamir's Secret Sharing
- **Encryption**: AES-256 + ABE
- **Blockchain**: Ganache (local, instant mining)

---

**Last Updated**: December 24, 2025
**Status**: ✅ Complete and Tested
**Ready for**: Development, Testing, Demonstration
