# MongoDB Atlas setup (for storing encrypted files in GridFS)

This project stores **encrypted file bytes** in **MongoDB GridFS** (Atlas) and stores metadata in SQLite.

## 1) Create Atlas DB user
1. Atlas → **Database Access** → **Add New Database User**
2. Create a username/password (save it)
3. Give role: **Read and write to any database** (for demo) or restrict to `secure_data_sharing`

## 2) Allow your IP in Network Access
1. Atlas → **Network Access**
2. Add your current IP
   - For quick demo you can temporarily use `0.0.0.0/0` (NOT recommended for production)

## 3) Set `.env`
Edit your project root `.env`:
- `MONGODB_URI=...` (SRV string from Atlas)
- `MONGODB_DB=secure_data_sharing`
- `MONGODB_FILES_BUCKET=encrypted_files`

If you want to **force** MongoDB only (no local fallback):
- `STORAGE_ALLOW_LOCAL_FALLBACK=false`

## 4) Verify connection
Run from project root:
```bash
python -m backend.test_mongo
```
Expected: `MongoDB connected successfully!`

## 5) Verify uploads go to MongoDB
1. Start backend.
2. Upload a file.
3. Check where it was stored:
```bash
python -m backend.verify_uploaded_storage
```
- `file_path=gridfs:<id>` → stored in MongoDB GridFS
- `file_path=local:<id>` → stored locally (fallback)

## 6) Verify inside Atlas UI
Atlas → **Browse Collections**:
- Database: `secure_data_sharing`
- Collections:
  - `encrypted_files.files` (metadata + filename + uploadDate)
  - `encrypted_files.chunks` (actual encrypted bytes)

## Common issue: TLS handshake errors
If you see: `SSL handshake failed ... TLSV1_ALERT_INTERNAL_ERROR`
- Try a different network (mobile hotspot often works)
- Ensure Atlas IP allowlist includes your current IP
- Some college/corporate networks block MongoDB ports (27017) or do SSL inspection

Quick runtime check (backend must be running):
- http://127.0.0.1:8000/storage/health
