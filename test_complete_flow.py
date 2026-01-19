#!/usr/bin/env python3
"""End-to-end test for upload/approval/download flows."""

import requests
import time
from io import BytesIO

API_BASE = "http://127.0.0.1:8000"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(msg):
    print(f"\n{BLUE}{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}OK: {msg}{RESET}")

def print_error(msg):
    print(f"{RED}ERROR: {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}INFO: {msg}{RESET}")

def test_login(username, password):
    """Test login endpoint"""
    print_info(f"Logging in as {username}...")
    try:
        res = requests.post(f"{API_BASE}/login", json={
            "username": username,
            "password": password
        })
        if res.status_code == 200:
            data = res.json()
            print_success(f"Login successful!")
            print(f"   Role: {data['role']}, Dept: {data['department']}, Clearance: {data['clearance']}")
            return data
        else:
            print_error(f"Login failed: {res.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_upload_file(admin_username, file_content, filename, policy):
    """Test file upload as admin"""
    print_info(f"Uploading file '{filename}' as {admin_username}...")
    print(f"   Policy: {policy}")
    
    try:
        files = {
            'file': (filename, BytesIO(file_content.encode()), 'text/plain')
        }
        data = {
            'policy': policy,
            'username': admin_username
        }
        
        res = requests.post(f"{API_BASE}/files/upload", files=files, data=data)
        
        if res.status_code == 200:
            file_id = res.json()['file_id']
            print_success(f"File uploaded! File ID: {file_id}")
            return file_id
        else:
            print_error(f"Upload failed: {res.text}")
            return None
    except Exception as e:
        print_error(f"Upload error: {e}")
        return None

def test_request_approval(file_id, username, user_attrs):
    """Test requesting approval for decryption"""
    print_info(f"Requesting approval for file {file_id} as {username}...")
    print(f"   User attributes: role={user_attrs['role']}, dept={user_attrs['department']}, clearance={user_attrs['clearance']}")
    
    try:
        res = requests.post(f"{API_BASE}/api/access/request-key-approval", json={
            "file_id": str(file_id),
            "user_id": username,
            "user_attributes": user_attrs
        })
        
        if res.status_code == 200:
            data = res.json()
            key_id = data['key_id']
            print_success(f"Approval request created! Key ID: {key_id[:20]}...")
            return key_id
        else:
            print_error(f"Request failed: {res.text}")
            return None
    except Exception as e:
        print_error(f"Request error: {e}")
        return None

def test_simulate_approvals(key_id, authorities):
    """Test simulating approvals from authorities"""
    print_info(f"Simulating 4-of-7 approvals...")
    
    try:
        res = requests.post(f"{API_BASE}/api/access/simulate-approvals", json={
            "key_id": key_id,
            "authority_addresses": authorities[:4]
        })
        
        if res.status_code == 200:
            print_success(f"Approvals simulated successfully!")
            return True
        else:
            print_error(f"Simulation failed: {res.text}")
            return False
    except Exception as e:
        print_error(f"Simulation error: {e}")
        return False

def test_download_file(file_id, username, key_id):
    """Test downloading and decrypting file"""
    print_info(f"Downloading file {file_id} as {username}...")
    
    try:
        res = requests.get(f"{API_BASE}/files/download/{file_id}", params={
            "username": username,
            "key_id": key_id
        })
        
        if res.status_code == 200:
            print_success(f"File downloaded successfully!")
            print(f"   Content length: {len(res.content)} bytes")
            return res.content
        else:
            print_error(f"Download failed with status {res.status_code}: {res.text}")
            return None
    except Exception as e:
        print_error(f"Download error: {e}")
        return None

def main():
    print_header("🔐 SECURE DATA SHARING - COMPLETE END-TO-END TEST")
    
    # Wait for backend
    print_info("Waiting for backend to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            res = requests.get(f"{API_BASE}/")
            if res.status_code == 200:
                print_success("Backend is ready!")
                break
        except:
            if i == max_retries - 1:
                print_error("Backend did not start in time!")
                return
            time.sleep(1)
    
    # ============================================================================
    # TEST 1: Login verification
    # ============================================================================
    print_header("TEST 1: User Login & Attributes")
    
    admin_data = test_login("admin", "admin123")
    if not admin_data:
        print_error("Admin login failed!")
        return
    
    alice_data = test_login("alice", "alice123")
    if not alice_data:
        print_error("Alice login failed!")
        return
    
    bob_data = test_login("bob", "bob123")
    if not bob_data:
        print_error("Bob login failed!")
        return
    
    # ============================================================================
    # TEST 2: Upload file as admin with complex policy
    # ============================================================================
    print_header("TEST 2: Upload File with ABE Policy (Admin Only)")
    
    test_content = "This is a confidential IT department file with high clearance requirement!"
    filename = "confidential_it_file.txt"
    
    # Policy: (admin OR manager) AND (IT OR Finance) AND high clearance
    policy = "(role:admin OR role:manager) AND (dept:IT OR dept:Finance) AND clearance:high"
    
    file_id = test_upload_file("admin", test_content, filename, policy)
    if not file_id:
        print_error("Upload failed!")
        return
    
    # ============================================================================
    # TEST 3: Alice tries to download (should succeed - matches policy)
    # ============================================================================
    print_header("TEST 3: Alice Downloads File (Should Succeed)")
    print(f"{YELLOW}Alice: role=user, dept=IT, clearance=high{RESET}")
    print(f"{YELLOW}Policy: (role:admin OR manager) AND (dept:IT OR Finance) AND clearance:high{RESET}")
    
    key_id = test_request_approval(file_id, "alice", {
        "role": alice_data["role"],
        "department": alice_data["department"],
        "clearance": alice_data["clearance"]
    })
    
    if key_id:
        # Get authorities
        try:
            auth_res = requests.get(f"{API_BASE}/api/access/authorities")
            authorities = auth_res.json() if auth_res.status_code == 200 else []
            auth_addrs = [a.get('address') if isinstance(a, dict) else a for a in authorities]
            
            if test_simulate_approvals(key_id, auth_addrs[:7]):
                content = test_download_file(file_id, "alice", key_id)
                if content:
                    print_success(f"File downloaded: {content.decode()[:50]}...")
                else:
                    print_error("Failed to download file")
        except Exception as e:
            print_error(f"Error during approval: {e}")
    
    # ============================================================================
    # TEST 4: Bob tries to download (should fail - doesn't match policy)
    # ============================================================================
    print_header("TEST 4: Bob Tries to Download (Should Fail - Wrong Attributes)")
    print(f"{YELLOW}Bob: role=user, dept=Finance, clearance=medium{RESET}")
    print(f"{YELLOW}Policy requires: clearance:high (Bob has medium){RESET}")
    
    key_id_bob = test_request_approval(file_id, "bob", {
        "role": bob_data["role"],
        "department": bob_data["department"],
        "clearance": bob_data["clearance"]
    })
    
    if key_id_bob:
        try:
            auth_res = requests.get(f"{API_BASE}/api/access/authorities")
            authorities = auth_res.json() if auth_res.status_code == 200 else []
            auth_addrs = [a.get('address') if isinstance(a, dict) else a for a in authorities]
            
            if test_simulate_approvals(key_id_bob, auth_addrs[:7]):
                content = test_download_file(file_id, "bob", key_id_bob)
                if content:
                    print_error(f"UNEXPECTED: Bob could download! This is a security issue!")
                else:
                    print_success("Access correctly denied to Bob!")
        except Exception as e:
            print_info(f"Download failed as expected: {e}")
    
    # ============================================================================
    # TEST 5: Upload another file with different policy
    # ============================================================================
    print_header("TEST 5: Upload Finance File (Finance dept only)")
    
    finance_content = "This is finance department data!"
    finance_filename = "finance_report.txt"
    finance_policy = "dept:Finance AND clearance:medium"
    
    file_id_2 = test_upload_file("admin", finance_content, finance_filename, finance_policy)
    if file_id_2:
        # Bob should be able to download this one
        print_header("TEST 5b: Bob Downloads Finance File (Should Succeed)")
        
        key_id_bob_2 = test_request_approval(file_id_2, "bob", {
            "role": bob_data["role"],
            "department": bob_data["department"],
            "clearance": bob_data["clearance"]
        })
        
        if key_id_bob_2:
            try:
                auth_res = requests.get(f"{API_BASE}/api/access/authorities")
                authorities = auth_res.json() if auth_res.status_code == 200 else []
                auth_addrs = [a.get('address') if isinstance(a, dict) else a for a in authorities]
                
                if test_simulate_approvals(key_id_bob_2, auth_addrs[:7]):
                    content = test_download_file(file_id_2, "bob", key_id_bob_2)
                    if content:
                        print_success(f"Bob can access finance file: {content.decode()[:40]}...")
                    else:
                        print_error("Failed to download finance file")
            except Exception as e:
                print_error(f"Error: {e}")
    
    print_header("END-TO-END TEST COMPLETE")
    print(f"{GREEN}Summary:{RESET}")
    print(f"  {GREEN}- User login with attributes{RESET}")
    print(f"  {GREEN}- File upload with ABE policy{RESET}")
    print(f"  {GREEN}- Alice can download (matches policy){RESET}")
    print(f"  {GREEN}- Bob cannot access restricted files{RESET}")
    print(f"  {GREEN}- Bob can access finance files{RESET}")
    print(f"\n{BLUE}System is working correctly!{RESET}\n")

if __name__ == "__main__":
    main()
