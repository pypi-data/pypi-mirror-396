# Acceso x402 Python SDK

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Solana](https://img.shields.io/badge/Solana-9945FF?style=for-the-badge&logo=solana&logoColor=white)
![USDC](https://img.shields.io/badge/USDC-2775CA?style=for-the-badge&logo=circle&logoColor=white)
![PyPI](https://img.shields.io/badge/PyPI-3775A9?style=for-the-badge&logo=pypi&logoColor=white)

**HTTP Payment Protocol for Solana**

[Documentation](https://docs.acceso.dev) • [API Reference](https://api.acceso.dev/docs) • [Get API Key](https://acceso.dev)

</div>

---

## 🚀 Overview

The **Acceso x402 Python SDK** implements the x402 HTTP payment protocol for Solana. Enable pay-per-request API monetization using USDC payments.

### Key Features

- 💳 **Pay-per-Request** - Monetize APIs with micropayments
- ⚡ **Fast Settlements** - Sub-second Solana transactions
- 🔐 **Secure** - Cryptographic payment verification
- 🐍 **Pythonic** - Clean, typed API with dataclasses
- 📦 **Minimal Dependencies** - Just `requests`

---

## 📦 Installation

```bash
pip install acceso-x402
```

---

## ⚡ Quick Start

```python
from acceso_x402 import X402Client, X402Config

# Initialize client
config = X402Config(api_key="your_api_key")
client = X402Client(config)

# Generate payment requirements
requirements = client.generate_requirements(
    price="0.01",  # $0.01 USDC
    pay_to="recipient_wallet_address",
    resource="/api/premium-data",
    description="Premium API access"
)

print(f"Price: {requirements.max_amount_required} atomic units")
print(f"Pay to: {requirements.pay_to}")
```

---

## 📖 API Reference

### X402Client

Main client for x402 payment operations.

```python
from acceso_x402 import X402Client, X402Config

config = X402Config(
    api_key="your_api_key",
    api_url="https://api.acceso.dev",  # Default
    timeout=30,  # Seconds
    debug=False,
)

client = X402Client(config)
```

---

### Generate Requirements

Create payment requirements for a protected resource:

```python
requirements = client.generate_requirements(
    price="0.01",
    pay_to="recipient_wallet",
    resource="/api/data",
    description="API access fee",
    timeout_seconds=300,  # 5 minutes validity
)

print(requirements.scheme)              # "exact"
print(requirements.network)             # "solana-mainnet"
print(requirements.asset)               # USDC mint address
print(requirements.max_amount_required) # "10000" (atomic units)
print(requirements.pay_to)              # Recipient address
```

---

### Verify Payment

Verify a signed payment transaction:

```python
result = client.verify(payment_header, requirements)

if result.is_valid:
    print("✅ Payment verified!")
    print(f"Payer: {result.payer}")
else:
    print(f"❌ Invalid: {result.invalid_reason}")
```

---

### Settle Payment

Settle a verified payment on-chain:

```python
result = client.settle(payment_header, requirements)

if result.success:
    print(f"✅ Settled! TX: {result.tx_hash}")
else:
    print(f"❌ Failed: {result.error}")
```

---

### Access Protected Resource

Make requests to x402-protected endpoints:

```python
# First request - will get 402
response = client.request_protected("https://api.example.com/premium")

if response["status"] == 402:
    # Payment required
    payment_info = response["data"]
    requirements = payment_info["accepts"][0]
    
    # Sign transaction and retry with payment
    # ... sign transaction ...
    
    response = client.request_protected(
        "https://api.example.com/premium",
        payment_header=signed_transaction
    )
    
    if response["status"] == 200:
        print("✅ Access granted!")
        print(response["data"])
```

---

### Event Handling

Subscribe to payment events:

```python
def on_payment_verified(data):
    print(f"Payment verified: {data}")

def on_payment_settled(data):
    print(f"Payment settled: {data.tx_hash}")

def on_error(data):
    print(f"Error: {data['error']}")

# Subscribe
unsubscribe = client.on("payment:verified", on_payment_verified)
client.on("payment:settled", on_payment_settled)
client.on("payment:error", on_error)

# Later, unsubscribe
unsubscribe()
```

**Available Events:**
- `payment:requirements` - Requirements generated
- `payment:verifying` - Verification started
- `payment:verified` - Payment verified
- `payment:settling` - Settlement started
- `payment:settled` - Payment settled on-chain
- `payment:error` - Error occurred

---

### Health & Info

```python
# Check API health
health = client.health()
print(f"Status: {health.status}")

# Get supported payment methods
supported = client.get_supported()
print(f"Networks: {supported.networks}")
print(f"Schemes: {supported.schemes}")

# Get fee payer
fee_payer = client.get_fee_payer()
print(f"Fee payer: {fee_payer.fee_payer}")
```

---

## 🔧 Utilities

```python
from acceso_x402 import (
    usdc_to_atomic,
    atomic_to_usdc,
    format_usdc,
    is_valid_pubkey,
    encode_base64,
    decode_base64,
)

# Convert amounts
usdc_to_atomic(1.50)        # 1500000
atomic_to_usdc(1500000)     # 1.5
format_usdc(1.50)           # "$1.50 USDC"

# Validate addresses
is_valid_pubkey("EPjFWdd5...")  # True
is_valid_pubkey("invalid")       # False

# Base64 encoding
encoded = encode_base64(b"data")
decoded = decode_base64(encoded)
```

---

## 💡 Server-Side Integration

Protect your API endpoints:

```python
from flask import Flask, request, jsonify
from acceso_x402 import X402Client, X402Config

app = Flask(__name__)
client = X402Client(X402Config(api_key="your_key"))

@app.route("/api/premium-data")
def premium_data():
    payment_header = request.headers.get("X-PAYMENT")
    
    if not payment_header:
        # Return 402 with payment requirements
        requirements = client.generate_requirements(
            price="0.01",
            pay_to="your_wallet",
            resource="/api/premium-data"
        )
        return jsonify({
            "error": "Payment Required",
            "accepts": [requirements.to_dict()]
        }), 402
    
    # Verify payment
    result = client.verify(payment_header, requirements)
    
    if not result.is_valid:
        return jsonify({"error": result.invalid_reason}), 402
    
    # Settle payment
    settle = client.settle(payment_header, requirements)
    
    if not settle.success:
        return jsonify({"error": settle.error}), 500
    
    # Return premium data
    return jsonify({"data": "Premium content here!"})
```

---

## 📋 Type Definitions

```python
from acceso_x402 import (
    X402Config,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    HealthResponse,
    SupportedResponse,
)
```

---

## 🔒 Constants

```python
from acceso_x402.types import (
    USDC_MAINNET_MINT,  # USDC on mainnet
    USDC_DEVNET_MINT,   # USDC on devnet
    USDC_DECIMALS,      # 6
)
```

---

## 🔧 Error Handling

```python
from acceso_x402 import X402Client, X402Error

try:
    requirements = client.generate_requirements(...)
except X402Error as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Status: {e.status}")
```

---

## 📄 License

MIT © [Acceso](https://acceso.dev)

---

<div align="center">

**Built with ❤️ by the Acceso Team**

[Website](https://acceso.dev) • [Twitter](https://twitter.com/AccesoDev) • [Discord](https://discord.gg/acceso)

</div>
