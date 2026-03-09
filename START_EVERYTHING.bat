@echo off
REM Secure Data Sharing - Startup instructions for Windows
REM Open 4 Command Prompts and paste these commands

cls
echo.
echo ====================================================================
echo  SECURE DATA SHARING - STARTUP INSTRUCTIONS FOR WINDOWS
echo ====================================================================
echo.
echo Open 4 separate Command Prompts (cmd.exe) and copy-paste these:
echo.
echo ====================================================================
echo  COMMAND PROMPT 1: Start Ganache (Blockchain)
echo ====================================================================
echo.
echo ganache-cli --accounts 7 --deterministic --host 127.0.0.1 --port 7545
echo.
echo.
echo ====================================================================
echo  COMMAND PROMPT 2: Start Python Backend (FastAPI)
echo ====================================================================
echo.
echo cd /d "%cd%"
echo python -m pip install -r backend\requirements.txt
echo python scripts\deploy_contract_compiled.py
echo python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
echo.
echo.
echo ====================================================================
echo  COMMAND PROMPT 3: Start React Frontend
echo ====================================================================
echo.
echo cd frontend
echo npm install
echo npm start
echo.
echo.
echo ====================================================================
echo  BROWSER: Deploy Smart Contract
echo ====================================================================
echo.
echo 1. Go to: https://remix.ethereum.org
echo 2. Create file: KeyAuthority.sol
echo 3. Copy from: %cd%\contracts\KeyAuthority.sol
echo 4. Set compiler to: 0.8.20
echo 5. GAS LIMIT: 10000000
echo 6. Deploy with constructor parameters:
echo    - Authorities: [use the FIRST 7 Ganache accounts shown in your Ganache UI]
echo    - Threshold: 4
echo 7. Copy contract address to: backend\blockchain\DEPLOYMENT_INFO.json
echo.
echo.
echo ====================================================================
echo  CHECK IF EVERYTHING IS RUNNING
echo ====================================================================
echo.
echo Ganache:  http://127.0.0.1:7545 (should respond with JSON)
echo Backend:  http://localhost:8000 (API running)
echo Frontend: http://localhost:3000 (React app)
echo API Docs: http://localhost:8000/docs (Swagger UI)
echo.
echo.
echo ====================================================================
echo  METAMASK SETUP
echo ====================================================================
echo.
echo 1. Install MetaMask extension (Chrome Web Store)
echo 2. Add custom network:
echo    - Name: Ganache
echo    - RPC URL: http://127.0.0.1:7545
echo    - Chain ID: 1337
echo    - Currency: ETH
echo 3. Import account from Ganache private key
echo 4. Should show 100 ETH balance
echo.
echo.
echo ====================================================================
echo  TEST THE SYSTEM
echo ====================================================================
echo.
echo 1. Open http://localhost:3000
echo 2. Login with demo admin:
echo    - Username: admin
echo    - Password: admin123
echo 3. Upload a file and set an access policy
echo 4. Go to /access and request key approval
echo 5. Simulate 4 approvals (threshold)
echo 6. Go to /download and decrypt/download
echo.
echo.
echo ====================================================================
echo  QUICK API TESTS (Using PowerShell or cURL)
echo ====================================================================
echo.
echo Check Blockchain:
echo curl -X POST http://localhost:8000/api/access/blockchain/status
echo.
echo Get Authorities:
echo curl http://localhost:8000/api/access/authorities
echo.
echo Request Approval:
echo curl -X POST http://localhost:8000/api/access/request-key-approval -H "Content-Type: application/json" -d "{\"file_id\":\"test\",\"user_id\":\"alice\",\"user_attributes\":{\"role\":\"admin\",\"department\":\"IT\",\"clearance\":\"top-secret\"}}"
echo.
echo.
echo ====================================================================
echo  DOCUMENTATION (READ IN THIS ORDER)
echo ====================================================================
echo.
echo 1. START_HERE.md (fast demo runbook)
echo 2. docs\root-guides\QUICK_REFERENCE.md (5-minute overview)
echo 3. docs\root-guides\TESTING_GUIDE.md (test + flows)
echo 4. http://localhost:8000/docs (API docs when running)
echo.
echo.
echo ====================================================================
echo  TROUBLESHOOTING
echo ====================================================================
echo.
echo Port already in use?
echo   - Use different port: ganache-cli --port 7546
echo.
echo ModuleNotFoundError?
echo   - pip install charm-crypto web3 eth-account
echo.
echo MetaMask not connecting?
echo   - Check Ganache RPC: http://127.0.0.1:7545
echo   - Make sure you're on Ganache network
echo   - Unlock MetaMask
echo.
echo Contract deployment fails?
echo   - Increase GAS_LIMIT to 10000000 in Remix
echo   - Make sure Ganache is running
echo   - Click "force sending" if gas estimation fails
echo.
echo Can't import DecentralizedAccess?
echo   - Check file exists: frontend\src\pages\DecentralizedAccess.js
echo.
echo.
echo ====================================================================
echo  KILL PROCESSES (if needed)
echo ====================================================================
echo.
echo Kill Ganache (port 7545):
echo   netstat -ano ^| findstr :7545
echo   taskkill /PID [PID] /F
echo.
echo Kill Backend (port 8000):
echo   netstat -ano ^| findstr :8000
echo   taskkill /PID [PID] /F
echo.
echo Kill Frontend (port 3000):
echo   netstat -ano ^| findstr :3000
echo   taskkill /PID [PID] /F
echo.
echo.
echo ====================================================================
echo  FEATURES
echo ====================================================================
echo.
echo - Decentralized access control
echo - Attribute-based encryption
echo - 4-of-7 threshold blockchain authentication
echo - MetaMask integration
echo - Smart contracts on Ganache
echo - React frontend + FastAPI backend
echo - REST API + docs
echo.
echo Ready to:
echo - Test and demonstrate
echo - Submit for evaluation
echo - Deploy to production
echo - Scale to Ethereum mainnet
echo.
echo ====================================================================
echo  SECURE DATA SHARING SYSTEM - READY
echo ====================================================================
echo.

pause
