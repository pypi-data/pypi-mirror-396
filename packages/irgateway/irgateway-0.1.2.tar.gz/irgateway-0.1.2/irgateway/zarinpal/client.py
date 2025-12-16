from typing import Optional, List, Dict, Tuple
from datetime import datetime
from urllib.parse import urljoin

from irgateway.zarinpal.errors import ERROR_MAP, ZarinpalException
from irgateway.zarinpal.types import (
    PaymentRequest, PaymentVerification,
    UnverifiedTransactions, UnverifiedTransaction,
    PaymentMetadata, ZarinpalConfig, PaymentCartData, Wage, FeeCalculation
)
from irgateway.zarinpal.enums import Environment, Currency, PaymentStatus

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class BaseClient:
    """Base client containing shared logic between sync and async clients."""

    def __init__(
            self,
            merchant_id: str,
            environment: Environment = Environment.PRODUCTION,
            config: Optional[ZarinpalConfig] = None,
    ):
        """
        Initialize base client.

        Args:
            merchant_id: Zarinpal merchant ID (UUID format)
            environment: Payment environment (PRODUCTION or SANDBOX)
            config: Optional configuration override
        """
        self.merchant_id = merchant_id
        self.environment = environment
        self.config = config or ZarinpalConfig()
        self._base_url = environment.value

    def _get_endpoint(self, path: str) -> str:
        """Construct full API endpoint URL."""
        return urljoin(self._base_url, path)

    def _get_custom_endpoint(self, authority: str) -> str:
        """Get payment gateway start URL (supports custom StartPay endpoint)."""
        if self.config.startpay_endpoint:
            return urljoin(self.config.startpay_endpoint, authority)
        return urljoin(self._base_url, f"pg/StartPay/{authority}")

    @staticmethod
    def _get_response(response: dict) -> Tuple[Optional[int], dict]:
        """Normalize API response structure."""
        if response.get('data'):
            data = response['data']
            code = data.get('code')
        elif response.get('errors'):
            data = response['errors']
            code = data.get('code')
        else:
            data = {}
            code = None
        return code, data

    @staticmethod
    def _handle_error(code: Optional[int], message: str = None):
        """Raise appropriate exception based on error code."""
        if code and code in ERROR_MAP:
            raise ERROR_MAP[code]()
        raise ZarinpalException(code, message or "Unknown error", "")

    @staticmethod
    def _parse_unverified(data: Dict) -> UnverifiedTransactions:
        """Parse unverified transactions response into structured object."""
        authorities = []
        for auth in data.get("authorities", []):
            authorities.append(UnverifiedTransaction(
                authority=auth.get("authority"),
                amount=auth.get("amount"),
                callback_url=auth.get("callback_url"),
                referer=auth.get("referer"),
                date=datetime.strptime(auth["date"], "%Y-%m-%d %H:%M:%S") if auth.get("date") else None
            ))
        return UnverifiedTransactions(
            code=data.get("code", 100),
            authorities=authorities
        )


