# System Architecture (Component View)

This diagram shows the major components of the system and how data flows through them.

```mermaid
flowchart LR
  %% =====================
  %% Client / UI Layer
  %% =====================
  subgraph C[Client Layer]
    UI[React Frontend\n(frontend/src)]
    MM[MetaMask Wallet\n(ECDSA signature)]
  end

  %% =====================
  %% API Layer
  %% =====================
  subgraph A[API Layer]
    API[FastAPI Backend\n(backend/main.py)]

    subgraph R[Route Modules]
      AUTH[Auth Routes\nbackend/auth/routes.py]
      FILES[File Routes\nbackend/api/file_routes.py]
      ACCESS[Decentralized Access Routes\nbackend/api/access_routes.py]
    end
  end

  %% =====================
  %% Service Layer (inside backend)
  %% =====================
  subgraph S[Backend Services]
    AES[AES-256-CBC\nbackend/aes/aes_utils.py]
    ABE[ABE / Key Manager\nbackend/abe/abe_key_manager.py]
    STORE[Storage Backend\nbackend/storage/storage_backend.py]
    BC[Blockchain Service (Web3)\nbackend/blockchain/blockchain_auth.py]
  end

  %% =====================
  %% Data Layer
  %% =====================
  subgraph D[Data Layer]
    SQLITE[(SQLite DB\nusers, file metadata, policies\nbackend/database.py)]
    MONGO[(MongoDB Atlas - GridFS\nencrypted blobs\nBucket: encrypted_files)]
    SHARES[(Local Key Shares Storage\nstorage/shares/)]
    CHAIN[(Ganache Local Blockchain\nKeyAuthority.sol)]
  end

  %% =====================
  %% Edges: client <-> API
  %% =====================
  UI -->|HTTP/JSON| API
  UI <-->|Basic Auth| AUTH
  UI <-->|Upload / List / Delete| FILES
  UI <-->|Request approval / Decrypt| ACCESS
  UI <-->|Sign challenge| MM

  %% =====================
  %% Edges: API -> services
  %% =====================
  API --> AUTH
  API --> FILES
  API --> ACCESS

  FILES --> AES
  FILES --> STORE
  FILES --> SQLITE

  ACCESS --> BC
  ACCESS --> ABE
  ACCESS --> STORE
  ACCESS --> SQLITE
  ACCESS --> MM

  ABE --> SHARES
  STORE --> MONGO
  BC --> CHAIN

  %% =====================
  %% Notes (labels)
  %% =====================
  AES -. encrypt/decrypt file bytes .- STORE
  ABE -. policy check + key reconstruction .- ACCESS
  BC -. 4-of-7 threshold approvals .- ACCESS
```

## What each layer does

- **Client Layer**: React UI for admin + users; MetaMask provides a signature the backend verifies before decrypting.
- **API Layer (FastAPI)**: Implements authentication, file management, approval workflow, and secure download.
- **Backend Services**:
  - **AES**: Encrypts file bytes (ciphertext stored; plaintext never persisted).
  - **ABE/Key Manager**: Evaluates attribute policies and reconstructs an AES key from authority shares.
  - **Storage Backend**: Saves/loads encrypted blobs in MongoDB Atlas GridFS.
  - **Blockchain Service**: Talks to Ganache + the `KeyAuthority` contract to enforce threshold approvals.
- **Data Layer**:
  - **SQLite**: User accounts, file records, metadata, policies.
  - **MongoDB Atlas (GridFS)**: Encrypted file blobs.
  - **Local shares**: Authority key shares stored on disk for reconstruction.
  - **Ganache**: Approval/audit trail via smart contract.
