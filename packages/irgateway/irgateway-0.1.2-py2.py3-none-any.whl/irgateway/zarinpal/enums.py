from enum import Enum


class Environment(Enum):
    SANDBOX = "https://sandbox.zarinpal.com/"
    PRODUCTION = "https://payment.zarinpal.com/"


class PaymentStatus(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    IN_BANK = "IN_BANK"
    PAID = "PAID"


class Currency(Enum):
    TOMAN = "IRT"
    RIAL = "IRR"
