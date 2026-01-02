# Blockchain & ABE Architecture - Corrected Explanation

## What You're Actually Using

Your project uses **THRESHOLD APPROVAL AUTHENTICATION**, NOT threshold cryptography.

---

## 4 Key Corrections

### ❌ MISMATCH 1: "Backend sends requests to authorities"

**What you wrote:** Backend sends approval request to 7 authorities

**What actually happens:**
- Backend does NOT push requests to authority wallets
- Authorities must manually approve by calling the smart contract
- OR you use the `/api/access/simulate-approvals` endpoint to simulate approvals (for testing)

**Correct description:**
> Authorities approve by calling the smart contract (simulated locally via the `/api/access/simulate-approvals` endpoint for testing).

---

### ❌ MISMATCH 2: "AES key is split into 7 shares"

**What you wrote:** AES key is split into 7 cryptographic shares (Shamir's Secret Sharing)

**What your code actually does:**
- NO cryptographic key splitting happens in the download flow
- The full AES key is stored in the database (encrypted_key column)
- Authorities do NOT hold shares
- Blockchain approval is LOGICAL only (vote tracking), not mathematical (key reconstruction)

**Correct description:**
> The AES key is released from the database only after blockchain confirms 4-of-7 approvals. This is threshold approval, not threshold cryptography.

---

### ❌ MISMATCH 3: "Each authority holds a key share"

**What you wrote:** Each authority has a cryptographic share of the AES key

**What actually happens:**
- Authorities do NOT hold key material
- Authorities only VOTE (approve/reject access)
- The full AES key stays in the database until approval threshold is reached

**Correct description:**
> Each authority provides an approval vote recorded on the blockchain. The backend releases the full decryption key only after ≥4 authorities approve.

---

### ❌ MISMATCH 4: "Backend sends requests to authorities"

**What you wrote:** Backend initiates requests to all 7 authorities

**What actually happens:**
- Backend does NOT contact authorities
- Backend only creates an approval record (key_id)
- Authorities must independently interact with the smart contract
- OR you call `/api/access/simulate-approvals` to simulate authority approvals (for testing)

**Correct description:**
> Authorities approve independently by calling the smart contract (simulated via test endpoint). Backend does not notify or push requests to authorities.

---

## Accurate Data Flow

```
User requests download (file_id=6)
    ↓
Backend generates key_id = hash(file_id + user_id)
    ↓
Backend creates approval request: POST /api/access/request-key-approval
    ↓
⚠️ Backend DOES NOT send to authorities
    ↓
Test/Admin simulates approvals: POST /api/access/simulate-approvals
    ↓ 
4 authorities call contract.approveKey(key_id) or simulated via endpoint
    ↓
BLOCKCHAIN RECORDS: approvals[key_id] = 4
    ↓
User requests decrypt: POST /api/access/decrypt
    ↓
Backend checks: contract.isApproved(key_id) → TRUE (4 ≥ threshold)
    ↓
Backend retrieves full AES key from database
    ↓
Backend decrypts file content
    ↓
Browser receives file with correct filename and PDF content-type
```

---

## Technology Stack (Corrected)

| Component | Technology | Purpose | Reality |
|-----------|-----------|---------|---------|
| **Encryption** | AES-256 | Encrypt file content | ✅ Working |
| **Access Control** | ABE Policy | Attribute-based policies | ✅ Working (prevents wrong users) |
| **Threshold** | Blockchain Approval (4-of-7) | Requires majority vote | ✅ Working (logical only) |
| **Key Splitting** | Shamir SSS (implemented) | Distribute shares | ❌ NOT USED (full key stored in DB) |
| **Authority Shares** | Blockchain votes | Track approval | ✅ Authorities vote (no key material) |

---

## For Your Exam / Presentation

**Say this:**

> My system uses **threshold approval authentication** where 4 out of 7 authorities must vote on the blockchain to allow decryption. It does NOT use threshold cryptography; authorities do not hold cryptographic key shares. Instead, the full AES decryption key is stored securely in the database and released only after the blockchain confirms sufficient approvals.

---

## Code Files Updated With Accurate Comments

- ✅ `backend/blockchain/blockchain_auth.py` — Updated docstrings to clarify voting (not pushing)
- ✅ `backend/abe/abe_key_manager.py` — Updated comments to clarify Shamir code is NOT used in download flow
- ✅ `backend/blockchain/blockchain_utils.py` — Clear comments on contract interactions

---

## Project Status

**Your system is working correctly.** The code matches your intended functionality:
- Users can only download after attributes match policy
- 4-of-7 blockchain approvals required
- Files download with correct filenames and content-types

The fixes were **accuracy of documentation and comments**, not code logic changes.

✅ **Ready for exam/presentation with correct terminology!**
