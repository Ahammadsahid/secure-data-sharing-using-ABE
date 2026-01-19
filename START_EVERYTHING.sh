#!/bin/bash
# Secure Data Sharing - Startup commands
# Copy these commands to your VS Code terminals

# ================================================================
# TERMINAL 1: START GANACHE BLOCKCHAIN (Local Ethereum)
# ================================================================
# Copy this command to the first VS Code terminal:

ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545

# Expected output:
# - Listening on 127.0.0.1:7545
# - [List of accounts]


# ================================================================
# TERMINAL 2: START PYTHON BACKEND (FastAPI)
# ================================================================
# Copy these commands to the second VS Code terminal:

cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
# [Ready to receive API requests]


# ================================================================
# TERMINAL 3: START REACT FRONTEND
# ================================================================
# Copy these commands to the third VS Code terminal:

cd frontend
npm install
npm start

# Expected output:
# webpack compiled successfully
# Compiled successfully!
# Local:   http://localhost:3000
# [Browser opens automatically to http://localhost:3000]


# ================================================================
# OPTIONAL - TERMINAL 4: LOCAL REMIX SERVER
# ================================================================
# If you want Remix running locally (advanced):

npm install -g @remix-project/remixd
remixd -s . --port 65521

# Then go to: https://remix.ethereum.org
# Click "Connect to localhost" (bottom left)


# ================================================================
# CHECK IF EVERYTHING IS RUNNING
# ================================================================

# Ganache running?
curl http://127.0.0.1:7545

# Backend running?
curl http://localhost:8000/

# Frontend running?
curl http://localhost:3000

# API docs available?
# Open: http://localhost:8000/docs


# ================================================================
# DEPLOY SMART CONTRACT (Via Remix in Browser)
# ================================================================

# 1. Go to https://remix.ethereum.org
# 2. Create file: KeyAuthority.sol
# 3. Copy from: contracts/KeyAuthority.sol
# 4. Compile (Ctrl+S)
# 5. Go to "Deploy & Run Transactions"
# 6. Environment: "Injected Provider - MetaMask"
# 7. GAS LIMIT: 10000000
# 8. Constructor Parameters:
#    - Authorities: [use the FIRST 7 Ganache accounts shown in your Ganache UI]
#    - Threshold: 4
# 9. Click "Deploy"
# 10. Copy contract address to: backend/blockchain/DEPLOYMENT_INFO.json


# ================================================================
# METAMASK SETUP
# ================================================================

# 1. Install MetaMask extension from Chrome Web Store
# 2. Create wallet or import existing
# 3. Add custom network:
#    - Network Name: Ganache
#    - RPC URL: http://127.0.0.1:7545
#    - Chain ID: 1337
#    - Currency Symbol: ETH
# 4. Import first account from Ganache (private key from terminal 1)
# 5. Should show 100 ETH balance


# ================================================================
# TEST THE SYSTEM
# ================================================================

# Check Blockchain Connection:
curl -X POST http://localhost:8000/api/access/blockchain/status

# Get All 7 Authorities:
curl http://localhost:8000/api/access/authorities

# Frontend Flow:
# 1. http://localhost:3000
# 2. Click Register
# 3. Register new user with attributes
# 4. Click Upload
# 5. Upload file with ABE policy
# 6. Click /access (or go to http://localhost:3000/access)
# 7. Request key approval
# 8. Simulate 4 approvals
# 9. Click Decrypt File


# ================================================================
# TROUBLESHOOTING
# ================================================================

# Port already in use?
# Change Ganache port: ganache-cli --port 7546

# ModuleNotFoundError?
# pip install charm-crypto web3 eth-account

# Can't import DecentralizedAccess?
# Check: frontend/src/pages/DecentralizedAccess.js exists

# MetaMask not connecting?
# 1. Check Ganache is running
# 2. Verify RPC: http://127.0.0.1:7545
# 3. Switch to Ganache network
# 4. Unlock MetaMask

# Contract deployment fails?
# 1. Increase GAS_LIMIT to 10000000
# 2. Make sure Ganache is running
# 3. MetaMask has ETH (should have 100)
# 4. Click "force sending" if gas estimation fails


# ================================================================
# QUICK API TESTS (cURL)
# ================================================================

# Test 1: Check blockchain connection
curl -s http://localhost:8000/api/access/blockchain/status | jq .

# Test 2: Get authorities list
curl -s http://localhost:8000/api/access/authorities | jq .

# Test 3: Request key approval
curl -s -X POST http://localhost:8000/api/access/request-key-approval \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "test-file-123",
    "user_id": "alice",
    "user_attributes": {
      "role": "admin",
      "department": "IT",
      "clearance": "top-secret"
    }
  }' | jq .

# Test 4: Check approval status
# Replace KEY_ID with actual key_id from test 3
curl -s http://localhost:8000/api/access/approval-status/KEY_ID | jq .


# ================================================================
# USEFUL COMMANDS
# ================================================================

# Kill process on port 7545:
lsof -ti:7545 | xargs kill -9

# Kill process on port 8000:
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000:
lsof -ti:3000 | xargs kill -9

# View logs:
# Terminal 1 (Ganache): Shows all transactions
# Terminal 2 (Backend): Shows API requests and errors
# Terminal 3 (Frontend): Shows build output and console.log

# Clear cache and reinstall:
rm -rf node_modules && npm install

# Reset database:
rm backend/test.db


# ================================================================
# DOCUMENTATION TO READ
# ================================================================

# 1. QUICK_REFERENCE.md - 5 minute overview
# 2. COMPLETE_IMPLEMENTATION_GUIDE.md - Full guide
# 3. PROJECT_COMPLETION_SUMMARY.md - What's implemented
# 4. VS_CODE_SETUP_GUIDE.md - VS Code tips
# 5. http://localhost:8000/docs - API documentation


# ================================================================
# DONE
# ================================================================

# Features:
# - Decentralized access control
# - Attribute-based encryption
# - 4-of-7 threshold blockchain authentication
# - MetaMask integration
# - Smart contracts on Ganache
# - React frontend + FastAPI backend

echo "Secure Data Sharing System - Ready"
