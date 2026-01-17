# Secure Data Sharing Using ABE + Blockchain (Ganache) — Project Explanation (Presentation Notes)

This document is meant to be read directly during a viva/review.
It explains:
- what each folder/file is for
- where it is used (imports / API calls)
- how all pieces connect end-to-end

---

## 1) One‑line idea (what problem this solves)
We securely share files by **encrypting file content with AES**, **controlling who can decrypt using an attribute policy (“ABE policy”)**, and **requiring decentralized 4‑of‑7 authority approvals stored on a blockchain (Ganache smart contract)** before decryption is allowed.

---

## 2) Tech stack (what you’re using)
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React + Axios
- **Crypto:** AES‑256‑CBC for file encryption; policy-enforced key wrapping (simulated CP‑ABE) using Fernet; optional Shamir Secret Sharing code exists
- **Blockchain:** Ganache local Ethereum network + Solidity smart contract `KeyAuthority` for threshold approvals
- **Wallet/signature:** MetaMask `personal_sign` + backend signature verification

---

## 3) Architecture (how components connect)

### Components
1. **React frontend** (UI)
2. **FastAPI backend** (API)
3. **SQLite database** (`users.db`) storing users + file metadata
4. **Local file storage** for encrypted blobs (`backend/storage/encrypted_files/`)
5. **Ganache + Smart Contract** for approval voting (`contracts/KeyAuthority.sol`)

### Data/control flow (big picture)
- Upload:
  1) Admin uploads file → backend encrypts and stores
  2) Backend stores encrypted file blob + encrypted AES key + policy
- Access request:
  3) User requests key approval → backend generates `key_id` and returns authority list
  4) Authorities approve on-chain (simulated in demo)
- Download:
  5) User signs a message in MetaMask → backend verifies signature
  6) Backend checks on-chain approvals (4-of-7) → then checks policy (attributes) → then decrypts and streams plaintext

---

## 4) What is “ABE” in this repo (important to explain clearly)

### What is real encryption here?
- The **file data is really encrypted** with AES-256-CBC in `backend/aes/aes_utils.py`.

### Where is “ABE” used?
- This project uses an **ABE-style attribute policy** to decide whether the user can obtain the AES key.
- In this repo, CP‑ABE is **simulated** in `backend/abe/cpabe_utils.py`:
  - It evaluates the policy string (supports `AND` / `OR`)
  - If satisfied, it allows decrypting the stored AES key (wrapped with Fernet)

### Why blockchain is included?
- Even if a user matches the policy, the system **still requires decentralized authority approvals** recorded on-chain.
- So the effective control is:

  **Decryption allowed only if:**

  $$\text{BlockchainApproved}(key\_id) \wedge \text{PolicySatisfied}(user\_attributes, file\_policy)$$

---

## 5) End‑to‑end demo flow (what to say during demo)

### Step A — Start services
- Start Ganache at `127.0.0.1:7545`
- Deploy `KeyAuthority.sol` to Ganache (Remix + MetaMask)
- Start backend at `127.0.0.1:8000`
- Start frontend at `localhost:3000`

### Step B — Login / users
- Backend auto-creates test users in `backend/main.py` (`admin`, `manager`, `alice`, `bob`, `charlie`).
- Frontend uses `/login` and stores user info in `localStorage`.

### Step C — Upload (admin only)
Frontend page: `frontend/src/pages/Upload.js`
- Admin selects policy values (role/department/clearance)
- Frontend sends multipart to `POST /files/upload`

Backend route: `backend/api/file_routes.py` → `upload_file`
- Reads file bytes
- Generates AES key (`generate_aes_key`)
- Encrypts file (`encrypt_file`)
- Saves encrypted blob to disk (`backend/storage/file_storage.py`)
- Encrypts AES key under policy (`backend/abe/cpabe_utils.py` → `encrypt_aes_key`)
- Stores metadata in SQLite as `SecureFile`

### Step D — Request on-chain approvals
Frontend page: `frontend/src/pages/Download.js` (or `DecentralizedAccess.js`)
- Calls `POST /api/access/request-key-approval`

Backend: `backend/api/access_routes.py`
- Uses `backend/blockchain/blockchain_auth.py` to:
  - create a `key_id`
  - return the list of authority addresses

### Step E — Simulate approvals (demo)
Frontend calls `POST /api/access/simulate-approvals`
- Backend sends transactions to Ganache from authority accounts
- Smart contract records votes: `approvals[keyId]++`

### Step F — MetaMask signature
Frontend calls `POST /api/access/verify-signature`
- Uses `personal_sign` to sign `Approve access for file <id>`
- Backend recovers signer address and verifies it matches

### Step G — Download / decrypt
Frontend calls `GET /files/download/{file_id}?username=...&key_id=...`
Backend route: `backend/api/file_routes.py` → `download_file`
- Checks the blockchain isApproved(key_id)
- Loads user’s attributes from DB (`User` table)
- Checks the ABE policy and decrypts AES key (`decrypt_aes_key`)
- Loads encrypted blob from disk
- AES decrypts and streams plaintext back

