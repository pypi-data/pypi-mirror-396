"""
Type definitions for x402 SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class X402Config:
    """Configuration for X402 client"""
    api_key: str
    api_url: str = "https://api.acceso.dev"
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    timeout: int = 30
    debug: bool = False


@dataclass
class PaymentRequirements:
    """Payment requirements from 402 response"""
    scheme: str
    network: str
    asset: str
    max_amount_required: str
    pay_to: str
    resource: Optional[str] = None
    description: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentRequirements":
        return cls(
            scheme=data.get("scheme", "exact"),
            network=data.get("network", "solana-mainnet"),
            asset=data.get("asset", ""),
            max_amount_required=str(data.get("maxAmountRequired", "0")),
            pay_to=data.get("payTo", ""),
            resource=data.get("resource"),
            description=data.get("description"),
            extra=data.get("extra", {}),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scheme": self.scheme,
            "network": self.network,
            "asset": self.asset,
            "maxAmountRequired": self.max_amount_required,
            "payTo": self.pay_to,
            "resource": self.resource,
            "description": self.description,
            "extra": self.extra,
        }


@dataclass
class VerifyResponse:
    """Response from payment verification"""
    is_valid: bool
    invalid_reason: Optional[str] = None
    payer: Optional[str] = None
    amount: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VerifyResponse":
        return cls(
            is_valid=data.get("isValid", False),
            invalid_reason=data.get("invalidReason"),
            payer=data.get("payer"),
            amount=data.get("amount"),
        )


@dataclass
class SettleResponse:
    """Response from payment settlement"""
    success: bool
    tx_hash: Optional[str] = None
    error: Optional[str] = None
    block_time: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettleResponse":
        return cls(
            success=data.get("success", False),
            tx_hash=data.get("txHash"),
            error=data.get("error"),
            block_time=data.get("blockTime"),
        )


@dataclass
class HealthResponse:
    """API health check response"""
    status: str
    version: str = ""
    timestamp: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        return cls(
            status=data.get("status", "unknown"),
            version=data.get("version", ""),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class SupportedResponse:
    """Supported payment methods"""
    schemes: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SupportedResponse":
        return cls(
            schemes=data.get("schemes", []),
            networks=data.get("networks", []),
            assets=data.get("assets", []),
        )


@dataclass
class FeePayerResponse:
    """Fee payer public key response"""
    fee_payer: str
    network: str = "solana-mainnet"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeePayerResponse":
        return cls(
            fee_payer=data.get("feePayer", ""),
            network=data.get("network", "solana-mainnet"),
        )


@dataclass
class PaymentResult:
    """Result of a payment operation"""
    success: bool
    tx_hash: Optional[str] = None
    error: Optional[str] = None


# Constants
USDC_MAINNET_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_DEVNET_MINT = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
USDC_DECIMALS = 6
