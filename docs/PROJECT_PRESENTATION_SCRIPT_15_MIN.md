# 15‑Minute Presentation Script — Secure Data Sharing (ABE Policy + Blockchain Approvals)

Use this as a **verbatim talk track**. It’s time‑boxed and matches the code in this repo.

---

## 0:00 – 0:45  Title + Problem
**Say:**
- “My capstone is Secure Data Sharing using an ABE-style access policy plus blockchain-based threshold approval.”
- “Goal: store files encrypted, allow only eligible users to decrypt, and require decentralized approval so no single authority can grant access alone.”

**Key claim:**
- “Even if you satisfy the policy, you still need on-chain approvals.”

---

## 0:45 – 2:00  What you built (3 bullets)
**Say:**
1) “Files are encrypted with AES-256-CBC before storage.”
2) “Access is controlled by an attribute policy string like `(role:admin OR role:manager) AND (dept:IT) AND clearance:high`.”
3) “Authorities vote on a Ganache smart contract. Decryption is allowed only after 4-of-7 approvals.”

**Show (optional):**
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## 2:00 – 4:30  Architecture overview (how components connect)
**Say (point to the architecture):**
- “Frontend is React, backend is FastAPI, database is SQLite, encrypted blobs are stored on disk, and approvals are stored on-chain.”

**Connect it to real files:**
- “Backend entrypoint is `backend/main.py` (creates DB + seeds users + mounts routes).”
- “File APIs are in `backend/api/file_routes.py`.”
- “Access/approval APIs are in `backend/api/access_routes.py`.”
- “Blockchain integration is `backend/blockchain/blockchain_auth.py` reading `backend/blockchain/DEPLOYMENT_INFO.json`.”
- “Smart contract is `contracts/KeyAuthority.sol`.”

**One-sentence data rule:**
- “Encrypted file bytes go to disk, while metadata + policy + encrypted AES key go to SQLite.”

---

## 4:30 – 6:30  Algorithms (what is working internally)

### Algorithm A — AES file encryption (confidentiality)
**Say:**
- “We never store the plaintext file. We store only an AES-encrypted blob.”
- “AES key is random 256-bit. A new IV is created per file.”

**Explain the steps (simple):**
1) Generate a random 32-byte AES key.
2) Generate a random 16-byte IV.
3) Pad file bytes using PKCS#7.
4) Encrypt using AES-256-CBC.
5) Save `IV + ciphertext` to disk.

**Where in code:** `backend/aes/aes_utils.py` and blob is saved via `backend/storage/file_storage.py`.

### Algorithm B — “ABE policy” evaluation (authorization)
**Say (be very clear to reviewer):**
- “This project enforces ABE-style policies, but CP-ABE is simulated: the policy check decides whether the AES key can be recovered.”

**Explain the policy algorithm:**
- Policy is a string like:
  - `(role:admin OR role:manager) AND (dept:IT OR dept:Finance) AND clearance:high`
- User has an attribute set like:
  - `{role:employee, dept:IT, clearance:high}`
- We evaluate:
  1) Split the policy by `AND` into groups.
  2) For each group, split by `OR` into alternatives.
  3) The policy is satisfied if **every AND-group has at least one OR-alternative present** in the user’s attribute set.

**Where in code:** `backend/abe/cpabe_utils.py` (`policy_satisfied`).

### Algorithm C — Blockchain 4-of-7 threshold approvals (decentralized control)
**Say:**
- “Authorities are listed in the smart contract. Each authority can approve a request only once.”
- “The contract counts approvals; if approvals ≥ threshold (4), the request is approved.”

**Explain the logic:**
1) Backend generates a `key_id` for `(file_id, user_id, timestamp)`.
2) Authorities vote by calling `approveKey(keyId)`.
3) Contract increments `approvals[keyId]` and tracks who already voted.
4) Backend checks `isApproved(keyId)` before allowing download.

**Where in code:**
- Contract: `contracts/KeyAuthority.sol`
- Backend web3 integration: `backend/blockchain/blockchain_auth.py`

### Algorithm D — MetaMask signature verification (proof of wallet control)
**Say:**
- “Before download, the user signs a message in MetaMask.”
- “Backend recovers the signer address from the signature and compares it with the claimed address.”

**Explain the steps:**
1) Frontend calls `personal_sign(message, address)`.
2) Backend uses ECDSA recovery to compute `recovered_address`.
3) If `recovered_address == address`, the signature is valid.

**Where in code:**
- Frontend: `frontend/src/pages/Download.js`
- Backend: `backend/api/access_routes.py` (`/api/access/verify-signature`)

---

