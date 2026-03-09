# System Workflow Flowchart (Secure Data Sharing)

This flowchart describes the complete secure data sharing process: cryptographic confidentiality (AES), attribute-based access control (policy), and blockchain-based multi-authority authorization (4-of-7 approvals).

```mermaid
flowchart TD
  %% --- Styles ---
  classDef start fill:#0ea5e9,stroke:#0369a1,color:#fff;
  classDef action fill:#eef2ff,stroke:#6366f1,color:#111827;
  classDef decision fill:#fff7ed,stroke:#fb923c,color:#111827;
  classDef store fill:#ecfeff,stroke:#06b6d4,color:#111827;
  classDef chain fill:#f0fdf4,stroke:#22c55e,color:#111827;
  classDef end fill:#111827,stroke:#111827,color:#fff;

  %% --- Start / Init ---
  S([System Start]):::start
  I[Initialize services\n- Load .env config\n- SQLite metadata DB\n- MongoDB GridFS storage\n- Ganache/KeyAuthority contract]:::action
  S --> I

  %% --- Login ---
  L[User Login\n(username + password)]:::action
  A{Credentials valid?}:::decision
  I --> L --> A
  A -- No --> LERR[Reject login\n(show error)]:::end

  %% --- Role routing ---
  A -- Yes --> R{Role is Admin?}:::decision

  %% --- Admin upload flow ---
  U[Admin Upload File\n+ Build access policy\n(role/department/clearance)]:::action
  ENC[Encrypt file bytes\nAES-256-CBC with random AES key]:::action
  STORE[Store encrypted blob\nMongoDB Atlas GridFS\n(bucket: encrypted_files)]:::store
  META[Store metadata in SQLite\nsecure_files: filename, owner, policy\n+ store encrypted AES key struct]:::store
  SHARES[Split AES key into shares\nfor authorities (demo)]:::action

  R -- Yes --> U --> ENC --> STORE --> META --> SHARES

  %% --- Non-admin path ---
  R -- No --> BROWSE[Browse available files]:::action

  %% --- Request access / download flow ---
  REQ[Request access for a file\nCreate request tracking key_id]:::action
  POL{Policy satisfied\nby user attributes?}:::decision
  BC[Blockchain authorization\nRequire 4-of-7 approvals\n(KeyAuthority on Ganache)]:::chain
  SIG[Verify user signature\n(MetaMask personal_sign)]:::action
  LOAD[Load encrypted blob\nfrom GridFS]:::store
  DEC[Decrypt using AES key\n(ABE-derived key material)]:::action
  DL[Secure download\nstream decrypted bytes]:::action

  BROWSE --> REQ --> POL
  SHARES --> BROWSE

  POL -- No --> DENY[Access denied\n(policy mismatch)]:::end
  POL -- Yes --> BC --> SIG

  SIG -->|Verified + Approved| LOAD --> DEC --> DL
  SIG -->|Not verified| SIGERR[Stop\nSignature not verified]:::end

  BC -->|Not enough approvals| PEND[Pending\ncollect more approvals]:::action
  PEND --> BC

  %% --- Logout & audit ---
  OUT([Logout / End Session]):::end
  AUDIT[Audit / Logs\n- access requests\n- approval status\n- downloads/deletions]:::action

  DL --> AUDIT --> OUT

```

Notes
- **Confidentiality**: AES encrypts file bytes before storage.
- **Access control**: policy checks role/department/clearance.
- **Authorization**: blockchain multi-authority approval enforces 4-of-7 threshold.
