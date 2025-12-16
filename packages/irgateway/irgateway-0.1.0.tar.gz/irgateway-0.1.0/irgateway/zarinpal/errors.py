class ZarinpalException(Exception):
    """Base exception for Zarinpal SDK"""

    def __init__(self, code: int, message: str, message_fa: str = ""):
        self.code = code
        self.message = message
        self.message_fa = message_fa
        super().__init__(f"[{code}] {message}")


# Public Errors (-9 to -19)
class ValidationException(ZarinpalException):
    def __init__(self):
        super().__init__(-9, "Validation error", "خطای اعتبار سنجی")


class InvalidTerminalException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -10,
            "Terminal is not valid, please check merchant_id or ip address",
            "ای پی یا مرچنت کد پذیرنده صحیح نیست"
        )


class InactiveTerminalException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -11,
            "Terminal is not active, please contact our support team",
            "مرچنت کد فعال نیست، لطفا به امور مشتریان مراجعه کنید"
        )


class TooManyAttemptsException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -12,
            "Too many attempts, please try again later",
            "تلاش بیش از دفعات مجاز در یک بازه زمانی کوتاه"
        )


class TerminalLimitReachedException(ZarinpalException):
    def __init__(self):
        super().__init__(-13, "Terminal limit reached", "خطای مربوط به محدودیت تراکنش")


class CallbackDomainMismatchException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -14,
            "The callback URL domain does not match the registered terminal domain",
            "کال‌بک URL با دامنه ثبت شده درگاه مغایرت دارد"
        )


class TerminalSuspendedException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -15,
            "Terminal user is suspended, please contact our support team",
            "درگاه پرداخت به حالت تعلیق در آمده است"
        )


class TerminalLevelException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -16,
            "Terminal user level is not valid, please contact our support team",
            "سطح تایید پذیرنده پایین تر از سطح نقره ای است"
        )


class BlueLevelLimitException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -17,
            "Terminal user level is not valid, please contact our support team",
            "محدودیت پذیرنده در سطح آبی"
        )


class ReferrerMismatchException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -18,
            "The referrer address does not match the registered domain",
            "امکان استفاده از کد درگاه اختصاصی خود بر روی سایت دیگری را ندارید"
        )


class TransactionBannedException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -19,
            "Terminal user transactions are banned",
            "امکان ایجاد تراکنش برای این ترمینال امکان پذیر نیست"
        )


# Payment Request Errors (-30 to -41)
class FloatingWagesNotAllowedException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -30,
            "Terminal do not allow to accept floating wages",
            "پذیرنده اجازه دسترسی به سرویس تسویه اشتراکی شناور را ندارد"
        )


class NoBankAccountException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -31,
            "Terminal do not allow to accept wages, please add default bank account in panel",
            "حساب بانکی تسویه را به پنل اضافه کنید"
        )


class WagesOverloadException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -32,
            "Wages is not valid, Total wages has been overload max amount",
            "مبلغ وارد شده از مبلغ کل تراکنش بیشتر است"
        )


class InvalidWagesFloatingException(ZarinpalException):
    def __init__(self):
        super().__init__(-33, "Wages floating is not valid", "درصدهای وارد شده صحیح نیست")


class WagesFixedOverloadException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -34,
            "Wages is not valid, Total wages(fixed) has been overload max amount",
            "مبلغ وارد شده از مبلغ کل تراکنش بیشتر است"
        )


class TooManyWagesPartsException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -35,
            "Wages is not valid, Total wages has been reached the limit in max parts",
            "تعداد افراد دریافت کننده تسهیم بیش از حد مجاز است"
        )


class MinimumWagesException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -36,
            "The minimum amount for wages should be 10,000 Rials",
            "حداقل مبلغ جهت تسهیم باید ۱۰۰۰۰ ریال باشد"
        )


class InactiveIbanException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -37,
            "One or more iban entered for wages from the bank side are inactive",
            "یک یا چند شماره شبای وارد شده برای تسهیم از سمت بانک غیر فعال است"
        )


class IbanNotSetException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -38,
            "Wages need to set Iban in shaparak",
            "خطا، عدم تعریف صحیح شبا، لطفا دقایقی دیگر تلاش کنید"
        )


class WagesErrorException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -39,
            "Wages have an error",
            "خطایی رخ داده است به امور مشتریان زرین پال اطلاع دهید"
        )


class InvalidExpireInException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -40,
            "Invalid extra params, expire_in is not valid",
            "پارامتر expire_in نامعتبر است"
        )


class MaxAmountExceededException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -41,
            "Maximum amount is 100,000,000 tomans",
            "حداکثر مبلغ پرداختی ۱۰۰ میلیون تومان است"
        )


