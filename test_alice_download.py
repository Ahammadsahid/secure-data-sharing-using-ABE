import requests
from io import BytesIO

API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("TEST: Upload file with policy that Alice can match")
print("=" * 70)

# Test with a policy that Alice CAN match
# Alice is: role=user, dept=IT, clearance=high
# So policy should be: role:user AND dept:IT AND clearance:high

print("\n1) Admin uploads file with policy:")
print("   Policy: role:user AND dept:IT AND clearance:high")
print("   (Alice matches all attributes)")

policy = "role:user AND dept:IT AND clearance:high"
files = {
    'file': ('test_alice_file.txt', BytesIO(b"Secret IT data for Alice!"), 'text/plain')
}
data = {
    'policy': policy,
    'username': 'admin'
}

res = requests.post(f"{API_BASE}/files/upload", files=files, data=data)
print(f"\n   Response: {res.status_code}")
if res.status_code == 200:
    file_id = res.json()['file_id']
    print(f"   File uploaded. ID: {file_id}")
else:
    print(f"   Upload failed: {res.text}")
    exit(1)

# Alice requests approval
print(f"\n2) Alice requests approval for file {file_id}")
res = requests.post(f"{API_BASE}/api/access/request-key-approval", json={
    "file_id": str(file_id),
    "user_id": "alice",
    "user_attributes": {
        "role": "user",
        "department": "IT",
        "clearance": "high"
    }
})

if res.status_code == 200:
    key_id = res.json()['key_id']
    print(f"   Approval requested. Key ID: {key_id[:30]}...")
else:
    print(f"   Request failed: {res.text}")
    exit(1)

# Simulate approvals
print("\n3) Simulate 4-of-7 authority approvals")
res = requests.get(f"{API_BASE}/api/access/authorities")
authorities = res.json() if res.status_code == 200 else []
auth_addrs = [a.get('address') if isinstance(a, dict) else a for a in authorities]

res = requests.post(f"{API_BASE}/api/access/simulate-approvals", json={
    "key_id": key_id,
    "authority_addresses": auth_addrs[:4]
})

if res.status_code == 200:
    print("   Approvals simulated")
else:
    print(f"   Simulation failed: {res.text}")

# Alice downloads
print(f"\n4) Alice downloads file {file_id}")
res = requests.get(f"{API_BASE}/files/download/{file_id}", params={
    "username": "alice",
    "key_id": key_id
})

if res.status_code == 200:
    print("   File downloaded successfully")
    print(f"   Content: {res.content.decode()}")
else:
    print(f"   Download failed: {res.text}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
