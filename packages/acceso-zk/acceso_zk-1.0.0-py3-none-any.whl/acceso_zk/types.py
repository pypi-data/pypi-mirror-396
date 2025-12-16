"""
Type definitions for ZK SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ZkConfig:
    """Configuration for ZK client"""
    api_key: str
    api_url: str = "https://api.acceso.dev"
    timeout: int = 60
    debug: bool = False


@dataclass
class Groth16Proof:
    """A Groth16 zero-knowledge proof"""
    pi_a: List[str]
    pi_b: List[List[str]]
    pi_c: List[str]
    protocol: str = "groth16"
    curve: str = "bn128"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Groth16Proof":
        return cls(
            pi_a=data.get("pi_a", []),
            pi_b=data.get("pi_b", []),
            pi_c=data.get("pi_c", []),
            protocol=data.get("protocol", "groth16"),
            curve=data.get("curve", "bn128"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pi_a": self.pi_a,
            "pi_b": self.pi_b,
            "pi_c": self.pi_c,
            "protocol": self.protocol,
            "curve": self.curve,
        }


@dataclass
class BalanceProofResponse:
    """Response from balance proof generation"""
    proof: Groth16Proof
    public_signals: List[str]
    verification_info: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceProofResponse":
        return cls(
            proof=Groth16Proof.from_dict(data.get("proof", {})),
            public_signals=data.get("public_signals", data.get("publicSignals", [])),
            verification_info=data.get("verification_info", data.get("verificationInfo", "")),
        )


@dataclass
class ThresholdProofResponse:
    """Response from threshold proof generation"""
    proof: Groth16Proof
    public_signals: List[str]
    verification_info: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThresholdProofResponse":
        return cls(
            proof=Groth16Proof.from_dict(data.get("proof", {})),
            public_signals=data.get("public_signals", data.get("publicSignals", [])),
            verification_info=data.get("verification_info", data.get("verificationInfo", "")),
        )


@dataclass
class HolderProofResponse:
    """Response from holder proof generation"""
    proof: Groth16Proof
    public_signals: List[str]
    verification_info: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HolderProofResponse":
        return cls(
            proof=Groth16Proof.from_dict(data.get("proof", {})),
            public_signals=data.get("public_signals", data.get("publicSignals", [])),
            verification_info=data.get("verification_info", data.get("verificationInfo", "")),
        )


@dataclass
class HashTokenResponse:
    """Response from token hashing"""
    token_hash: str
    token_address: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HashTokenResponse":
        return cls(
            token_hash=data.get("token_hash", data.get("tokenHash", "")),
            token_address=data.get("token_address", data.get("tokenAddress", "")),
        )


@dataclass
class VerifyResponse:
    """Response from proof verification"""
    valid: bool
    circuit_id: str
    verified_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VerifyResponse":
        return cls(
            valid=data.get("valid", False),
            circuit_id=data.get("circuit_id", data.get("circuitId", "")),
            verified_at=data.get("verified_at", data.get("verifiedAt")),
        )


@dataclass
class CalldataResponse:
    """Response from calldata generation"""
    calldata: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalldataResponse":
        return cls(calldata=data.get("calldata", ""))


@dataclass
class Circuit:
    """A ZK circuit definition"""
    id: str
    name: str
    description: str
    constraints: int
    proving_time_estimate: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Circuit":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            constraints=data.get("constraints", 0),
            proving_time_estimate=data.get("proving_time_estimate", data.get("provingTimeEstimate", "")),
        )


# Circuit IDs
CIRCUIT_BALANCE = "balance"
CIRCUIT_THRESHOLD = "threshold"
CIRCUIT_HOLDER = "holder"
