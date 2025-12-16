"""
Utility functions for x402 SDK
"""

import base64
import re
from typing import Optional, Union


def usdc_to_atomic(amount: Union[str, float, int]) -> int:
    """
    Convert USDC amount to atomic units (6 decimals).
    
    Args:
        amount: USDC amount (e.g., 1.50 for $1.50)
    
    Returns:
        Atomic units as integer (e.g., 1500000)
    
    Example:
        >>> usdc_to_atomic(1.50)
        1500000
    """
    if isinstance(amount, str):
        # Remove $ and commas
        cleaned = amount.replace("$", "").replace(",", "")
        num = float(cleaned)
    else:
        num = float(amount)
    
    return int(round(num * 1_000_000))


def atomic_to_usdc(atomic: Union[str, int]) -> float:
    """
    Convert atomic units to USDC amount.
    
    Args:
        atomic: Atomic units (e.g., 1500000)
    
    Returns:
        USDC amount as float (e.g., 1.5)
    
    Example:
        >>> atomic_to_usdc(1500000)
        1.5
    """
    if isinstance(atomic, str):
        num = int(atomic)
    else:
        num = atomic
    
    return num / 1_000_000


def format_usdc(amount: Union[str, float, int], decimals: int = 2) -> str:
    """
    Format amount as USDC string.
    
    Args:
        amount: USDC amount
        decimals: Number of decimal places
    
    Returns:
        Formatted string (e.g., "$1.50 USDC")
    
    Example:
        >>> format_usdc(1.5)
        "$1.50 USDC"
    """
    if isinstance(amount, str):
        num = float(amount)
    else:
        num = float(amount)
    
    return f"${num:.{decimals}f} USDC"


def is_valid_pubkey(key: str) -> bool:
    """
    Check if string is a valid Solana public key (base58).
    
    Args:
        key: String to validate
    
    Returns:
        True if valid base58 public key
    
    Example:
        >>> is_valid_pubkey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        True
    """
    if not isinstance(key, str):
        return False
    
    if len(key) < 32 or len(key) > 44:
        return False
    
    # Base58 alphabet (no 0, O, I, l)
    base58_pattern = re.compile(r'^[1-9A-HJ-NP-Za-km-z]+$')
    return bool(base58_pattern.match(key))


def is_valid_signature(sig: str) -> bool:
    """
    Check if string is a valid Solana transaction signature.
    
    Args:
        sig: Signature string
    
    Returns:
        True if valid signature format
    """
    if not isinstance(sig, str):
        return False
    
    if len(sig) < 87 or len(sig) > 88:
        return False
    
    base58_pattern = re.compile(r'^[1-9A-HJ-NP-Za-km-z]+$')
    return bool(base58_pattern.match(sig))


def encode_base64(data: bytes) -> str:
    """
    Encode bytes to base64 string.
    
    Args:
        data: Bytes to encode
    
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(data).decode("utf-8")


def decode_base64(b64_string: str) -> bytes:
    """
    Decode base64 string to bytes.
    
    Args:
        b64_string: Base64 encoded string
    
    Returns:
        Decoded bytes
    """
    return base64.b64decode(b64_string)


def encode_hex(data: bytes) -> str:
    """
    Encode bytes to hex string.
    
    Args:
        data: Bytes to encode
    
    Returns:
        Hex encoded string
    """
    return data.hex()


def decode_hex(hex_string: str) -> bytes:
    """
    Decode hex string to bytes.
    
    Args:
        hex_string: Hex encoded string
    
    Returns:
        Decoded bytes
    """
    return bytes.fromhex(hex_string)


def parse_payment_header(header: str) -> Optional[dict]:
    """
    Parse X-PAYMENT header string.
    
    Args:
        header: Payment header value
    
    Returns:
        Dict with amount and currency, or None if invalid
    
    Example:
        >>> parse_payment_header("amount=1.50,currency=USDC")
        {"amount": 1.5, "currency": "USDC"}
    """
    try:
        parts = header.split(",")
        result = {}
        
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                if key == "amount":
                    result["amount"] = float(value)
                elif key == "currency":
                    result["currency"] = value
        
        if "amount" in result and "currency" in result:
            return result
        return None
    except Exception:
        return None


def create_payment_header(amount: float, currency: str = "USDC") -> str:
    """
    Create X-PAYMENT header string.
    
    Args:
        amount: Payment amount
        currency: Currency code
    
    Returns:
        Header value string
    
    Example:
        >>> create_payment_header(1.50)
        "amount=1.5,currency=USDC"
    """
    return f"amount={amount},currency={currency}"


def shorten_address(address: str, chars: int = 4) -> str:
    """
    Shorten a Solana address for display.
    
    Args:
        address: Full address
        chars: Number of chars at start/end
    
    Returns:
        Shortened address (e.g., "EPjF...Dt1v")
    
    Example:
        >>> shorten_address("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        "EPjF...Dt1v"
    """
    if len(address) <= chars * 2 + 3:
        return address
    return f"{address[:chars]}...{address[-chars:]}"


def get_explorer_url(
    signature: str,
    network: str = "mainnet-beta"
) -> str:
    """
    Get Solana Explorer URL for a transaction.
    
    Args:
        signature: Transaction signature
        network: Solana network
    
    Returns:
        Explorer URL
    """
    cluster = "" if network == "mainnet-beta" else f"?cluster={network}"
    return f"https://explorer.solana.com/tx/{signature}{cluster}"
