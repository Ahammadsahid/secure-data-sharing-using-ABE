# KeyAuthority Smart Contract - Deployment Guide

## Error: Internal JSON-RPC Error (Gas Issues)

### **Quick Fix in Remix:**

#### Step 1: Set Gas Limit
1. In Remix, click on the "Deploy & Run Transactions" tab (bottom left)
2. Look for "GAS LIMIT" field
3. Change it from default (~3,000,000) to **8,000,000**
4. Look for "GAS PRICE" - Ganache default is **2 gwei** ✓

#### Step 2: Enter Constructor Parameters
1. Find the input field that says "address[]" (authorities)
2. Copy-paste this array in JSON format:
```json
["0x5B38Da6a701c568545dCfcB03FcB875f56beddC4","0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2","0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db","0x78731D3Ca6b7E34aC0F824c42a7cC18A495cabaB","0x617F2E2fD72FD9D5503197092aC168c91465E7f2","0x17F6AD8Ef982297579C203069C1DbfFE4348c372","0x5c6B0f7Bf3E7ce046039Bd8FABdfD3f9F5021678"]
```

3. For "uint" (threshold), enter: **4**

#### Step 3: Deploy
1. Click the orange "Deploy" button
2. Wait for confirmation in Ganache terminal
3. Should see "creation of KeyAuthority" ✓

---

## Verification Checklist

- [ ] Ganache running on `127.0.0.1:7545`
- [ ] MetaMask connected to Ganache network
- [ ] Remix shows correct Solidity version (0.8.20)
- [ ] Gas Limit set to 8,000,000
- [ ] Constructor params provided (authorities array + threshold = 4)
- [ ] Account has sufficient ETH balance (Ganache gives 100 ETH by default)

---

## Alternative: Using Hardhat Script

If you have Hardhat/Node.js set up:

```bash
npx hardhat run scripts/deploy.js --network ganache
```

This handles all parameters automatically.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Not enough gas" | Increase GAS LIMIT to 8,000,000+ |
| "Invalid parameters" | Ensure authorities is a proper JSON array |
| "Network error" | Check Ganache is running and MetaMask RPC is correct |
| "Account locked" | Unlock MetaMask account |

