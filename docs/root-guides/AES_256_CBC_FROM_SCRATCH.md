# AES-256 (CBC) — From Scratch + Algorithm Diagrams

This project uses **AES-256 in CBC mode** to encrypt file bytes (see `backend/aes/aes_utils.py`).

![AES-256-CBC full operations (project-specific)](../assets/aes256cbc_full_detail.svg)

If you want the short takeaway:
- **AES** is a fast symmetric block cipher (block size **128 bits**).
- **AES-256** means the secret key is **256 bits** and encryption uses **14 rounds**.
- **CBC** chains blocks using an **IV** (random 16 bytes) and requires **padding**.
- Your stored blob format is: `iv(16 bytes) + ciphertext`.

---

## 1) “Big Picture” (how your system encrypts a file)

```mermaid
flowchart TD
    A[User selects file] --> B[Read file bytes]
    B --> C[Generate random AES-256 key (32 bytes)]
    C --> D[PKCS7 pad file bytes to 16-byte blocks]
    D --> E[Generate random IV (16 bytes)]
    E --> F[AES-256-CBC encrypt]
    F --> G[Store blob = IV || Ciphertext]
    C --> H[Encrypt AES key using CP-ABE policy]
    H --> I[Store ABE-encrypted key + metadata]
    G --> J[Upload encrypted blob]
```

In your code:
- `generate_aes_key()` → step C
- `encrypt_file()` / `encrypt_blob()` → steps D–G
- CP-ABE key protection happens elsewhere (ABE module)

---

## 2) AES basics (what “AES-256” means)

### Parameters
- Block size: **128 bits** (16 bytes)
- Key size: **256 bits** (32 bytes)
- Number of rounds: **14**
- State: AES operates on a **4×4 byte matrix** (16 bytes total)

### State layout (concept)
AES treats 16 bytes as:

$$
\text{State} = \begin{bmatrix}
 b_0 & b_4 & b_8 & b_{12}\\
 b_1 & b_5 & b_9 & b_{13}\\
 b_2 & b_6 & b_{10} & b_{14}\\
 b_3 & b_7 & b_{11} & b_{15}
\end{bmatrix}
$$

---

## 3) AES-256 encryption rounds (internal algorithm “image”)

AES encryption is:
1. Key expansion → produce **round keys**
2. Initial round: `AddRoundKey`
3. Rounds 1..13: `SubBytes → ShiftRows → MixColumns → AddRoundKey`
4. Final round (14): `SubBytes → ShiftRows → AddRoundKey` (no MixColumns)

```mermaid
flowchart TD
    K[256-bit Key] --> KS[Key Expansion]
    KS --> RK0[RoundKey 0]
    KS --> RK14[RoundKey 14]

    P[Plaintext Block (16 bytes)] --> ARK0[AddRoundKey (RK0)]
    ARK0 --> R1[Round 1..13]
    R1 -->|each round| SB[SubBytes]
    SB --> SR[ShiftRows]
    SR --> MC[MixColumns]
    MC --> ARK[AddRoundKey (RK1..RK13)]
    ARK --> R1

    R1 --> FR[Final Round (14)]
    FR --> SB2[SubBytes]
    SB2 --> SR2[ShiftRows]
    SR2 --> ARK2[AddRoundKey (RK14)]
    ARK2 --> C[Ciphertext Block (16 bytes)]
```

Notes:
- **SubBytes**: byte substitution via an S-box
- **ShiftRows**: rotates rows of the state
- **MixColumns**: linear mixing in GF(2^8)
- **AddRoundKey**: XOR with round key

---

## 4) CBC mode (how blocks are chained)

AES encrypts *one 16-byte block at a time*. CBC makes it work for arbitrary-length data by chaining blocks.

### CBC encryption
Let $P_i$ be plaintext blocks, $C_i$ ciphertext blocks, and IV is $C_0$.

$$
C_0 = IV\\
C_i = AES_{K}(P_i \oplus C_{i-1})
$$

```mermaid
flowchart LR
    IV[IV (16 bytes)] --> XOR1((XOR))
    P1[P1] --> XOR1
    XOR1 --> E1[AES Encrypt (K)]
    E1 --> C1[C1]

    C1 --> XOR2((XOR))
    P2[P2] --> XOR2
    XOR2 --> E2[AES Encrypt (K)]
    E2 --> C2[C2]

    C2 --> XOR3((XOR))
    P3[P3] --> XOR3
    XOR3 --> E3[AES Encrypt (K)]
    E3 --> C3[C3]
```

### CBC decryption
$$
P_i = AES^{-1}_{K}(C_i) \oplus C_{i-1}
$$

```mermaid
flowchart LR
    IV[IV (C0)] --> XOR1((XOR))
    C1[C1] --> D1[AES Decrypt (K)]
    D1 --> XOR1
    XOR1 --> P1[P1]

    C1 --> XOR2((XOR))
    C2[C2] --> D2[AES Decrypt (K)]
    D2 --> XOR2
    XOR2 --> P2[P2]
```

---

## 5) Padding (PKCS7) — required for CBC

CBC requires plaintext length to be a multiple of 16 bytes.

**PKCS7 padding** adds $n$ bytes each with value $n$.
- If the plaintext is already a multiple of 16, PKCS7 adds a full block of padding (16 bytes of `0x10`).

Example (concept):
- If you need 5 bytes of padding → append: `05 05 05 05 05`

Your code uses:
- `padding.PKCS7(128).padder()` where 128 = block size in **bits**.

---

## 6) Your stored encrypted format (matches `aes_utils.py`)

### Blob format
- `iv` is 16 bytes
- `ciphertext` is N bytes (multiple of 16)

Stored blob:

$$
\text{blob} = IV \;||\; ciphertext
$$

In code:
- `encrypt_blob(file_bytes, key)` returns `iv + ciphertext`
- `decrypt_blob(encrypted_blob, key)` splits the first 16 bytes as IV

---

## 7) From-scratch pseudocode (end-to-end)

### Encrypt (CBC + PKCS7)
```text
encrypt(fileBytes, key32):
  iv = random(16)
  padded = pkcs7_pad(fileBytes, blockSize=16)
  ciphertext = AES_CBC_Encrypt(key32, iv, padded)
  return iv || ciphertext
```

### Decrypt
```text
decrypt(blob, key32):
  iv = blob[0:16]
  ciphertext = blob[16:]
  paddedPlain = AES_CBC_Decrypt(key32, iv, ciphertext)
  plain = pkcs7_unpad(paddedPlain, blockSize=16)
  return plain
```

---

## 8) Important security note (integrity)

AES-CBC **does not provide integrity/authentication** by itself.
That means a modified ciphertext may decrypt into corrupted plaintext without being detected.

If you want modern best practice, consider:
- **AES-GCM** (authenticated encryption), or
- CBC + **HMAC** (encrypt-then-MAC)

This repo’s current AES logic focuses on confidentiality; integrity protection should be added separately if needed.

---

## 9) Where this lives in the repo

- AES implementation: `backend/aes/aes_utils.py`
- AES tests: `backend/aes/test_aes.py` and `tests/test_aes.py`
