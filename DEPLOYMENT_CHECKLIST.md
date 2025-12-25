# REMIX DEPLOYMENT - Quick Steps

## You Need To Do (Manual Steps in Remix):

1. **Open Remix**: https://remix.ethereum.org
2. **Create File**: `KeyAuthority.sol`
3. **Paste This Code**:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KeyAuthority {
    address public owner;
    uint public threshold;
    mapping(address => bool) public authorities;
    mapping(bytes32 => uint) public approvals;
    mapping(bytes32 => mapping(address => bool)) public approvedBy;

    constructor(address[] memory _authorities, uint _threshold) {
        owner = msg.sender;
        threshold = _threshold;
        for (uint i = 0; i < _authorities.length; i++) {
            authorities[_authorities[i]] = true;
        }
    }

    modifier onlyAuthority() {
        require(authorities[msg.sender], "Not an authority");
        _;
    }

    function approveKey(bytes32 keyId) public onlyAuthority {
        require(!approvedBy[keyId][msg.sender], "Already approved");
        approvedBy[keyId][msg.sender] = true;
        approvals[keyId] += 1;
    }

    function isApproved(bytes32 keyId) public view returns (bool) {
        return approvals[keyId] >= threshold;
    }
}
```

4. **Compile**: Solidity Compiler → Set to 0.8.20 → Compile

5. **Deploy**:
   - Tab: Deploy & Run Transactions
   - Environment: **Injected Provider - MetaMask**
   - Contract: **KeyAuthority**
   - Constructor Args:
     - Authorities: `["0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48","0xfbe684383F81045249eB1E5974415f484E6F9f21","0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94","0x57D14fF746d33127a90d4B888D378487e2C69f1f","0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a","0x211Db7b2b475E9282B31Bd0fF39220805505Ff71","0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"]`
     - Threshold: `4`
   - Gas Limit: **3000000**
   - Click **Deploy** → Confirm in MetaMask

6. **Copy Address**: After deployment, copy the contract address from "Deployed Contracts"

## I Can Do (Automatic):

Once you have the address, run:
```bash
python scripts/update_deployment_address.py 0xYourAddressHere
```

I'll update the backend config automatically.

---

**⏱️ Estimated time**: 5-10 minutes
**🔧 Tools needed**: MetaMask + Ganache running

Tell me when you've deployed and I'll update the backend!
