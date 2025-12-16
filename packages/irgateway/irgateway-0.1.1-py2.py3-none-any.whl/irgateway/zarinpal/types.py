from __future__ import annotations
from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
from typing import Optional, List
from json import dumps


@dataclass(kw_only=True)
class DictMixin:
    def to_dict(self) -> dict:
        if not is_dataclass(self):
            raise TypeError("to_dict only works with dataclasses")

        def convert(value):
            if is_dataclass(value):
                return value.to_dict()
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, list):
                return [convert(v) for v in value]
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            return value

        return {k: convert(v) for k, v in asdict(self).items()}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_json(self, indent: int = None, ensure_ascii: bool = False) -> str:
        return dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii, default=str)

    def __str__(self):
        return self.to_json(indent=4)


@dataclass
class PaymentRequest(DictMixin):
    """
    Response from ZarinPal's payment request endpoint (pg/v4/payment/request.json).

    This dataclass models the API response after initiating a payment request.
    Upon success (code=100), it provides the authority for redirecting users to the payment gateway.

    Attributes:
        authority (str): Unique payment authority token. Append to StartPay URL for user redirection (e.g., https://www.zarinpal.com/pg/StartPay/{authority}).
        code (int): Response status code. 100 indicates success; other values (e.g., -12 for invalid amount) indicate errors.
        payment_url (str): Pre-constructed full redirect URL to ZarinPal's StartPay gateway.
        fee_type (Optional[str]): Who should pay the transaction fee.
        fee (Optional[int]): Calculated fee amount in Iranian Rials (IRR/IRT), if applicable.

    Properties:
        is_success (bool): True if transaction created (code == 100).

    Example Response (Success):
        {
            "data": {
                "code": 100,
                "authority": "A00000000000000000000000000123456789",
                "fee_type": "Merchant",
                "fee": 200
            }
        }

    Reference: ZarinPal API Documentation - Payment Request[](https://www.zarinpal.com/docs/paymentGateway/connectToGateway).
    """
    authority: str
    code: int
    payment_url: str
    fee_type: Optional[str] = None
    fee: Optional[int] = None

    @property
    def is_success(self) -> bool:
        return self.code == 100


@dataclass
class PaymentVerification(DictMixin):
    """
    Response from ZarinPal's payment verification endpoint (pg/v4/payment/verify.json).

    This dataclass models the API response after verifying a completed payment.
    Call this endpoint on callback or redirect from ZarinPal after user completes payment.

    Attributes:
        code (int): Verification status code. 100 means successful verification; others indicate errors (e.g., -11 for invalid authority).
        ref_id (int): Unique ZarinPal reference ID for the transaction (tracking number).
        card_pan (Optional[str]): Masked primary account number of the user's card (e.g., "6037-****-****-1234").
        card_hash (Optional[str]): Hashed card identifier for tokenization in future payments (no CVV required).
        fee_type (Optional[str]): Who should pay the transaction fee.
        fee (Optional[int]): Actual fee amount in Iranian Rials deducted by ZarinPal.
        wages (Optional[List[Wage]]): List of wage splits if commission sharing was configured in the request.

    Properties:
        is_success (bool): True if verification succeeded (code == 100).

    Example Response (Success):
        {
            "data": {
                "code": 100,
                "ref_id": 123456789,
                "card_pan": "6037-****-****-1234",
                "card_hash": "abc123...",
                "fee_type": "Merchant",
                "fee": 200,
                "wages": [{"iban": "IR...", "amount": 500, "description": "Commission"}]
            }
        }

    Reference: ZarinPal API Documentation - Payment Verification[](https://www.zarinpal.com/docs/sdk/nodejs/method/verify).
    """
    code: int
    ref_id: int
    card_pan: Optional[str] = None
    card_hash: Optional[str] = None
    fee_type: Optional[str] = None
    fee: Optional[int] = None
    wages: Optional[List["Wage"]] = None

    @property
    def is_success(self) -> bool:
        return self.code == 100