---

## 6) Database and storage (what is stored where)

### SQLite DB
- File: project root `users.db` (configured in `backend/database.py`)
- Tables (defined in `backend/models.py`):
  - `users` → username/password-hash + role/department/clearance
  - `secure_files` → filename/owner/file_path/encrypted_key/policy
  - `recovery_codes` → username + recovery code hash

### Disk storage
- Encrypted blobs: `backend/storage/encrypted_files/<uuid>`
- Optional shares: `storage/shares/<file_id>/<authority>.share` (written by ABE key manager)

---

## 7) File-by-file explanation (why each file exists, where it is used)

### Root files
- `README.md`
  - Project overview + how to run.
- `START_HERE.md`
  - Quick demo steps.
- `START_EVERYTHING.bat` / `START_EVERYTHING.sh`
  - “Operator instructions” to start Ganache/backend/frontend and deploy the contract.
- `pytest.ini`
  - pytest configuration.
- `deploy_to_ganache.py`
  - Helper for saving contract address + metadata into `backend/blockchain/DEPLOYMENT_INFO.json` after Remix deployment.
- `init_test_data.py`
  - Old/alternate script to insert test users into a different sqlite path (note: backend uses `users.db`; this script uses `sqlite/test.db`).
- `run_decrypt_flow.py`
  - Scripted API client to request approvals, simulate approvals, then call `/api/access/decrypt` and save output.
- `test_complete_flow.py`
  - End-to-end test script using HTTP requests to validate upload + approval + download flows.
- `test_alice_download.py`
  - Focused script proving a policy that Alice matches succeeds.

### `backend/` (FastAPI backend)
- `backend/main.py`
  - FastAPI app entrypoint.
  - Creates DB tables.
  - Seeds default users.
  - Includes routers: auth + files + access.
- `backend/database.py`
  - SQLAlchemy engine + session.
  - Sets DB path to project root `users.db`.
- `backend/models.py`
  - SQLAlchemy models: `User`, `SecureFile`, `RecoveryCode`.
- `backend/schemas.py`
  - Pydantic request bodies: login/change password/forgot reset/user create.

#### `backend/auth/` (authentication and admin user management)
- `backend/auth/routes.py`
  - API endpoints:
    - `/login`
    - `/change-password`
    - `/forgot-password/reset`
    - Admin endpoints under `/admin/users` (HTTP Basic admin auth)
  - Creates recovery codes.
  - Registration is disabled.
- `backend/auth/auth_utils.py`
  - Password hashing helpers (bcrypt via passlib).
- `backend/auth/__init__.py`
  - Package marker.

#### `backend/api/` (API routers)
- `backend/api/file_routes.py`
  - `/files/all` list files
  - `/files/upload` encrypt + save (admin only)
  - `/files/download/{id}` verify blockchain + policy + decrypt
  - `/files/{id}` delete (admin only)
- `backend/api/access_routes.py`
  - `/api/access/blockchain/status` health/status
  - `/api/access/request-key-approval` create key_id + return authorities
  - `/api/access/simulate-approvals` submit approval txs to Ganache
  - `/api/access/approval-status/{key_id}` read on-chain approvals
  - `/api/access/verify-signature` verify MetaMask signature (+ optional policy check)
  - `/api/access/decrypt` alternate decrypt endpoint (share-reconstruction style demo)

#### `backend/aes/` (AES file encryption)
- `backend/aes/aes_utils.py`
  - AES-256-CBC encrypt/decrypt helpers.
- `backend/aes/test_aes.py`
  - Unit test for AES utils.

#### `backend/abe/` (ABE policy + key management)
- `backend/abe/cpabe_utils.py`
  - Policy evaluation (`AND`/`OR`) + key wrapping via Fernet.
  - Used by `backend/api/file_routes.py` upload/download.
- `backend/abe/abe_key_manager.py`
  - Contains Shamir Secret Sharing code to split/reconstruct AES keys as shares.
  - Shares are stored under `storage/shares/`.
  - In the **main download path** (`/files/download/{id}`), the AES key is decrypted from DB using policy check, not reconstructed from shares.
- `backend/abe/test_cpabe.py`
  - Tests for policy/key wrapping utilities.

#### `backend/storage/` (encrypted blob persistence)
- `backend/storage/file_storage.py`
  - Saves/loads encrypted blobs on local disk.
  - Used by `backend/api/file_routes.py`.
- `backend/storage/s3_storage.py`
  - Optional alternative storage backend for AWS S3 (not used in default local demo).
- `backend/storage/encrypted_files/`
  - Runtime folder containing encrypted blobs.

#### `backend/blockchain/` (Ganache + smart contract integration)
- `backend/blockchain/blockchain_auth.py`
  - Core web3 integration.
  - Loads ABI from `contracts/KeyAuthorityABI.json`.
  - Validates contract address and threshold.
  - Reads `approvals()` and `isApproved()`.
  - Sends transactions in simulation endpoints.
