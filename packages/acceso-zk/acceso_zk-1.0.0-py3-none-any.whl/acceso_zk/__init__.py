"""
Acceso ZK Python SDK - Zero-Knowledge Proofs

A Python SDK for generating and verifying ZK proofs via Acceso API.
"""

__version__ = "1.0.0"
__author__ = "Acceso"
__email__ = "dev@acceso.dev"

from .client import ZkClient, ZkError
from .types import (
    ZkConfig,
    Groth16Proof,
    BalanceProofResponse,
    ThresholdProofResponse,
    HolderProofResponse,
    VerifyResponse,
    Circuit,
)

__all__ = [
    "ZkClient",
    "ZkError",
    "ZkConfig",
    "Groth16Proof",
    "BalanceProofResponse",
    "ThresholdProofResponse",
    "HolderProofResponse",
    "VerifyResponse",
    "Circuit",
]
