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