class ZarinpalClient(BaseClient):
    """Synchronous client for Zarinpal Payment Gateway."""
    __type__ = 'SYNC'

    def __init__(
            self,
            merchant_id: str,
            environment: Environment = Environment.PRODUCTION,
            config: Optional[ZarinpalConfig] = None,
    ):
        """
        Initialize synchronous Zarinpal client.

        Args:
            merchant_id: Your Zarinpal merchant ID
            environment: Use SANDBOX for testing
            config: Custom configuration (timeout, custom StartPay, etc.)

        Raises:
            ImportError: If `requests` library is not installed
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("Install 'requests' to use synchronous client: pip install requests")

        super().__init__(merchant_id, environment, config)
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close underlying HTTP session."""
        self._session.close()

    def request(
            self,
            amount: int,
            callback_url: str,
            description: str,
            currency: Currency = Currency.RIAL,
            metadata: Optional[PaymentMetadata] = None,
            cart_data: Optional[PaymentCartData] = None,
            wages: Optional[List[Wage]] = None,
    ) -> PaymentRequest:
        """
        Create a new payment request.

        Args:
            amount: Amount in Rial/Toman (min 1000 IRT or 10000 IRR)
            callback_url: URL user returns to after payment
            description: Payment description shown to user
            currency: Currency.RIAL (Toman) or Currency.TOMAN (Rial)
            metadata: Mobile/email or custom metadata
            cart_data: Structured cart information
            wages: List of IBANs and amounts for shared settlement

        Returns:
            PaymentRequest with authority and payment URL
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
            "currency": currency.value,
        }

        if metadata:
            payload["metadata"] = metadata.to_dict()
        if cart_data:
            payload["cart_data"] = cart_data.to_dict()
        if wages:
            payload["wages"] = [w.to_dict() for w in wages]

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/request.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, data = self._get_response(response.json())

        if code != 100:
            self._handle_error(code)

        payment_url = self._get_custom_endpoint(data["authority"])

        return PaymentRequest(
            authority=data["authority"],
            code=code,
            payment_url=payment_url,
            fee_type=data.get("fee_type"),
            fee=data.get("fee")
        )

    def verify(self, authority: str, amount: int) -> PaymentVerification:
        """Verify payment status after user returns from bank."""
        payload = {
            "merchant_id": self.merchant_id,
            "authority": authority,
            "amount": amount
        }

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/verify.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, data = self._get_response(response.json())

        if code != 100:
            self._handle_error(code)

        return PaymentVerification(
            code=code,
            ref_id=data.get("ref_id"),
            card_pan=data.get("card_pan"),
            card_hash=data.get("card_hash"),
            fee_type=data.get("fee_type"),
            fee=data.get("fee"),
            wages=[Wage(**w) for w in data.get("wages", [])] if data.get("wages") else None,
        )

    def unverified(self) -> UnverifiedTransactions:
        """Retrieve list of successful but unverified transactions."""
        payload = {"merchant_id": self.merchant_id}

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/unVerified.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, data = self._get_response(response.json())

        if code != 100:
            self._handle_error(code)

        return self._parse_unverified(data)

    def reverse(self, authority: str) -> bool:
        """Request refund (requires special permission and access token)."""
        payload = {"merchant_id": self.merchant_id, "authority": authority}

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/reverse.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, _ = self._get_response(response.json())
        return code == 100

    def inquiry(self, authority: str) -> PaymentStatus:
        """Check current status of a payment authority."""
        payload = {"merchant_id": self.merchant_id, "authority": authority}

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/inquiry.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, data = self._get_response(response.json())

        if code != 100:
            self._handle_error(code)

        return PaymentStatus(data.get("status"))

    def calculate_fee(self, amount: int, currency: Currency = Currency.RIAL) -> FeeCalculation:
        """Calculate gateway fee for a specific amount and authority."""
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "currency": currency.value,
        }

        response = self._session.post(
            self._get_endpoint("pg/v4/payment/feeCalculation.json"),
            json=payload,
            timeout=self.config.timeout
        )
        code, data = self._get_response(response.json())

        if code != 100:
            self._handle_error(code)

        return FeeCalculation(
            amount=data.get("amount"),
            fee=data.get("fee"),
            fee_type=data.get("fee_type"),
            suggested_amount=data.get("suggested_amount"),
        )


class AsyncZarinpalClient(BaseClient):
    """Asynchronous client for Zarinpal Payment Gateway (fully compatible with sync version)."""
    __type__ = 'ASYNC'

    def __init__(
            self,
            merchant_id: str,
            environment: Environment = Environment.PRODUCTION,
            config: Optional[ZarinpalConfig] = None,
    ):
        """
        Initialize asynchronous client.

        Args:
            merchant_id: Zarinpal merchant ID
            environment: SANDBOX or PRODUCTION
            config: Optional config (timeout, custom StartPay URL, etc.)

        Raises:
            ImportError: If aiohttp is not installed
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError("Install 'aiohttp' to use async client: pip install aiohttp")

        super().__init__(merchant_id, environment, config)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
            self,
            amount: int,
            callback_url: str,
            description: str,
            currency: Currency = Currency.RIAL,
            metadata: Optional[PaymentMetadata] = None,
            cart_data: Optional[PaymentCartData] = None,
            wages: Optional[List[Wage]] = None,
    ) -> PaymentRequest:
        """
        Create payment request (async) - identical behavior to sync version.
        """
        await self._ensure_session()

        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
            "currency": currency.value,
        }

        if metadata:
            payload["metadata"] = metadata.to_dict()
        if cart_data:
            payload["cart_data"] = cart_data.to_dict()
        if wages:
            payload["wages"] = [w.to_dict() for w in wages]

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/request.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, data = self._get_response(result)

            if code != 100:
                self._handle_error(code)

            payment_url = self._get_custom_endpoint(data["authority"])

            return PaymentRequest(
                authority=data["authority"],
                code=code,
                payment_url=payment_url,
                fee_type=data.get("fee_type"),
                fee=data.get("fee")
            )

    async def verify(self, authority: str, amount: int) -> PaymentVerification:
        """Verify payment after redirect (async)."""
        await self._ensure_session()

        payload = {
            "merchant_id": self.merchant_id,
            "authority": authority,
            "amount": amount
        }

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/verify.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, data = self._get_response(result)

            if code != 100:
                self._handle_error(code)

            return PaymentVerification(
                code=code,
                ref_id=data.get("ref_id"),
                card_pan=data.get("card_pan"),
                card_hash=data.get("card_hash"),
                fee_type=data.get("fee_type"),
                fee=data.get("fee"),
                wages=[Wage(**w) for w in data.get("wages", [])] if data.get("wages") else None,
            )

    async def unverified(self) -> UnverifiedTransactions:
        """Get list of unverified transactions (async)."""
        await self._ensure_session()

        payload = {"merchant_id": self.merchant_id}

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/unVerified.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, data = self._get_response(result)

            if code != 100:
                self._handle_error(code)

            return self._parse_unverified(data)

    async def reverse(
            self,
            authority: str,
    ) -> bool:
        """
        Request a full refund for a successful payment (reverse transaction).

        Note:
            - Requires "Refund Permission" enabled on your Zarinpal merchant panel
            - Uses `reverse.json` endpoint (no access token needed)
            - Only works on successfully verified payments

        Args:
            authority: The payment authority (from request or verify step)

        Returns:
            bool: True if refund was successfully requested

        Raises:
            ZarinpalException: With appropriate error code (e.g., -11: already refunded, etc.)
        """
        await self._ensure_session()

        payload = {
            "merchant_id": self.merchant_id,
            "authority": authority
        }

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/reverse.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, _ = self._get_response(result)
            return code == 100

    async def inquiry(self, authority: str) -> PaymentStatus:
        """
        Check the current status of a payment using its authority.

        Useful for:
            - Re-checking payment status after network issues
            - Syncing offline payments
            - Debugging callback failures

        Args:
            authority: Payment authority string

        Returns:
            PaymentStatus enum (e.g., PaymentStatus.SUCCESS, PaymentStatus.PENDING, etc.)
        """
        await self._ensure_session()

        payload = {
            "merchant_id": self.merchant_id,
            "authority": authority
        }

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/inquiry.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, data = self._get_response(result)

            if code != 100:
                self._handle_error(code)

            status_code = data.get("status")
            return PaymentStatus(status_code)

    async def calculate_fee(
            self,
            amount: int,
            currency: Currency = Currency.RIAL
    ) -> FeeCalculation:
        """
        Calculate Zarinpal gateway fee for a given amount and authority.

        This is useful when you want to:
            - Show exact fee to user before payment
            - Adjust final amount to cover fee (e.g., user pays X, you receive X)

        Args:
            amount: Amount to calculate fee for
            currency: Currency.RIAL (Toman) or Currency.TOMAN (Rial)

        Returns:
            FeeCalculation object with fee, suggested_amount, etc.
        """
        await self._ensure_session()

        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "currency": currency.value,
        }

        async with self._session.post(
                self._get_endpoint("pg/v4/payment/feeCalculation.json"),
                json=payload
        ) as resp:
            result = await resp.json()
            code, data = self._get_response(result)

            if code != 100:
                self._handle_error(code)

            return FeeCalculation(
                amount=data.get("amount"),
                fee=data.get("fee"),
                fee_type=data.get("fee_type"),
                suggested_amount=data.get("suggested_amount"),
            )
