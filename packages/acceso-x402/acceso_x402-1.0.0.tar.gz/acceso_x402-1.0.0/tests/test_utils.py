"""
Tests for x402 SDK utilities
"""

import pytest
from acceso_x402.utils import (
    usdc_to_atomic,
    atomic_to_usdc,
    format_usdc,
    is_valid_pubkey,
    is_valid_signature,
    encode_base64,
    decode_base64,
    parse_payment_header,
    create_payment_header,
    shorten_address,
)


class TestAmountConversions:
    def test_usdc_to_atomic_float(self):
        assert usdc_to_atomic(1.50) == 1500000
        assert usdc_to_atomic(0.01) == 10000
        assert usdc_to_atomic(100) == 100000000
    
    def test_usdc_to_atomic_string(self):
        assert usdc_to_atomic("1.50") == 1500000
        assert usdc_to_atomic("$1.50") == 1500000
        assert usdc_to_atomic("1,000.00") == 1000000000
    
    def test_atomic_to_usdc(self):
        assert atomic_to_usdc(1500000) == 1.5
        assert atomic_to_usdc("1500000") == 1.5
        assert atomic_to_usdc(10000) == 0.01
    
    def test_format_usdc(self):
        assert format_usdc(1.5) == "$1.50 USDC"
        assert format_usdc(1.5, decimals=4) == "$1.5000 USDC"
        assert format_usdc("1.5") == "$1.50 USDC"


class TestValidation:
    def test_is_valid_pubkey_valid(self):
        valid = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        assert is_valid_pubkey(valid) is True
    
    def test_is_valid_pubkey_invalid(self):
        assert is_valid_pubkey("invalid") is False
        assert is_valid_pubkey("") is False
        assert is_valid_pubkey("0OIl") is False  # Invalid base58 chars
        assert is_valid_pubkey(123) is False
    
    def test_is_valid_signature(self):
        # Valid signature length is 87-88 chars
        valid_sig = "5" * 88
        short_sig = "5" * 50
        
        assert is_valid_signature(short_sig) is False


class TestBase64:
    def test_encode_decode(self):
        data = b"Hello, Solana!"
        encoded = encode_base64(data)
        decoded = decode_base64(encoded)
        assert decoded == data
    
    def test_encode_empty(self):
        assert encode_base64(b"") == ""


class TestPaymentHeader:
    def test_parse_payment_header(self):
        header = "amount=1.5,currency=USDC"
        result = parse_payment_header(header)
        assert result == {"amount": 1.5, "currency": "USDC"}
    
    def test_parse_payment_header_invalid(self):
        assert parse_payment_header("invalid") is None
        assert parse_payment_header("") is None
    
    def test_create_payment_header(self):
        header = create_payment_header(1.5, "USDC")
        assert header == "amount=1.5,currency=USDC"


class TestFormatting:
    def test_shorten_address(self):
        addr = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        assert shorten_address(addr) == "EPjF...Dt1v"
        assert shorten_address(addr, chars=6) == "EPjFWd...yTDt1v"
    
    def test_shorten_address_short(self):
        short = "ABC"
        assert shorten_address(short) == "ABC"