## 6:30 – 8:45  Upload flow (admin)
**Say:**
- “Upload is admin-only.”
- “On upload, backend encrypts file data with AES and stores it.”
- “Then it stores a policy and an encrypted AES key that is only recoverable if user attributes satisfy the policy.”

**Show (recommended):**
1) UI page: `http://localhost:3000/upload`
2) Select file and choose policy values

**Explain what happens in code (high level):**
- `POST /files/upload` in `backend/api/file_routes.py`
  - generates AES key (`backend/aes/aes_utils.py`)
  - encrypts file (AES)
  - stores encrypted blob (`backend/storage/file_storage.py`)
  - encrypts AES key under policy (`backend/abe/cpabe_utils.py`)
  - stores record in DB (`SecureFile` in `backend/models.py`)

**Say the output:**
- “Backend returns `file_id`.”

---

## 8:45 – 12:30  Approval + signature + download flow (user)
**Say:**
- “A user first requests an approval key id.”
- “Authorities approve on blockchain.”
- “User also proves identity by signing a message with MetaMask.”
- “Only then download succeeds.”

**Very important integration statement:**
- “The final download route enforces BOTH checks: blockchain approval threshold AND policy satisfaction.”

### Step 1: Request approvals
**Show:** `http://localhost:3000/download`

**Say:**
- “When I click request approval, frontend calls `POST /api/access/request-key-approval`.”
- “Backend returns a `key_id` and list of authority addresses.”

**Explain what backend actually does:**
- “It does NOT push keys to authorities. It creates an on-chain approval tracking ID and tells the UI which authorities exist.”

### Step 2: On-chain approvals (4-of-7)
**Say:**
- “In real life, each authority votes separately. For demo, I simulate 4 approvals.”

**Show:** click “Simulate approvals” (Download page).

**Tie to smart contract:**
- “`contracts/KeyAuthority.sol` increments `approvals[keyId]` and `isApproved(keyId)` becomes true once approvals reach threshold.”

**Where to prove it live:**
- “We can query `GET /api/access/approval-status/{key_id}` to show the approval count coming from the contract.”

### Step 3: Signature verification
**Say:**
- “Now I verify signature: MetaMask signs a message, backend recovers the signer and validates it.”

**Show:** click “Verify signature with MetaMask”

### Step 4: Download
**Say:**
- “Finally I download. Backend checks in this exact order:”
  1) “`isApproved(key_id)` on blockchain must be true.”
  2) “User attributes from DB must satisfy the stored policy.”
  3) “Only then AES decrypt happens and plaintext is streamed.”

**Show:** click “Download”

---

## 12:30 – 13:45  Security reasoning (what is protected)
**Say:**
- “Confidentiality: file bytes are encrypted at rest using AES.”
- “Authorization: policy check enforces who is eligible.”
- “Decentralized control: 4-of-7 approvals are required, preventing a single authority from granting access.”

**Important clarification (reviewer-ready):**
- “This repo uses an ABE-style policy enforcement with a simulated CP-ABE mechanism (policy evaluator + key wrapping). The actual file encryption is real AES.”

---

## 13:45 – 14:30  Files I will open if asked “show me code”
Pick 3–4 only (don’t open everything):
1) `backend/api/file_routes.py` — upload + download orchestration
2) `backend/api/access_routes.py` — approval request + simulate approvals + signature verify
3) `backend/blockchain/blockchain_auth.py` — reads contract, checks `isApproved` and approvals
4) `contracts/KeyAuthority.sol` — minimal threshold voting logic

---

## 14:30 – 15:00  Closing + Q&A prepared answers

### Q: “What happens if blockchain is down?”
**Answer:** “Download returns error because approval can’t be verified; backend reports blockchain unavailable/misconfigured.”

### Q: “Where are the policies stored?”
**Answer:** “In SQLite `SecureFile.policy`.”

### Q: “Where is the encrypted key stored?”
**Answer:** “In SQLite `SecureFile.encrypted_key`, wrapped and only decrypted if policy matches.”

### Q: “What is the exact access condition?”
**Answer:** “Approved on-chain AND policy satisfied. Both are required.”

### Q: “Is the key split among authorities?”
**Answer:** “In the main demo download flow, no: authorities vote on-chain. The repo contains optional Shamir share code, but the enforced gate is on-chain approvals + policy satisfaction.”

### Q: “Why do you need signature if login exists?”
**Answer:** “Signature proves wallet control; it’s an extra identity proof step for the decentralized part.”

---

## Optional: 30-second demo checklist (if time is short)
1) Show `/upload` as admin → upload → get `file_id`
2) Go to `/download` as user → request approval → simulate approvals
3) Verify signature → download