# Payment Verify Errors (-50 to -55)
class AmountMismatchException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -50,
            "Session is not valid, amounts values is not the same",
            "مبلغ پرداخت شده با مقدار مبلغ ارسالی در متد وریفای متفاوت است"
        )


class PaymentFailedException(ZarinpalException):
    def __init__(self):
        super().__init__(-51, "Session is not valid, session is not active paid try", "پرداخت ناموفق")


class UnexpectedErrorException(ZarinpalException):
    def __init__(self):
        super().__init__(-52, "Oops! Please contact our support team", "خطای غیر منتظره‌ای رخ داده است")


class WrongMerchantException(ZarinpalException):
    def __init__(self):
        super().__init__(-53, "Session is not this merchant_id session", "پرداخت متعلق به این مرچنت کد نیست")


class InvalidAuthorityException(ZarinpalException):
    def __init__(self):
        super().__init__(-54, "Invalid authority", "اتوریتی نامعتبر است")


class ManualPaymentNotFoundException(ZarinpalException):
    def __init__(self):
        super().__init__(-55, "Manual payment request not found", "تراکنش مورد نظر یافت نشد")


# Payment Reverse Errors (-60 to -63)
class CannotReverseException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -60,
            "Session cannot be reversed with bank",
            "امکان ریورس کردن تراکنش با بانک وجود ندارد"
        )


class ReverseNotAllowedException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -61,
            "Session is not in success status",
            "تراکنش موفق نیست یا قبلا ریورس شده است"
        )


class IpNotSetException(ZarinpalException):
    def __init__(self):
        super().__init__(-62, "Terminal ip limit must be active", "آی پی درگاه ست نشده است")


class ReverseTimeExpiredException(ZarinpalException):
    def __init__(self):
        super().__init__(
            -63,
            "Maximum time for reverse this session is expired",
            "حداکثر زمان (۳۰ دقیقه) برای ریورس کردن این تراکنش منقضی شده است"
        )


# Success Codes
class AlreadyVerifiedException(ZarinpalException):
    def __init__(self):
        super().__init__(101, "Already verified", "تراکنش وریفای شده است")


# Referrer Errors
class InvalidReferrerCodeException(ZarinpalException):
    def __init__(self):
        super().__init__(429, "Invalid referrer code format", "قالب کد معرف معتبر نیست")


class InvalidDecodingException(ZarinpalException):
    def __init__(self):
        super().__init__(430, "Invalid decoding of referrer_id", "خطای رمزگشایی شناسه")


class ReferrerNotFoundException(ZarinpalException):
    def __init__(self):
        super().__init__(431, "Referrer user not found", "کاربر معرف یافت نشد")


class TerminalBelongsToReferrerException(ZarinpalException):
    def __init__(self):
        super().__init__(432, "Terminal belongs to referrer", "ترمینال متعلق به معرف است")


class TerminalAlreadyHasReferrerException(ZarinpalException):
    def __init__(self):
        super().__init__(433, "Terminal already has a referrer", "ترمینال از قبل دارای معرف است")


ERROR_MAP = {
    -9: ValidationException,
    -10: InvalidTerminalException,
    -11: InactiveTerminalException,
    -12: TooManyAttemptsException,
    -13: TerminalLimitReachedException,
    -14: CallbackDomainMismatchException,
    -15: TerminalSuspendedException,
    -16: TerminalLevelException,
    -17: BlueLevelLimitException,
    -18: ReferrerMismatchException,
    -19: TransactionBannedException,
    -30: FloatingWagesNotAllowedException,
    -31: NoBankAccountException,
    -32: WagesOverloadException,
    -33: InvalidWagesFloatingException,
    -34: WagesFixedOverloadException,
    -35: TooManyWagesPartsException,
    -36: MinimumWagesException,
    -37: InactiveIbanException,
    -38: IbanNotSetException,
    -39: WagesErrorException,
    -40: InvalidExpireInException,
    -41: MaxAmountExceededException,
    -50: AmountMismatchException,
    -51: PaymentFailedException,
    -52: UnexpectedErrorException,
    -53: WrongMerchantException,
    -54: InvalidAuthorityException,
    -55: ManualPaymentNotFoundException,
    -60: CannotReverseException,
    -61: ReverseNotAllowedException,
    -62: IpNotSetException,
    -63: ReverseTimeExpiredException,
    101: AlreadyVerifiedException,
    429: InvalidReferrerCodeException,
    430: InvalidDecodingException,
    431: ReferrerNotFoundException,
    432: TerminalBelongsToReferrerException,
    433: TerminalAlreadyHasReferrerException,
}
