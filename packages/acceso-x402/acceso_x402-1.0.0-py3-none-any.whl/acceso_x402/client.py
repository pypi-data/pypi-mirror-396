"""
X402 API Client for Solana payments
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union

import requests

from .types import (
    X402Config,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    HealthResponse,
    SupportedResponse,
    FeePayerResponse,
    PaymentResult,
    USDC_MAINNET_MINT,
)
from .utils import usdc_to_atomic, atomic_to_usdc, encode_base64


class X402Error(Exception):
    """Exception raised for x402 API errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class X402Client:
    """
    Client for x402 HTTP payment protocol on Solana.
    
    The x402 protocol enables pay-per-request API monetization using
    USDC payments on Solana.
    
    Example:
        >>> from acceso_x402 import X402Client, X402Config
        >>> 
        >>> config = X402Config(api_key="your_api_key")
        >>> client = X402Client(config)
        >>> 
        >>> # Generate payment requirements
        >>> requirements = client.generate_requirements(
        ...     price="0.01",
        ...     pay_to="recipient_wallet",
        ...     resource="/api/premium-data"
        ... )
        >>> 
        >>> # Verify a payment
        >>> result = client.verify(payment_header, requirements)
    """
    
    def __init__(self, config: Union[X402Config, Dict[str, Any]]):
        """
        Initialize the X402 client.
        
        Args:
            config: X402Config object or dict with configuration
        """
        if isinstance(config, dict):
            config = X402Config(**config)
        
        self.config = config
        self.api_url = config.api_url.rstrip("/")
        self.timeout = config.timeout
        self.debug = config.debug
        
        # Setup logging
        self.logger = logging.getLogger("acceso_x402")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(
                    "[x402] %(message)s"
                ))
                self.logger.addHandler(handler)
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Session for connection pooling
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
            "User-Agent": "acceso-x402-python/1.0.0",
        })
    
    def _log(self, message: str, *args: Any) -> None:
        """Log debug message"""
        if self.debug:
            self.logger.debug(message, *args)
    
    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method
            path: API path
            body: Request body
            headers: Additional headers
        
        Returns:
            Response data
        
        Raises:
            X402Error: On API error
        """
        url = f"{self.api_url}{path}"
        self._log(f"{method} {url}")
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
                timeout=self.timeout,
            )
            
            data = response.json()
            
            if not response.ok and response.status_code != 402:
                error_msg = data.get("error") or data.get("detail") or data.get("message") or f"HTTP {response.status_code}"
                raise X402Error(
                    message=error_msg,
                    code=data.get("code"),
                    status=response.status_code,
                    details=data,
                )
            
            return data
            
        except requests.Timeout:
            raise X402Error("Request timeout", code="TIMEOUT")
        except requests.RequestException as e:
            raise X402Error(f"Network error: {e}", code="NETWORK_ERROR")
    
    # ========================================
    # Event Handling
    # ========================================
    
    def on(self, event: str, handler: Callable) -> Callable[[], None]:
        """
        Subscribe to SDK events.
        
        Args:
            event: Event name (e.g., "payment:required", "payment:success")
            handler: Callback function
        
        Returns:
            Unsubscribe function
        
        Example:
            >>> def on_payment(data):
            ...     print(f"Payment: {data}")
            >>> 
            >>> unsubscribe = client.on("payment:success", on_payment)
            >>> # Later...
            >>> unsubscribe()
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        
        self._event_handlers[event].append(handler)
        
        def unsubscribe():
            if event in self._event_handlers:
                self._event_handlers[event].remove(handler)
        
        return unsubscribe
    
    def _emit(self, event: str, data: Any = None) -> None:
        """Emit an event to all handlers"""
        self._log(f"Event: {event}")
        
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                self._log(f"Event handler error: {e}")
    
    # ========================================
    # Health & Info
    # ========================================
    
    def health(self) -> HealthResponse:
        """
        Check API health status.
        
        Returns:
            HealthResponse with status info
        
        Example:
            >>> health = client.health()
            >>> print(health.status)
            "ok"
        """
        data = self._request("GET", "/health")
        return HealthResponse.from_dict(data)
    
    def get_supported(self) -> SupportedResponse:
        """
        Get supported payment schemes and networks.
        
        Returns:
            SupportedResponse with supported methods
        
        Example:
            >>> supported = client.get_supported()
            >>> print(supported.networks)
            ["solana-mainnet", "solana-devnet"]
        """
        data = self._request("GET", "/v1/x402/supported")
        return SupportedResponse.from_dict(data)
    
    def get_fee_payer(self) -> FeePayerResponse:
        """
        Get the facilitator's fee payer public key.
        
        Returns:
            FeePayerResponse with fee payer address
        
        Example:
            >>> fee_payer = client.get_fee_payer()
            >>> print(fee_payer.fee_payer)
            "ABC123..."
        """
        data = self._request("GET", "/v1/x402/fee-payer")
        return FeePayerResponse.from_dict(data)
    
    # ========================================
    # Payment Flow
    # ========================================
    
    def generate_requirements(
        self,
        price: Union[str, float],
        pay_to: str,
        resource: str,
        description: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        asset: Optional[str] = None,
        network: str = "solana-mainnet",
    ) -> PaymentRequirements:
        """
        Generate payment requirements for a protected resource.
        
        Args:
            price: Price in USDC (e.g., "0.01" or 0.01)
            pay_to: Recipient wallet address
            resource: Resource URL being protected
            description: Optional description
            timeout_seconds: Payment validity period
            asset: Token mint (defaults to USDC)
            network: Solana network
        
        Returns:
            PaymentRequirements for the resource
        
        Example:
            >>> requirements = client.generate_requirements(
            ...     price="0.01",
            ...     pay_to="recipient_wallet",
            ...     resource="/api/premium"
            ... )
        """
        # Convert price to string
        if isinstance(price, (int, float)):
            price = str(price)
        
        body = {
            "price": price,
            "payTo": pay_to,
            "resource": resource,
        }
        
        if description:
            body["description"] = description
        if timeout_seconds:
            body["timeout_seconds"] = timeout_seconds
        if asset:
            body["asset"] = asset
        if network:
            body["network"] = network
        
        data = self._request("POST", "/v1/x402/requirements", body)
        requirements = PaymentRequirements.from_dict(data)
        
        self._emit("payment:requirements", requirements)
        return requirements
    
    def verify(
        self,
        payment_header: str,
        requirements: Union[PaymentRequirements, Dict[str, Any]],
    ) -> VerifyResponse:
        """
        Verify a payment header against requirements.
        
        Args:
            payment_header: Base64 encoded signed transaction
            requirements: Payment requirements to verify against
        
        Returns:
            VerifyResponse indicating validity
        
        Example:
            >>> result = client.verify(payment_header, requirements)
            >>> if result.is_valid:
            ...     print("Payment verified!")
        """
        self._emit("payment:verifying")
        
        if isinstance(requirements, PaymentRequirements):
            requirements_dict = requirements.to_dict()
        else:
            requirements_dict = requirements
        
        data = self._request("POST", "/v1/x402/verify", {
            "paymentHeader": payment_header,
            "paymentRequirements": requirements_dict,
        })
        
        result = VerifyResponse.from_dict(data)
        self._emit("payment:verified", result)
        return result
    
    def settle(
        self,
        payment_header: str,
        requirements: Union[PaymentRequirements, Dict[str, Any]],
    ) -> SettleResponse:
        """
        Settle a payment on-chain.
        
        Args:
            payment_header: Base64 encoded signed transaction
            requirements: Payment requirements
        
        Returns:
            SettleResponse with transaction hash
        
        Example:
            >>> result = client.settle(payment_header, requirements)
            >>> if result.success:
            ...     print(f"TX: {result.tx_hash}")
        """
        self._emit("payment:settling")
        
        if isinstance(requirements, PaymentRequirements):
            requirements_dict = requirements.to_dict()
        else:
            requirements_dict = requirements
        
        data = self._request("POST", "/v1/x402/settle", {
            "paymentHeader": payment_header,
            "paymentRequirements": requirements_dict,
        })
        
        result = SettleResponse.from_dict(data)
        
        if result.success:
            self._emit("payment:settled", result)
        else:
            self._emit("payment:error", {"error": result.error})
        
        return result
    
    # ========================================
    # Protected Resource Access
    # ========================================
    
    def request_protected(
        self,
        url: str,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        payment_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to a protected resource.
        
        Args:
            url: Full URL of the protected resource
            method: HTTP method
            body: Request body
            headers: Additional headers
            payment_header: X-PAYMENT header value
        
        Returns:
            Dict with "status" and "data" keys
        
        Example:
            >>> response = client.request_protected(
            ...     "https://api.example.com/premium",
            ...     payment_header=signed_tx
            ... )
            >>> if response["status"] == 402:
            ...     # Payment required
            ...     requirements = response["data"]["accepts"][0]
        """
        request_headers = {"Content-Type": "application/json"}
        
        if headers:
            request_headers.update(headers)
        
        if payment_header:
            request_headers["X-PAYMENT"] = payment_header
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                headers=request_headers,
                timeout=self.timeout,
            )
            
            return {
                "status": response.status_code,
                "data": response.json(),
            }
        except Exception as e:
            raise X402Error(f"Request failed: {e}", code="REQUEST_ERROR")
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def get_usdc_balance(
        self,
        wallet_address: str,
        usdc_mint: str = USDC_MAINNET_MINT,
    ) -> float:
        """
        Get USDC balance for a wallet.
        
        Args:
            wallet_address: Solana wallet address
            usdc_mint: USDC token mint address
        
        Returns:
            USDC balance as float
        
        Note:
            This uses the Acceso API to fetch balance.
        """
        data = self._request(
            "GET",
            f"/v1/solana/wallet/{wallet_address}/balance",
            headers={"X-Token-Mint": usdc_mint},
        )
        
        return atomic_to_usdc(data.get("balance", 0))
    
    def get_sol_balance(self, wallet_address: str) -> float:
        """
        Get SOL balance for a wallet.
        
        Args:
            wallet_address: Solana wallet address
        
        Returns:
            SOL balance as float
        """
        data = self._request("GET", f"/v1/solana/wallet/{wallet_address}")
        return data.get("sol_balance", 0)
    
    @staticmethod
    def parse_amount(usd_amount: str) -> int:
        """
        Parse USD string to atomic units.
        
        Args:
            usd_amount: Amount string (e.g., "$1.50")
        
        Returns:
            Atomic units (e.g., 1500000)
        """
        return usdc_to_atomic(usd_amount)
    
    @staticmethod
    def format_amount(atomic_units: Union[str, int]) -> str:
        """
        Format atomic units to USD string.
        
        Args:
            atomic_units: Amount in atomic units
        
        Returns:
            Formatted string (e.g., "$1.50")
        """
        usd = atomic_to_usdc(atomic_units)
        return f"${usd:.2f}"
    
    def close(self) -> None:
        """Close the client session"""
        self._session.close()
    
    def __enter__(self) -> "X402Client":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
