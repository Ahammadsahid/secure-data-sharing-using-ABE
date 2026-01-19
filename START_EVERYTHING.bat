@echo off
REM 🚀 Secure Data Sharing - Complete Startup for Windows
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
echo cd backend
echo pip install -r requirements.txt
echo python -m uvicorn main:app --reload --port 8000
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
echo 2. Click "Register"
echo 3. Create user:
echo    - Username: alice
echo    - Password: test123
echo    - Role: admin
echo    - Department: IT
echo    - Clearance: top-secret
echo 4. Login and upload a file
echo 5. Set ABE Policy: role:admin AND department:IT
echo 6. Click navbar item to go to /access
echo 7. Request key approval
echo 8. Simulate 4 approvals
echo 9. Click Decrypt File
echo 10. Download decrypted content
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
echo 1. QUICK_REFERENCE.md (5-minute overview)
echo 2. COMPLETE_IMPLEMENTATION_GUIDE.md (full guide)
echo 3. PROJECT_COMPLETION_SUMMARY.md (what's implemented)
echo 4. VS_CODE_SETUP_GUIDE.md (VS Code tips)
echo 5. http://localhost:8000/docs (API docs when running)
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
echo  YOUR SYSTEM INCLUDES
echo ====================================================================
echo.
echo ✅ Decentralized access control
echo ✅ Attribute-based encryption
echo ✅ 4-of-7 threshold blockchain authentication
echo ✅ MetaMask integration
echo ✅ Smart contracts on Ganache
echo ✅ Professional frontend UI
echo ✅ Complete REST API
echo ✅ Comprehensive documentation
echo.
echo Ready to:
echo - Test and demonstrate
echo - Submit for evaluation
echo - Deploy to production
echo - Scale to Ethereum mainnet
echo.
echo ====================================================================
echo  🚀 SECURE DATA SHARING SYSTEM - READY TO LAUNCH!
echo ====================================================================
echo.

pause