@dataclass
class UnverifiedTransaction(DictMixin):
    """
    Individual unverified transaction details returned in UnverifiedTransactions response.

    Represents a payment that was successfully initiated and paid by the user but not yet verified
    via the verification endpoint. Useful for recovering missed verifications.

    Attributes:
        authority (str): The payment authority token for this transaction.
        amount (int): Original transaction amount in Iranian Rials.
        callback_url (str): The merchant's callback URL specified in the original request.
        referer (Optional[str]): HTTP referer from the initial payment request.
        date (Optional[datetime]): Timestamp when the transaction was created.

    Example:
        {
            "authority": "A00000000000000000000000000123456789",
            "amount": 100000,
            "callback_url": "https://example.com/verify",
            "referer": "https://example.com/pay",
            "date": "2025-12-06T10:00:00Z"
        }

    Reference: ZarinPal API Documentation - Unverified Transactions[](https://www.zarinpal.com/docs/paymentGateway/otherMethods/unVerified).
    """
    authority: str
    amount: int
    callback_url: str
    referer: Optional[str] = None
    date: Optional[datetime] = None


@dataclass
class UnverifiedTransactions(DictMixin):
    """
    Response from ZarinPal's unverified transactions endpoint (pg/v4/payment/unVerified.json).

    Retrieves a list of up to 100 recent payments that have been paid but not verified.
    Use to identify and verify missed transactions.

    Attributes:
        code (int): Response status code. 100 for success.
        authorities (List[UnverifiedTransaction]): Array of unverified transaction details.

    Properties:
        is_success (bool): True if code == 100.

    Example Response (Success):
        {
            "data": {
                "code": 100,
                "authorities": [
                    {
                        "authority": "A00000000000000000000000000123456789",
                        "amount": 100000,
                        "callback_url": "https://example.com/verify"
                    }
                ]
            }
        }

    Reference: ZarinPal API Documentation - Unverified Transactions[](https://www.zarinpal.com/docs/sdk/nodejs/method/unVerified).
    """
    code: int
    authorities: List[UnverifiedTransaction]

    def __iter__(self):
        return iter(self.authorities)

    def __len__(self):
        return len(self.authorities)

    def __getitem__(self, index):
        return self.authorities[index]

    @property
    def is_success(self) -> bool:
        return self.code == 100


@dataclass
class PaymentMetadata(DictMixin):
    """
    Optional metadata object sent in the payment request body for additional transaction details.

    Enhances payment requests with customer info for receipts, fraud prevention, and session validation.
    Include in the 'metadata' field of the request payload.

    Attributes:
        auto_verify (Optional[bool]): Enable automatic verification post-payment (limited to sandbox/testing).
        email (Optional[str]): Customer's email address for sending payment receipts.
        mobile (Optional[str]): Customer's mobile number for SMS notifications and receipts.
        order_id (Optional[str]): Merchant's internal order or invoice ID for tracking.
        card_pan (Optional[str]): Specific masked card PAN to restrict payment to that card.

    Example in Request:
        {
            "metadata": {
                "email": "customer@example.com",
                "mobile": "09123456789",
                "order_id": "ORD-12345",
                "card_pan": "6037-****-****-1234"
            }
        }

    Reference: ZarinPal API Documentation - Metadata in Payment Request[](https://www.zarinpal.com/docs/paymentGateway/connectToGateway).
    """
    auto_verify: Optional[bool] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    order_id: Optional[str] = None
    card_pan: Optional[str] = None


@dataclass
class PaymentCartDataItem(DictMixin):
    """
    Single item within the shopping cart data for advanced payment requests.

    Part of the 'cart_items' array in payment requests for detailed invoicing and transparency.
    Allows ZarinPal to display itemized breakdowns to users.

    Attributes:
        item_name (str): Descriptive name or title of the product/service.
        item_amount (int): Unit price in Iranian Rials.
        item_count (int): Quantity of this item.
        item_amount_sum (Optional[int]): Total for this item (auto-calculated as item_amount * item_count if omitted).

    Post-Init: Automatically computes item_amount_sum if not provided.

    Example:
        {
            "item_name": "Sample Product",
            "item_amount": 50000,
            "item_count": 2,
            "item_amount_sum": 100000
        }

    Reference: ZarinPal API Documentation - Cart Items (advanced features in payment request).
    """
    item_name: str
    item_amount: int
    item_count: int
    item_amount_sum: Optional[int] = None

    def __post_init__(self):
        if self.item_amount_sum is None:
            self.item_amount_sum = self.item_amount * self.item_count


