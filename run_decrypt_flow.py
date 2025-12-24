import requests
import os

API_BASE = "http://127.0.0.1:8000"
FILE_ID = "6"  # change if needed
USERNAME = "manager"  # who requests decryption
USER_ATTRIBUTES = {"role":"admin","department":"IT","clearance":"high"}

print(f"Requesting approval for file {FILE_ID} as {USERNAME}...")
res = requests.post(f"{API_BASE}/api/access/request-key-approval", json={
    "file_id": FILE_ID,
    "user_id": USERNAME,
    "user_attributes": USER_ATTRIBUTES
})
res.raise_for_status()
key_id = res.json().get('key_id')
print("Key ID:", key_id)

print("Fetching authorities list...")
res = requests.get(f"{API_BASE}/api/access/authorities")
res.raise_for_status()
auth_list = res.json().get('authorities', [])
addrs = [a['address'] if isinstance(a, dict) else a for a in auth_list]
print(f"Authorities ({len(addrs)}):", addrs)

# Simulate approvals from first 4 authorities
to_approve = addrs[:4]
print("Simulating approvals from:", to_approve)
res = requests.post(f"{API_BASE}/api/access/simulate-approvals", json={
    "key_id": key_id,
    "authority_addresses": to_approve
})
res.raise_for_status()
print("Simulate approvals result:", res.json())

# Call decrypt endpoint to get decrypted file
print("Calling decrypt endpoint to retrieve decrypted file...")
res = requests.post(f"{API_BASE}/api/access/decrypt", json={
    "file_id": FILE_ID,
    "key_id": key_id,
    "approving_authorities": to_approve
}, stream=True)

if res.status_code == 200:
    out_dir = os.path.join(os.getcwd(), 'downloaded_decrypted')
    os.makedirs(out_dir, exist_ok=True)
    # Try to get filename from headers
    cd = res.headers.get('content-disposition','')
    fname = FILE_ID + '_decrypted'
    if 'filename=' in cd:
        fname = cd.split('filename=')[-1].strip().strip('"')
    out_path = os.path.join(out_dir, fname)
    with open(out_path, 'wb') as f:
        for chunk in res.iter_content(4096):
            if chunk:
                f.write(chunk)
    print(f"Decrypted file saved to: {out_path}")
else:
    print(f"Decrypt failed: {res.status_code} {res.text}")
    res.raise_for_status()

print('Done')
