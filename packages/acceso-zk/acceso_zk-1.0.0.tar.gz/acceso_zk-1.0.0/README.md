# Acceso ZK Python SDK

Python SDK for generating and verifying Zero-Knowledge Proofs via Acceso API.

## Installation

```bash
pip install acceso-zk
```

## Features

- 🔐 **Groth16 Proofs** - Industry-standard ZK proof system
- 💰 **Balance Proofs** - Prove balance >= threshold without revealing balance
- 📊 **Threshold Proofs** - Prove any value >= threshold privately
- 🪙 **Holder Proofs** - Prove token ownership without revealing amount
- ✅ **Verification** - Verify proofs on-chain or off-chain
- 📜 **Calldata** - Generate Solidity calldata for smart contracts

## Quick Start

```python
from acceso_zk import ZkClient, ZkConfig

# Initialize client
client = ZkClient(ZkConfig(api_key="your_api_key"))

# Prove you have >= 1 SOL without revealing actual balance
proof = client.prove_balance(
    balance=5_000_000_000,    # 5 SOL (private - never leaves your machine)
    threshold=1_000_000_000,  # 1 SOL (public threshold)
)

print(f"Proof generated!")
print(f"Public signals: {proof.public_signals}")

# Verify the proof
is_valid = client.verify("balance", proof.proof, proof.public_signals)
print(f"Valid: {is_valid}")
```

## Available Proofs

### Balance Proof

Prove that your balance meets a minimum threshold:

```python
# Prove you have at least 100 USDC
proof = client.prove_balance(
    balance=500_000_000,   # 500 USDC (private)
    threshold=100_000_000,  # 100 USDC (public)
)
```

### Threshold Proof

Prove any numeric value meets a threshold:

```python
# Prove age >= 18 without revealing actual age
proof = client.prove_threshold(
    value=25,      # Actual age (private)
    threshold=18,  # Minimum age (public)
)
```

### Holder Proof

Prove you hold a specific token:

```python
# Hash the token address first
token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
hash_resp = client.hash_token(token_address)

# Prove you hold the token
proof = client.prove_holder(
    balance=1_000_000,           # Your balance (private)
    token_address=token_address,
    token_hash=hash_resp.token_hash,
)
```

## Verification

```python
# Verify any proof
is_valid = client.verify(
    circuit_id="balance",  # or "threshold", "holder"
    proof=proof.proof,
    public_signals=proof.public_signals,
)

# Get full verification response
result = client.verify_full("balance", proof.proof, proof.public_signals)
print(f"Valid: {result.valid}")
print(f"Circuit: {result.circuit_id}")
print(f"Verified at: {result.verified_at}")
```

## Smart Contract Integration

Generate calldata for Solidity verifier contracts:

```python
calldata = client.to_calldata(
    proof=proof.proof,
    public_signals=proof.public_signals,
)

print(f"Calldata: {calldata}")
# Use in web3: contract.verify(calldata)
```

## Convenience Methods

```python
# Prove and verify in one call
proof, is_valid = client.prove_and_verify_balance(
    balance=5_000_000_000,
    threshold=1_000_000_000,
)

proof, is_valid = client.prove_and_verify_threshold(
    value=100,
    threshold=50,
)
```

## Available Circuits

```python
# List all circuits
circuits = client.get_circuits()
for circuit in circuits:
    print(f"{circuit.name}: {circuit.description}")
    print(f"  Constraints: {circuit.constraints}")
    print(f"  Proving time: {circuit.proving_time_estimate}")
```

## Context Manager

```python
with ZkClient(ZkConfig(api_key="your_key")) as client:
    proof = client.prove_balance(5_000_000_000, 1_000_000_000)
    is_valid = client.verify("balance", proof.proof, proof.public_signals)
# Session automatically closed
```

## Error Handling

```python
from acceso_zk import ZkClient, ZkError

try:
    proof = client.prove_balance(balance, threshold)
except ZkError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status}")
```

## Types

```python
from acceso_zk import (
    ZkConfig,
    Groth16Proof,
    BalanceProofResponse,
    ThresholdProofResponse,
    HolderProofResponse,
    VerifyResponse,
    Circuit,
)
```

## Use Cases

- **KYC/AML**: Prove you meet financial thresholds without revealing exact balances
- **Age Verification**: Prove you're over 18/21 without revealing birthday
- **Credit Checks**: Prove creditworthiness without exposing financial details
- **Token Gating**: Prove token ownership for exclusive access
- **Private Voting**: Prove eligibility without revealing identity
- **Compliance**: Prove regulatory compliance privately

## License

MIT
