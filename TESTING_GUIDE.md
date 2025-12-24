# 🚀 Complete End-to-End Testing Guide

## ✅ System Status
- **Backend**: Running on `http://127.0.0.1:8000`
- **Contract Address**: `0x126d0D3B866D7ebb5856722B722Bc795a17AD1Ce`
- **Ganache RPC**: `http://127.0.0.1:7545`
- **Database**: SQLite (initialized with test users)

---

## 👤 Test Users (Ready to Use)

| Username | Password | Role | Department | Clearance |
|----------|----------|------|------------|-----------|
| **admin** | admin123 | Admin | IT | High |
| **alice** | alice123 | User | IT | High |
| **bob** | bob123 | User | Finance | Medium |
| **charlie** | charlie123 | User | HR | Low |

---

## 🏃 Quick Start (3 Steps)

### Step 1: Start Backend (if not already running)
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 2: Start Frontend
```bash
cd frontend
npm install
npm start
```

### Step 3: Open Browser
- Frontend: `http://localhost:3000`
- Backend Docs: `http://127.0.0.1:8000/docs`

---

## 📋 Full Testing Flow

### 🔐 Step 1: Register (Optional - Users Already Created)
- Go to **Register** page
- Use any username/password (already have test users)

### 🔑 Step 2: Login
1. Click **Login**
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click **Login** → Redirects to Dashboard

### 📤 Step 3: Upload File (Admin Only)
1. Click **Upload** tab
2. Select a test file (any .txt, .pdf, .jpg)
3. Policy: `role:admin AND department:IT` (matches admin's attributes)
4. Click **Upload**
5. **Save the File ID** (e.g., `1`, `2`, `3`)

### 📥 Step 4: Download & Decrypt (Full Flow)

#### A. Request Approval
1. Click **Download** tab
2. Enter:
   - **File ID**: (from step 3, e.g., `1`)
   - **Username**: `admin`
3. Click **"Request Approval"**
4. ✅ Should show:
   - Key ID (hex string)
   - 7 Authorities listed

#### B. Simulate Approvals (Local Testing)
1. Click **"Simulate Approvals (local)"**
2. Will send approval transactions from 4 authorities
3. ✅ Should show success message

#### C. Download Decrypted File
1. Click **"Download Decrypted File"**
2. ✅ Browser downloads the decrypted file!
3. File will be named: `secure_file_<fileId>`

---

## 🧪 Test Scenarios

### Scenario 1: Successful Decryption (Happy Path)
**Step-by-step:**
1. Login as `admin` (high clearance)
2. Upload file with policy: `role:admin AND department:IT`
3. Go to Download page
4. Request Approval
5. Simulate Approvals
6. Download file
7. **Result**: ✅ File downloads successfully

---

### Scenario 2: Access Denied (Failed Policy Check)
**Step-by-step:**
1. Login as `bob` (Finance dept, medium clearance)
2. Upload file with policy: `role:admin AND department:IT`
3. Go to Download page with File ID from step 2
4. Request Approval
5. Simulate Approvals
6. Try Download
7. **Result**: ❌ "Access denied by policy"

---

### Scenario 3: Insufficient Approvals
**Step-by-step:**
1. Request Approval
2. **Don't** click Simulate Approvals
3. Click Download
4. **Result**: ❌ "Insufficient approvals" error

---

## 🔧 API Testing (Direct Endpoints)

### Test Backend APIs with cURL or Postman

#### 1. Check Blockchain Status
```bash
curl -X POST http://127.0.0.1:8000/api/access/blockchain/status
```

**Expected Response:**
```json
{
  "status": "connected",
  "network": "Ganache",
  "contract_address": "0x126d0D3B...",
  "rpc_url": "http://127.0.0.1:7545"
}
```

#### 2. Request Key Approval
```bash
curl -X POST http://127.0.0.1:8000/api/access/request-key-approval \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "1",
    "user_id": "admin",
    "user_attributes": {
      "role": "admin",
      "department": "IT",
      "clearance": "high"
    }
  }'
```

**Expected Response:**
```json
{
  "key_id": "0x...",
  "file_id": "1",
  "authorities": ["0x266E...", ...],
  "threshold": 4,
  "required_approvals": 4,
  "status": "pending"
}
```

#### 3. Simulate Approvals
```bash
curl -X POST http://127.0.0.1:8000/api/access/simulate-approvals \
  -H "Content-Type: application/json" \
  -d '{
    "key_id": "0x...",
    "authority_addresses": [
      "0x266E6E85ae9D38F8888925c724Ab1B739E4794f3",
      "0x8F29929fC7094318BF562f981b04ecfA177Ecc54",
      "0x6518Bcb59B8E40A5a24189217912C511b783590f",
      "0x380cb6B16Ee5AbbB8A635e55e91c6F0eb982D7b6"
    ]
  }'
```

#### 4. Download (After Approvals)
```bash
curl -X GET "http://127.0.0.1:8000/files/download/1" \
  -G \
  --data-urlencode "username=admin" \
  --data-urlencode "key_id=0x..." \
  -o downloaded_file.bin
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | find "8000"

# Kill the process and restart
```

### Frontend Won't Start
```bash
cd frontend
rm -r node_modules
npm install
npm start
```

### File Upload Fails
- Check username is registered
- Ensure user role is "admin"
- Policy format: `role:admin AND department:IT`

### Download Fails
- Ensure file was uploaded first
- Check File ID is correct
- Verify Ganache is running
- Check contract address in DEPLOYMENT_INFO.json

### Ganache Connection Error
- Ensure Ganache is running: `ganache-cli --host 127.0.0.1 --port 7545`
- Verify MetaMask is set to Ganache network

---

## 📊 Architecture Diagram

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Backend    │────────▶│   Ganache    │
│  (React)    │         │  (FastAPI)   │         │ (Blockchain) │
└─────────────┘         └──────────────┘         └──────────────┘
                              │
                              │ (AES + ABE)
                              ▼
                        ┌──────────────┐
                        │   Database   │
                        │   (SQLite)   │
                        └──────────────┘
```

---

## ✅ Feature Checklist

- [x] Register/Login
- [x] Upload encrypted files (admin only)
- [x] Request blockchain approval
- [x] Simulate approvals (local Ganache)
- [x] 4-of-7 threshold enforcement
- [x] Download decrypted files
- [x] Attribute-based access control
- [x] Audit trail (blockchain)

---

## 🎯 Next Steps

1. **Test the complete flow** using the scenarios above
2. **Check logs** in browser console and backend terminal for errors
3. **Deploy to cloud** (AWS, Azure) when ready
4. **Add production security** (password hashing, HTTPS, etc.)

---

## 📞 Support

If you encounter issues:
1. Check backend logs (terminal where `uvicorn` is running)
2. Check browser console (F12 → Console)
3. Verify Ganache is running and has transactions
4. Ensure MetaMask is connected to correct network

---

**You're all set! Start the frontend and begin testing.** 🚀

