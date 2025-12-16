"""
Acceso x402 Python SDK - Solana Payment Protocol

A Python SDK for the x402 HTTP payment protocol on Solana.
"""

__version__ = "1.0.0"
__author__ = "Acceso"
__email__ = "dev@acceso.dev"

from .client import X402Client, X402Error
from .types import (
    X402Config,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    HealthResponse,
    SupportedResponse,
)
from .utils import (
    usdc_to_atomic,
    atomic_to_usdc,
    format_usdc,
    is_valid_pubkey,
    encode_base64,
    decode_base64,
)

__all__ = [
    "X402Client",
    "X402Error",
    "X402Config",
    "PaymentRequirements",
    "VerifyResponse",
    "SettleResponse",
    "HealthResponse",
    "SupportedResponse",
    "usdc_to_atomic",
    "atomic_to_usdc",
    "format_usdc",
    "is_valid_pubkey",
    "encode_base64",
    "decode_base64",
]
