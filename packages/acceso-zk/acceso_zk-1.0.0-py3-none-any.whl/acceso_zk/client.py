"""
ZK API Client
"""

import logging
from typing import Any, Dict, List, Optional, Union

import requests

from .types import (
    ZkConfig,
    Groth16Proof,
    BalanceProofResponse,
    ThresholdProofResponse,
    HolderProofResponse,
    HashTokenResponse,
    VerifyResponse,
    CalldataResponse,
    Circuit,
)


class ZkError(Exception):
    """Exception raised for ZK API errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class ZkClient:
    """
    Client for Zero-Knowledge Proofs via Acceso API.
    
    Supports generating and verifying Groth16 proofs for:
    - Balance proofs (prove balance >= threshold)
    - Threshold proofs (prove value >= threshold)
    - Holder proofs (prove token ownership)
    
    Example:
        >>> from acceso_zk import ZkClient, ZkConfig
        >>> 
        >>> client = ZkClient(ZkConfig(api_key="your_key"))
        >>> 
        >>> # Prove balance >= 1 SOL without revealing actual balance
        >>> proof = client.prove_balance(5_000_000_000, 1_000_000_000)
        >>> print(f"Valid: {proof.public_signals[0] == '1'}")
    """
    
    def __init__(self, config: Union[ZkConfig, Dict[str, Any]]):
        if isinstance(config, dict):
            config = ZkConfig(**config)
        
        self.config = config
        self.api_url = config.api_url.rstrip("/")
        self.timeout = config.timeout
        self.debug = config.debug
        
        self.logger = logging.getLogger("acceso_zk")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
        })
    
    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
    ) -> Any:
        url = f"{self.api_url}{path}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                timeout=self.timeout,
            )
            
            data = response.json()
            
            if not response.ok:
                raise ZkError(
                    data.get("error", f"HTTP {response.status_code}"),
                    status=response.status_code,
                )
            
            return data.get("data", data)
            
        except requests.Timeout:
            raise ZkError("Request timeout", code="TIMEOUT")
        except requests.RequestException as e:
            raise ZkError(f"Network error: {e}", code="NETWORK_ERROR")
    
    # ========================================
    # Circuits
    # ========================================
    
    def get_circuits(self) -> List[Circuit]:
        """Get available ZK circuits."""
        data = self._request("GET", "/v1/zk/circuits")
        return [Circuit.from_dict(c) for c in data]
    
    # ========================================
    # Balance Proofs
    # ========================================
    
    def prove_balance(
        self,
        balance: int,
        threshold: int,
    ) -> BalanceProofResponse:
        """
        Generate a balance proof.
        
        Proves that balance >= threshold without revealing the actual balance.
        
        Args:
            balance: Actual balance (private - never sent to server)
            threshold: Minimum balance to prove
        
        Returns:
            BalanceProofResponse with proof and public signals
        
        Example:
            >>> # Prove you have at least 1 SOL
            >>> proof = client.prove_balance(5_000_000_000, 1_000_000_000)
            >>> print(proof.public_signals)  # ["1", "1000000000"]
        """
        data = self._request("POST", "/v1/zk/balance-proof", {
            "balance": str(balance),
            "threshold": str(threshold),
        })
        return BalanceProofResponse.from_dict(data)
    
    # ========================================
    # Threshold Proofs
    # ========================================
    
    def prove_threshold(
        self,
        value: int,
        threshold: int,
    ) -> ThresholdProofResponse:
        """
        Generate a threshold proof.
        
        Proves that value >= threshold for any numeric value.
        
        Args:
            value: Actual value (private)
            threshold: Minimum value to prove
        
        Returns:
            ThresholdProofResponse
        
        Example:
            >>> # Prove age >= 18
            >>> proof = client.prove_threshold(25, 18)
        """
        data = self._request("POST", "/v1/zk/threshold-proof", {
            "value": str(value),
            "threshold": str(threshold),
        })
        return ThresholdProofResponse.from_dict(data)
    
    # ========================================
    # Holder Proofs
    # ========================================
    
    def hash_token(self, token_address: str) -> HashTokenResponse:
        """
        Hash a token address for holder proofs.
        
        Args:
            token_address: Token mint address
        
        Returns:
            HashTokenResponse with Poseidon hash
        """
        data = self._request("POST", "/v1/zk/hash-token", {
            "token_address": token_address,
        })
        return HashTokenResponse.from_dict(data)
    
    def prove_holder(
        self,
        balance: int,
        token_address: str,
        token_hash: str,
    ) -> HolderProofResponse:
        """
        Generate a holder proof.
        
        Proves ownership of a specific token without revealing balance.
        
        Args:
            balance: Token balance (private)
            token_address: Token mint address
            token_hash: Hash from hash_token()
        
        Returns:
            HolderProofResponse
        
        Example:
            >>> hash_resp = client.hash_token("USDC_MINT")
            >>> proof = client.prove_holder(1_000_000, "USDC_MINT", hash_resp.token_hash)
        """
        data = self._request("POST", "/v1/zk/holder-proof", {
            "balance": str(balance),
            "token_address": token_address,
            "token_hash": token_hash,
        })
        return HolderProofResponse.from_dict(data)
    
    # ========================================
    # Verification
    # ========================================
    
    def verify(
        self,
        circuit_id: str,
        proof: Union[Groth16Proof, Dict[str, Any]],
        public_signals: List[str],
    ) -> bool:
        """
        Verify a ZK proof.
        
        Args:
            circuit_id: Circuit ID ("balance", "threshold", "holder")
            proof: Groth16 proof
            public_signals: Public signals from proof
        
        Returns:
            True if valid, False otherwise
        """
        result = self.verify_full(circuit_id, proof, public_signals)
        return result.valid
    
    def verify_full(
        self,
        circuit_id: str,
        proof: Union[Groth16Proof, Dict[str, Any]],
        public_signals: List[str],
    ) -> VerifyResponse:
        """
        Verify a ZK proof with full response.
        
        Returns:
            VerifyResponse with validity and metadata
        """
        if isinstance(proof, Groth16Proof):
            proof_dict = proof.to_dict()
        else:
            proof_dict = proof
        
        data = self._request("POST", "/v1/zk/proofs/verify", {
            "circuit_id": circuit_id,
            "proof": proof_dict,
            "public_signals": public_signals,
        })
        return VerifyResponse.from_dict(data)
    
    # ========================================
    # Calldata
    # ========================================
    
    def to_calldata(
        self,
        proof: Union[Groth16Proof, Dict[str, Any]],
        public_signals: List[str],
    ) -> str:
        """
        Convert proof to Solidity calldata.
        
        Args:
            proof: Groth16 proof
            public_signals: Public signals
        
        Returns:
            Hex-encoded calldata for smart contract
        """
        if isinstance(proof, Groth16Proof):
            proof_dict = proof.to_dict()
        else:
            proof_dict = proof
        
        data = self._request("POST", "/v1/zk/to-calldata", {
            "proof": proof_dict,
            "public_signals": public_signals,
        })
        return CalldataResponse.from_dict(data).calldata
    
    # ========================================
    # Convenience Methods
    # ========================================
    
    def prove_and_verify_balance(
        self,
        balance: int,
        threshold: int,
    ) -> tuple:
        """
        Prove and verify balance in one call.
        
        Returns:
            Tuple of (BalanceProofResponse, is_valid)
        """
        proof_resp = self.prove_balance(balance, threshold)
        is_valid = self.verify("balance", proof_resp.proof, proof_resp.public_signals)
        return proof_resp, is_valid
    
    def prove_and_verify_threshold(
        self,
        value: int,
        threshold: int,
    ) -> tuple:
        """
        Prove and verify threshold in one call.
        
        Returns:
            Tuple of (ThresholdProofResponse, is_valid)
        """
        proof_resp = self.prove_threshold(value, threshold)
        is_valid = self.verify("threshold", proof_resp.proof, proof_resp.public_signals)
        return proof_resp, is_valid
    
    def close(self) -> None:
        """Close the client session."""
        self._session.close()
    
    def __enter__(self) -> "ZkClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
