Backend quick start and end-to-end test (Ganache + Remix + Backend)

Prerequisites
- Python 3.11+
- Node/Ganache running at http://127.0.0.1:7545 (Ganache GUI or CLI)
- MetaMask connected to Ganache (RPC http://127.0.0.1:7545)
- Install Python deps: `pip install -r requirements.txt` (see note below about charm-crypto)

1) Deploy the `KeyAuthority` contract
- Use Remix or the `contracts/deploy.js` script to deploy to Ganache.
- Save the deployed contract address into `backend/blockchain/DEPLOYMENT_INFO.json` with shape:
  {
    "contractAddress": "0x..."
  }

2) Start backend (from project root)
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

3) Upload a file (as admin)
- Use the `/files/upload` endpoint (multipart/form-data): `file`, `policy`, `username` (admin user must exist in DB).

4) Request key approval (user requests decryption)
- POST `/api/access/request-key-approval` with JSON:
  {
    "file_id": "<file_id>",
    "user_id": "<username>",
    "user_attributes": {"role":"admin","department":"IT","clearance":"high"}
  }
- The response contains `key_id` and `authorities` list.

5) Simulate approvals (local Ganache testing)
- Use POST `/api/access/simulate-approvals` with JSON:
  {
    "key_id":"0x...",
    "authority_addresses":["0x..","0x..","0x..","0x.."]
  }
- This sends approve transactions using Ganache unlocked accounts.

6) Download decrypted file via frontend or API
- Frontend `Download` page calls `/files/download/{file_id}` with query params `username` and `key_id`.
- Example cURL:
  ```bash
  curl -L -o secure_file.bin "http://127.0.0.1:8000/files/download/1?username=alice&key_id=0x..."
  ```

Notes
- `charm-crypto` is optional for local testing. If you want production CP-ABE functionality on Windows, consider using a Linux VM or WSL and install `charm-crypto` there.
- If the backend cannot find contract ABI or DEPLOYMENT_INFO, check `backend/blockchain` and the project `contracts` folder.

Contact
- If you want, I can add a script to auto-create `DEPLOYMENT_INFO.json` after deployment or wire the `deploy.js` output to the backend folder.
