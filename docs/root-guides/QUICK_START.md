# Quick start

This is a short local setup guide for running the project.

## Start the backend
```bash
cd "c:\7th sem\CAPSTON PROJECT\code\secure-data-sharing"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for Uvicorn to start: `Uvicorn running on http://127.0.0.1:8000`

---

## Start the frontend
```bash
cd "c:\7th sem\CAPSTON PROJECT\code\secure-data-sharing\frontend"
npm start
```

Open: `http://localhost:3000`

---

## Test the flow

### Step 1: Login as admin
- **Username:** `admin`
- **Password:** `admin123`
- **Click:** Login

### Step 2: Upload a file
1. Click **Upload** tab
2. Choose any file (test.txt, image.jpg, etc.)
3. Select attributes:
   - Roles: Check `admin` ✓
   - Departments: Check `IT` ✓
   - Clearance: Check `high` ✓
4. Click **Upload Secure File**
5. **Save the File ID** (shown in success alert)

### Step 3: Login as a different user
- Click **Logout**
- **Username:** `alice`
- **Password:** `alice123`
- Click **Login**

### Step 4: Download the file
1. Click **Download** tab
2. Enter **File ID** from Step 2
3. Username auto-fills with `alice`
4. Click **Request Approval**
   - Shows the Key ID and authority list
5. Click **Simulate Approvals (local)**
   - Sends approval transactions to Ganache
6. Click **Download Decrypted File**
   - The browser downloads the decrypted file

---

## What you should see

### Upload success
```
File uploaded successfully
File ID: 1
```

### Download success
```
Step 1: Request Approval
Step 2: Simulate Approvals (local)
Step 3: Download Decrypted File

Browser downloads: secure_file_1
```

---

## Test users

These users are created on backend startup for local testing.

### Admin
```
Username: admin
Password: admin123
Role: Admin | Dept: IT | Clearance: High
```

### IT user
```
Username: alice
Password: alice123
Role: User | Dept: IT | Clearance: High
```

### Finance user
```
Username: bob
Password: bob123
Role: User | Dept: Finance | Clearance: Medium
```

### HR user
```
Username: charlie
Password: charlie123
Role: User | Dept: HR | Clearance: Low
```

---

## 🔍 Advanced Testing

### Test Access Denied:
1. Upload file as `admin` (IT dept)
2. Logout
3. Login as `bob` (Finance dept)
4. Try to download → **❌ Access Denied**

### Test Admin-Only Upload:
1. Login as `alice` (not admin)
2. Go to Upload tab
3. See: **"🔒 Access Denied - Only administrators can upload files"**

---

## 📊 Monitoring

### Backend Logs:
```
Watch the terminal running Uvicorn for:
- POST /login → User authenticated
- POST /files/upload → File encrypted
- POST /api/access/request-key-approval → Key generated
- POST /api/access/simulate-approvals → Blockchain txs
- GET /files/download → File decrypted
```

### Ganache Transactions:
- Open Ganache GUI (if you have it open)
- See new transactions for each approval
- 4 transactions = 4 authorities approved

---

## 🛠️ Troubleshooting

### Backend won't start?
```bash
# Kill any running process on port 8000
netstat -ano | find "8000"
taskkill /PID <PID> /F

# Try again
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend won't start?
```bash
cd frontend
rm -r node_modules
npm install
npm start
```

### Can't connect to Ganache?
- Ensure Ganache is running: `ganache-cli --host 127.0.0.1 --port 7545`
- Check MetaMask is on Ganache network
- Verify contract address in backend config

### File download says "Access denied"?
- Check your user's attributes (role, dept, clearance)
- Verify file policy matches your attributes
- Try different attribute combinations in upload

---

## 🎯 What Each Component Does

| Component | Purpose |
|-----------|---------|
| **Upload Page** | Encrypt files with ABE policy (admin only) |
| **Download Page** | Request approval, get blockchain consensus, decrypt |
| **Blockchain** | 4-of-7 threshold approval (stored on Ganache) |
| **AES-256** | Encrypts actual file content |
| **ABE** | Controls who can decrypt (role + dept + clearance) |
| **Backend DB** | Stores users, files, metadata (SQLite) |

---

## 📈 Next Level Testing

### Test 1: Policy Matching
```
Upload as admin with: role:admin AND dept:IT AND clearance:high
Download as alice (admin, IT, high) → ✅ Success
Download as bob (user, Finance, medium) → ❌ Denied
```

### Test 2: Multiple Policies
```
Upload with: (role:admin OR role:manager) AND dept:IT
Only users with admin/manager role in IT can access
```

### Test 3: Blockchain Verification
```
Request approval but DON'T click simulate
Try to download → ❌ "Key not approved by blockchain"
Then click simulate and download → ✅ Success
```

---

## 🔐 Security Summary

Your system protects files with:
1. **AES-256 Encryption** - Military-grade file encryption
2. **Attribute-Based Encryption** - Access control via attributes
3. **Blockchain Verification** - 4-of-7 threshold consensus
4. **Password Hashing** - bcrypt for password security
5. **Session Management** - localStorage for session tracking

---

## 📞 Quick Reference

### API Endpoints (for advanced testing):
```bash
# Login
POST http://127.0.0.1:8000/login
Body: {"username": "admin", "password": "admin123"}

# Upload
POST http://127.0.0.1:8000/files/upload
FormData: file, policy, username

# Request Approval
POST http://127.0.0.1:8000/api/access/request-key-approval
Body: {"file_id": "1", "user_id": "alice", "user_attributes": {...}}

# Download
GET http://127.0.0.1:8000/files/download/1?username=alice&key_id=0x...
```

---

## 🎉 You're Ready!

1. ✅ Start backend
2. ✅ Start frontend
3. ✅ Login as admin
4. ✅ Upload file
5. ✅ Logout and login as different user
6. ✅ Download file
7. ✅ See file in Downloads folder

**That's it! The entire secure data sharing system is working.** 🚀

---

## 📞 Support

If you need help:
1. Check the console (F12 in browser)
2. Check backend logs (terminal)
3. Check Ganache for transactions
4. Read `IMPROVEMENTS_SUMMARY.md` for detailed info

Happy testing! 🎊

