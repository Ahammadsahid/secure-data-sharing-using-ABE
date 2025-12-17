// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract KeyAuthority {

    address public owner;
    uint public threshold;

    mapping(address => bool) public authorities;
    mapping(bytes32 => uint) public approvals;
    mapping(bytes32 => mapping(address => bool)) public approvedBy;

    constructor(uint _threshold) {
        owner = msg.sender;
        threshold = _threshold;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner allowed");
        _;
    }

    modifier onlyAuthority() {
        require(authorities[msg.sender], "Not an authority");
        _;
    }

    function registerAuthority(address authority) public onlyOwner {
        authorities[authority] = true;
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
