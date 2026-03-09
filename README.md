# Secure Data Sharing (ABE + Blockchain Approval)

This repository contains a capstone implementation of secure file sharing using:
- CP-ABE-style attribute policies for access control
- AES-256-CBC for file content encryption
- A local blockchain approval workflow (Ganache + Solidity contract)
- MongoDB Atlas (GridFS) for encrypted file blob storage

Backend: FastAPI + SQLAlchemy (SQLite)
Frontend: React

## Account model

Public self-registration is disabled.
- Accounts are created by an admin (UI: User Management).
- Admin can reset a user password and generate a new recovery code.
- Passwords and recovery codes are stored as hashes, so the app cannot display existing credentials.

## Run locally

If you want the fastest working demo, start with: `START_HERE.md`.

### Demo accounts

On backend startup, demo users are initialized automatically (see `backend/main.py`):

- Admin: `admin` / `admin123`
- Employee: `alice` / `alice123`

### 1) Ganache

```bash
ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545
```

### 2) Deploy the smart contract

Deploy `contracts/KeyAuthority.sol` and update `backend/blockchain/DEPLOYMENT_INFO.json` with the deployed contract address.

Recommended (auto compile + deploy to Ganache):

```bash
python -m pip install -r backend/requirements.txt
python scripts/deploy_contract_compiled.py
```

See: `docs/root-guides/REMIX_DEPLOYMENT_GUIDE.md`

### 3) Backend

This project stores encrypted file blobs in MongoDB (GridFS) by default, with an optional local fallback.

Configure environment variables (recommended):

1) Copy `.env.example` to `.env`
2) Choose one:
	- Offline demo: set `STORAGE_BACKEND=local`
	- Full setup: keep `STORAGE_BACKEND=mongo` and set `MONGODB_URI` (Atlas)

Environment variables:

- `STORAGE_BACKEND=mongo`
- `STORAGE_ALLOW_LOCAL_FALLBACK=true` (recommended for demos)
- `MONGODB_URI` (required if using mongo)
- `MONGODB_DB` (optional; default: `secure_data_sharing`)
- `MONGODB_FILES_BUCKET` (optional; default: `encrypted_files`)

```bash
cd "c:\\7th sem\\CAPSTON PROJECT\\code\\secure-data-sharing"
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 4) Frontend

```bash
cd frontend
npm install
npm start
```

UI: http://localhost:3000

## Documentation

- `docs/root-guides/QUICK_START.md`
- `docs/root-guides/QUICK_REFERENCE.md`
- `docs/root-guides/TESTING_GUIDE.md`
- `docs/root-guides/REMIX_DEPLOYMENT_GUIDE.md`
- `docs/root-guides/VS_CODE_SETUP_GUIDE.md`

## Notes

- If the contract address is missing/wrong, the access-control endpoints can return 503 with `contract_misconfigured`.
- This is a capstone/demo setup (local chain, local file storage, SQLite). Production deployment would require additional hardening.