- `backend/blockchain/DEPLOYMENT_INFO.json`
  - Stores the deployed contract address + threshold + authorities list.
  - Must match current Ganache accounts & deployed contract.
- `backend/blockchain/file_storage.py`
  - Currently empty (placeholder).

- `backend/requirements.txt`
  - Python dependencies (FastAPI, SQLAlchemy, web3, cryptography libs, pytest).

### `contracts/` (Solidity smart contract)
- `contracts/KeyAuthority.sol`
  - Contract that stores authorities and approval counts.
  - Rule: key is approved if `approvals[keyId] >= threshold`.
- `contracts/KeyAuthorityABI.json`
  - ABI used by backend to call contract methods.
- `contracts/deploy.js`
  - Deployment script (Hardhat/Ethers style) that also writes `backend/blockchain/DEPLOYMENT_INFO.json`.

### `frontend/` (React UI)
- `frontend/package.json`
  - Frontend dependencies and scripts.
- `frontend/src/index.js`
  - React bootstrap.
- `frontend/src/App.js`
  - Router mapping URLs to pages.
- `frontend/src/api/api.js`
  - Axios base instance.

#### `frontend/src/pages/` (UI screens)
- `Login.js`
  - Calls backend `/login` and writes user info into `localStorage`.
- `Dashboard.js`
  - Main navigation hub.
- `Upload.js`
  - Admin upload UI; calls `/files/upload` and `/files/all`.
- `Download.js`
  - Full user flow: request approvals → simulate approvals → MetaMask signature → download via `/files/download/{id}`.
- `DecentralizedAccess.js`
  - Separate page focusing on blockchain status + approvals polling + simulation.
- `Admin.js` / `AdminUsers.js`
  - Admin management screens. Backend endpoints used are in `backend/auth/routes.py` under `/admin/users`.
- `ChangePassword.js` / `ForgotPassword.js`
  - Password management flows that call `/change-password` and `/forgot-password/reset`.

### `docs/` (project documentation)
- `docs/README.md`
  - Docs index.
- `docs/TESTING_REPORT.md`
  - Testing evidence.
- `docs/root-guides/QUICK_REFERENCE.md`, `QUICK_START.md`, `TESTING_GUIDE.md`, `VS_CODE_SETUP_GUIDE.md`, `REMIX_DEPLOYMENT_GUIDE.md`
  - Detailed guides for running/testing/deploying.

### `scripts/` (helpers / experiments)
- `scripts/update_deployment_address.py`
  - CLI tool to update the contract address in `DEPLOYMENT_INFO.json`.
- `scripts/dump_users.py`
  - Reads `users.db` and prints users.
- `scripts/verify_manager.py`
  - Verifies password hash for a specific user.
- `scripts/deploy_fast.py` and other deploy scripts
  - Alternative deployment approaches (web3/hardcoded bytecode/artifacts) to speed up local deployment.

### `tests/` (test suite)
- `tests/test_api.py`, `tests/test_aes.py`, `tests/test_cpabe.py`
  - Automated tests for API and crypto utilities.
- `tests/tests/test_performance.py`
  - Performance-related testing.

---

## 8) Key connections you can quote in presentation (important “why/how” links)
- React pages call FastAPI endpoints using Axios:
  - `Upload.js` → `/files/upload`, `/files/all`
  - `Download.js` → `/api/access/request-key-approval`, `/api/access/simulate-approvals`, `/api/access/approval-status/{key}`, `/api/access/verify-signature`, `/files/download/{id}`
- Backend routes orchestrate services:
  - `file_routes.py` imports `aes_utils`, `cpabe_utils`, `storage/file_storage`, `blockchain_auth`
  - `access_routes.py` uses `blockchain_auth` for on-chain checks and approvals
- Blockchain contract is minimal and purpose-built:
  - `approveKey(keyId)` increments approval count once per authority
  - `isApproved(keyId)` enforces threshold

---

## 9) Common reviewer questions (ready answers)

### Q1: “Is this real CP‑ABE?”
Answer: The **policy enforcement is ABE-style**, but the repo currently uses a **simulated CP‑ABE mechanism** for key wrapping (Fernet + policy check). The file is still strongly encrypted with AES.

### Q2: “Where does decentralization happen?”
Answer: The decentralization is in **approval voting on-chain** (4-of-7). No single authority can approve alone.

### Q3: “Why also require MetaMask signature?”
Answer: It proves the requester controls a wallet account and prevents blind requests; backend verifies signature.

### Q4: “Where is the encrypted data stored?”
Answer: Encrypted blobs are stored on disk in `backend/storage/encrypted_files/`, and metadata + encrypted key are in SQLite `users.db`.

---

## 10) What to show live (minimum demo checklist)
1. Open `http://127.0.0.1:8000/docs` to show APIs.
2. Login as admin → upload a file with a clear policy.
3. Login as a user that matches the policy.
4. Request approvals → simulate approvals → show on-chain approval status.
5. Verify signature → download decrypted file.