@dataclass
class PaymentCartDataAddedCosts(DictMixin):
    """
    Additional costs structure for cart data in payment requests.

    Represents extra charges like taxes or shipping added to the cart subtotal.
    Included in the 'cart_data.added_costs' object.

    Attributes:
        tax (Optional[int]): Tax amount in Iranian Rials (e.g., VAT).
        payment (Optional[int]): Payment processing fee charged to the customer.
        transport (Optional[int]): Shipping or transportation costs in Rials.

    Example:
        {
            "tax": 5000,
            "payment": 2000,
            "transport": 10000
        }

    Reference: ZarinPal API Documentation - Cart Additional Costs.
    """
    tax: Optional[int] = None
    payment: Optional[int] = None
    transport: Optional[int] = None


@dataclass
class PaymentCartDataDeductions(DictMixin):
    """
    Deductions structure for cart data in payment requests.

    Represents discounts or reductions subtracted from the cart subtotal.
    Included in the 'cart_data.deductions' object.

    Attributes:
        discount (Optional[int]): Overall discount amount in Iranian Rials.

    Example:
        {
            "discount": 10000
        }

    Reference: ZarinPal API Documentation - Cart Deductions.
    """
    discount: Optional[int] = None


@dataclass
class PaymentCartData(DictMixin):
    """
    Complete shopping cart data object for advanced, itemized payment requests.

    Sent in the 'cart_data' field of the payment request for e-commerce scenarios.
    Enables detailed billing views and better user experience.

    Attributes:
        items (List[PaymentCartDataItem]): Array of individual cart items.
        added_costs (Optional[PaymentCartDataAddedCosts]): Extra costs like tax/shipping.
        deductions (Optional[PaymentCartDataDeductions]): Discounts or subtractions.

    Example in Request:
        {
            "cart_data": {
                "items": [{"item_name": "Product", "item_amount": 50000, "item_count": 1}],
                "added_costs": {"tax": 5000},
                "deductions": {"discount": 2000}
            }
        }

    Reference: ZarinPal API Documentation - Cart Data in Payment Requests.
    """
    items: List[PaymentCartDataItem]
    added_costs: Optional[PaymentCartDataAddedCosts] = None
    deductions: Optional[PaymentCartDataDeductions] = None

    def __iter__(self):
        return iter(self.items)


@dataclass
class Wage(DictMixin):
    """
    Wage (commission split) configuration for multi-party payments.

    Defines shares transferred to third-party IBANs post-verification (e.g., for marketplaces).
    Included in the 'wages' array of payment requests or verification responses.

    Attributes:
        iban (str): Recipient's Iranian IBAN (Sheba number, starting with 'IR').
        amount (int): Share amount in Iranian Rials.
        description (str): Brief description of the wage purpose.

    Example:
        {
            "iban": "IR123456789012345678901234",
            "amount": 5000,
            "description": "Affiliate Commission"
        }

    Note: Total wages must not exceed transaction amount minus fees.
    Reference: ZarinPal API Documentation - Wages/Commissions[](https://www.zarinpal.com/docs/paymentGateway/advanced/wages).
    """
    iban: str
    amount: int
    description: str


@dataclass
class FeeCalculation(DictMixin):
    """
    Response from ZarinPal's fee calculation endpoint (pg/v4/fee/calculate.json).

    Pre-calculates transaction fees before initiating a payment.
    Helps merchants decide who pays the fee (customer or merchant).

    Attributes:
        amount (int): Original transaction amount in Iranian Rials.
        fee (int): Computed gateway fee amount.
        fee_type (str): Who should pay the transaction fee.
        suggested_amount (int): Adjusted amount if merchant covers the fee (original + fee).

    Example Response:
        {
            "data": {
                "amount": 100000,
                "fee": 2000,
                "fee_type": "Merchant",
                "suggested_amount": 102000
            }
        }

    Reference: ZarinPal API Documentation - Fee Calculation (inferred from SDKs like Python/Node.js).
    """
    amount: int
    fee: int
    fee_type: str
    suggested_amount: int


@dataclass
class ZarinpalConfig(DictMixin):
    """
    Configuration settings for integrating with ZarinPal API.

    Used to initialize clients or SDKs with environment-specific parameters.

    Attributes:
        startpay_endpoint (Optional[str]): Custom base URL for StartPay redirects (defaults to sandbox/production).
        timeout (int): HTTP request timeout in seconds (default: 30).

    Example:
        {
            "startpay_endpoint": "https://sandbox.zarinpal.com/pg/StartPay/",
            "timeout": 60
        }

    Note: For full setup, include merchant_id and sandbox flag in client instantiation.
    Reference: ZarinPal SDK Documentation - Configuration (e.g., Node.js SDK).
    """
    startpay_endpoint: Optional[str] = None
    timeout: int = 30
