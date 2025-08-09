// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Stegano3DHash {
    mapping(bytes32 => bool) public hashes;

    event HashStored(bytes32 indexed fileHash, address indexed sender);

    function storeHash(bytes32 fileHash) public {
        hashes[fileHash] = true;
        emit HashStored(fileHash, msg.sender);
    }

    function verifyHash(bytes32 fileHash) public view returns (bool) {
        return hashes[fileHash];
    }
}
