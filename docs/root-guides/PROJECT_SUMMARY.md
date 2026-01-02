# Secure Data Sharing - Project Summary

## Overview

This project implements secure file sharing using Attribute-Based Encryption (ABE), symmetric encryption (AES), and a blockchain-based approval workflow for decentralized access control. Files are stored encrypted on disk; access is controlled by attribute policies and a 4-of-7 authority approval process recorded on a local Ethereum-compatible blockchain (Ganache).

## Technologies & Tools Used

- Backend: FastAPI (Python), Uvicorn
- Database: SQLite (SQLAlchemy ORM)
- Password hashing: passlib (bcrypt)
- Symmetric Encryption: AES utilities in `backend/aes`
- Attribute-Based Encryption: simulated ABE utilities in `backend/abe` (policy checks)
- Blockchain: Web3.py + local Ganache network; smart contract `KeyAuthority` enforces 4-of-7 approvals
- Frontend: React (create-react-app) — pages in `frontend/src/pages`
- Storage: encrypted files on disk under `backend/storage/encrypted_files`
- Testing: pytest scripts in project root (`test_complete_flow.py`, etc.)

## High-level Flow (Upload → Download)

1. Upload (admin-only)
   - Admin uploads a file via `POST /files/upload` (frontend Upload page).
   - Backend encrypts file content with AES and stores encrypted file on disk.
   - AES key is encrypted/managed according to ABE policy and stored in database.
   - File metadata (filename, owner, policy, encrypted_key, file_path) saved in `users.db`.

2. Request Approval
   - A user requests download and the backend generates a unique `key_id` for the file+user.
   - Backend records an approval request; authorities must approve by interacting with the smart contract.
   - For local testing, `/api/access/simulate-approvals` can simulate authority approvals.

3. Authority Approval (4-of-7)
   - Each authority calls `approveKey(keyId)` on the `KeyAuthority` contract.
   - Contract records approvals and tracks which authority approved which key.
   - Once approvals >= 4 (threshold), `isApproved(keyId)` returns true.

4. Decrypt & Download
   - Backend checks blockchain approval via `contract.isApproved(keyId)`.
   - If approved, backend retrieves AES key, decrypts file, and returns the file to the user with correct filename and MIME type.

## Important Clarifications

- The system implements *threshold approval authentication* (4-of-7 voting) — authorities vote to approve access on-chain.
- The project does *not* perform threshold cryptography by default: authorities do not hold cryptographic key shares in the deployed flow. Key splitting code exists for future use, but the release of the AES key is gated by blockchain votes.
- Files themselves are stored on disk (not on blockchain).

## Key Files & Where to Look

- Backend entry: `backend/main.py`
- Auth routes: `backend/auth/routes.py`
- Upload/download: `backend/api/file_routes.py`
- Access & approval workflow: `backend/api/access_routes.py`
- ABE utilities: `backend/abe` (policy checks & helpers)
- Blockchain wrappers: `backend/blockchain` (utils & `blockchain_auth.py`)
- Frontend pages: `frontend/src/pages` (Login/Register/Upload/Download/Dashboard)

## How to Run Locally (quick)

1. Start Ganache (or ensure local Ethereum node at `http://127.0.0.1:7545`).
2. Start backend:
```bash
cd "c:\7th sem\CAPSTON PROJECT\code\secure-data-sharing"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
3. Start frontend:
```bash
cd frontend
npm install
npm start
```

## Notes & Next Steps

- For full cryptographic threshold secrecy, implement Shamir Secret Sharing for AES keys and distribute shares to authorities. Current implementation simulates voting only.
- Ensure backups of `users.db` and `backend/storage/encrypted_files` before removing any data.

---

Created by automated cleanup & documentation script.
