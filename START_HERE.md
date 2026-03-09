# Start here (presentation demo)

Fast path to a working local demo.

If you only read one guide: `docs/root-guides/QUICK_REFERENCE.md`.

## One-command start

- Windows: `START_EVERYTHING.bat`
- macOS/Linux: `START_EVERYTHING.sh`

## Manual start (recommended for presenting)

1) Start Ganache (local blockchain)

```bash
ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545
```

2) Deploy the contract (auto)

```bash
python -m pip install -r backend/requirements.txt
python scripts/deploy_contract_compiled.py
```

If compilation/deploy fails on your network, deploy in Remix and just update `backend/blockchain/DEPLOYMENT_INFO.json`.

3) (Optional) Configure storage

- For an offline demo (no MongoDB Atlas): set `STORAGE_BACKEND=local` in `.env`.
- For full setup: copy `.env.example` 7 `.env` and set `MONGODB_URI`.

4) Start the backend (run from repo root)

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

5) Start the frontend

```bash
cd frontend
npm install
npm start
```

## Demo flow (happy path)

Pre-seeded demo accounts are created on backend startup:

- Admin: `admin` / `admin123`
- Employee: `alice` / `alice123`

Flow:
1) Log in as `admin`.
2) Upload a file and set an access policy.
3) Go to `/access` and request approvals.
4) Simulate approvals until threshold is met.
5) Download/decrypt from `/download`.

## Quick checks

- Backend docs: http://127.0.0.1:8000/docs
- API health: http://127.0.0.1:8000/

## Troubleshooting

| Problem | Fix |
|---|---|
| Ganache not reachable | Confirm `127.0.0.1:7545` and Ganache is running |
| Frontend cant reach API | Confirm backend is on `127.0.0.1:8000` |
| Contract misconfigured | Re-run `python scripts/deploy_contract_compiled.py` |
| MongoDB blocked/unavailable | Set `STORAGE_BACKEND=local` (or keep mongo + fallback) |

